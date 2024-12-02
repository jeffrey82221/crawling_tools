"""
應該要有一個關聯排序功能：

把endpoint與網頁輸入的網址做比對
從最相關排到最不相關
"""
from typing import List, Dict, Tuple
from urllib.parse import unquote
from requests.exceptions import JSONDecodeError
from bs4 import BeautifulSoup
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import threading 
from neo4j import GraphDatabase
from neo4j.exceptions import CypherSyntaxError
import tqdm
import uuid
import os
from urllib.parse import urlparse
import ssl
from html.parser import HTMLParser


class ConfirmHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.start_tags = list()
        self.end_tags = list()
        self.attributes = list()
    
    def is_text_html(self):
        return len(self.start_tags) == len(self.end_tags)

    def handle_starttag(self, tag, attrs):
        self.start_tags.append(tag)
        self.attributes.append(attrs)

    def handle_endtag(self, tag):
        self.end_tags.append(tag)

    def handle_data(self, data):
        pass

def has_head_n_body(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check for <head> and <body> tags
    has_head = soup.head is not None
    has_body = soup.body is not None

    return has_head and has_body


def get_webpage_records(url: str) -> List[Dict]:
    """
    Returns:
        request recorded data
    """
    driver = webdriver.Chrome(
        service=Service(executable_path=ChromeDriverManager().install()),
    )
    results = []
    try:
        driver.get(url)
        for i, request in enumerate(driver.requests):
            if request.response:
                request.response.headers
                if 'google' not in request.url and 'facebook' not in request.url and request.response.status_code == 200:
                    print(f'REQUEST No.{i}', request.response.status_code, request.method, request.response.headers['Content-Type'])
                    # body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')).decode('utf-8')
                    results.append(
                        {
                            'id': i,
                            'request': {
                                'headers': dict(request.headers),
                                'url': unquote(request.url),
                                'method': request.method,
                                'params': request.params
                            },
                            'response': {
                                'status_code': request.response.status_code,
                                'headers': dict(request.response.headers),
                            }
                        }
                    )
        return results
    finally:
        driver.close()

def collect_response_body(records: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Access the endpoint againt to get the response body
    """
    for i, record in enumerate(records):
        url = record['request']['url']
        method = record['request']['method']
        try:
            res = requests.request(
                url=url,
                params=record['request']['params'] if record['request']['method'] == 'POST' else None,
                method=method,
                headers=record['request']['headers'],
                timeout=10
            )
            records[i]['response']['status_code_v2'] = res.status_code
            try:
                data = res.json()
                data_type = 'json'
            except JSONDecodeError as e:
                data = res.content
                text = res.text
                parser = ConfirmHTMLParser()
                parser.feed(text)
                if parser.is_text_html() and has_head_n_body(text):
                    data_type = 'html'
                else:
                    data_type = None
            except BaseException as e:
                data = None
                data_type = None
                raise e
            print(f"ENDPOINT No.{i} {data_type} {res.status_code} {method} from {url}")
        except (ssl.SSLCertVerificationError, requests.exceptions.SSLError, requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
            data = str(e)
            data_type = None
            print(f"ENDPOINT No.{i} {data_type} ssl error {method} from {url}")
        finally:
            records[i]['response']['data'] = data
            records[i]['response']['data_type'] = data_type
    return records


def html_to_graph(html_content):
    """
    Converts an HTML document into a graph representation using the specified Node Types and Link Types.

    Parameters:
        html_content (str): The HTML string to be converted.

    Returns:
        tuple: A tuple containing two lists:
            - nodes: A list of dictionaries representing nodes.
            - links: A list of dictionaries representing links.
    """
    nodes = []
    links = []

    def get_unique_node_id():
        """Generates a unique node ID."""
        return str(uuid.uuid4())

    def get_unique_link_id():
        """Generates a unique link ID."""
        return str(uuid.uuid4())
    
    def connect_sequential_elements(element_ids):
        """connect a sequence"""
        nonlocal links
        for i, element_id in enumerate(element_ids):
            assert element_id is not None
            if i > 0:
                links.append({
                    "id": get_unique_link_id(),
                    "source": element_ids[i-1],
                    "target": element_id,
                    "type": "is_in_front_of"
                })

    def process_element(element, parent_id=None):
        """Recursively processes an HTML element and its children."""
        nonlocal nodes, links

        if element.name:  # If it's an HTML tag
            # Create a node for the element
            element_id = get_unique_node_id()
            nodes.append({
                "id": element_id,
                "tag": element.name,
                "type": "Element",
                "properties": {attr: element[attr] for attr in element.attrs}  # Add all attributes as properties
            })

            # If the element has a parent, create a "contains" link
            if parent_id:
                links.append({
                    "id": get_unique_link_id(),
                    "source": parent_id,
                    "target": element_id,
                    "type": "contains"
                })

            # Process attributes as separate nodes
            for attr_name, attr_value in element.attrs.items():
                attr_id = get_unique_node_id()
                nodes.append({
                    "id": attr_id,
                    "name": attr_name.strip().replace('-', '_'),
                    "value": attr_value,
                    "type": "Attribute"
                })
                # Link the element to its attribute
                links.append({
                    "id": get_unique_link_id(),
                    "source": element_id,
                    "target": attr_id,
                    "type": "has_attribute"
                })

            # Recursively process child elements
            child_ids = []
            for child in element.children:
                child_id = process_element(child, element_id)
                if child_id is not None:
                    child_ids.append(child_id)
            connect_sequential_elements(child_ids)
            return element_id

        elif element.string and element.string.strip():  # If it's text content
            # Create a node for the text
            text_id = get_unique_node_id()
            nodes.append({
                "id": text_id,
                "content": element.string.strip(),
                "type": "Text"
            })

            # Link the text node to its parent
            if parent_id:
                links.append({
                    "id": get_unique_link_id(),
                    "source": parent_id,
                    "target": text_id,
                    "type": "contains"
                })
            return text_id
    soup = BeautifulSoup(html_content, "html.parser")
    # Process each top-level element
    element_ids = []
    for element in soup.contents:
        element_id = process_element(element)
        if element_id is not None:
            element_ids.append(element_id)
    # Connect element one after another
    connect_sequential_elements(element_ids)
    return element_ids, nodes, links


def html_node_to_cypher(node, ignore_text_content=False) -> str:
    """
    Converts graph nodes into Cypher queries for Neo4j.

    Parameters:
        nodes (list): A list of dictionaries representing nodes.

    Returns:
        str: A string containing the Cypher queries.
    """
    if node["type"] == "Element":
        # Flatten properties for Element nodes
        tag = node['tag']
        assert isinstance(tag, str)
        assert tag != ''
        query = f"CREATE (n:Element:{tag.upper()} {{id: '{node['id']}', tag: '{tag}'"
        query += '}'
        query += ")"

    elif node["type"] == "Attribute":
        value = node.get('value', '')
        value_str = f'"{value}"'
        query = f"CREATE (n:Attribute:{node.get('name', '')} {{id: '{node['id']}', value: {value_str}}})"

    elif node["type"] == "Text":
        if ignore_text_content:
            node_content = '[CANNOT ATTACH TO CYPHER]'
        else:
            node_content = node.get('content', '')
            node_content = node_content.replace('\n', '\\n').replace('"', "'")
        id = node['id']
        query = f'CREATE (n:Text {{id: "{id}", content: "{node_content}"}})'
    else:
        raise ValueError('node is not Text/Attribute/Element')
    return query


def html_link_to_cypher(link) -> str:
    query = f"MATCH (a {{id: '{link['source']}'}}), (b {{id: '{link['target']}'}}) CREATE (a)-[:{link['type'].upper()}]->(b)"
    return query

def webpage_to_graph(url):
    """
    Converts a JSON object into a graph representation with specific node and link types.

    Parameters:
        json_data (dict | list | str | int | float | bool | None): The JSON data to convert.

    Returns:
        tuple: A tuple containing two lists:
            - nodes: A list of dictionaries representing the nodes.
            - links: A list of dictionaries representing the links.

    NOTE: Develop Prompt: https://poe.com/s/cUix9NxAto7NEDvaPaYe
    """
    endpoint_nodes = []
    domain_nodes = []
    links = []

    records = get_webpage_records(url)
    collect_response_body(records)
    for record in records:
        endpoint_id = str(uuid.uuid4())
        url = record['request']['url']
        endpoint_nodes.append(
            {   
                'id': endpoint_id,
                'path': urlparse(url).path,
                'url': url,
                'extension': os.path.splitext(urlparse(url).path)[-1],
                'method': record['request']['method'],
                'data_type': record['response']['data_type'],
                'type': 'Endpoint',
                'data': record['response']['data']
            }
        )
        domain = urlparse(url).netloc
        domain_nodes.append(
            {
                'id': domain,
                'type': 'Domain',
            }
        )
        links.append(
            {
                'id': str(uuid.uuid4()),
                'source': domain,
                'target': endpoint_id,
                'type': 'has_endpoint'
            }
        )
    return endpoint_nodes, domain_nodes, links


def split_list_into_n_parts(lst, n):
    """
    Splits a list into n sublists as evenly as possible.
    
    Args:
    lst (list): The list to be split.
    n (int): The number of sublists to create.
    
    Returns:
    list of lists: A list containing n sublists.
    """
    # If n is larger than the list length, we can only return actual list elements
    if n > len(lst):
        return [lst[i:i + 1] for i in range(len(lst))] + [[] for _ in range(n - len(lst))]

    # Calculate the size of each part: the minimum size of sublists
    part_size, remainder = divmod(len(lst), n)

    # Create the sublists
    sublists = []
    start = 0
    for i in range(n):
        # Add an extra element to some sublists to distribute the remainder
        end = start + part_size + (1 if i < remainder else 0)
        sublists.append(lst[start:end])
        start = end

    return sublists

class Neo4jIngestor:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def ingest(self, items, callback_func, desc='', n_thread=1):
        if n_thread == 1:
            args = self.driver, items, callback_func, desc
            t1 = threading.Thread(target=Neo4jIngestor._ingest_single_thread, args=args)
            t1.setDaemon(True)
            t1.start()
            t1.join()
        else:
            threads = []
            for i, items_part in enumerate(split_list_into_n_parts(items, n_thread)):
                args = self.driver, items_part, callback_func, desc + '.' + str(i)
                t1 = threading.Thread(target=Neo4jIngestor._ingest_single_thread, args=args)
                t1.setDaemon(True)
                threads.append(t1)
                t1.start()
            for t1 in threads:
                t1.join()
        
    def _ingest_single_thread(*args):
        driver, items, callback_func, desc = args
        with driver.session(database="neo4j") as session:
            for item in tqdm.tqdm(items, desc=desc):
                try:
                    query = callback_func(item)
                    if len(query.strip()) > 0:
                        session.run(query)
                except CypherSyntaxError:
                    query = callback_func(item, ignore_text_content=True)
                    if len(query.strip()) > 0:
                        session.run(query)


def endpoint2cypher(x):
    extension_label = ''
    if x['extension']:
        extension = x['extension'].replace('.', '')
        if len(extension) > 0 and extension[0].isalpha():
            extension_label = f":{extension.upper()}"
    cypher = f'''
        CREATE (n:{x["type"]}:{x["method"]}{extension_label} 
            {{
                id: "{x["id"]}", 
                path: "{x["path"]}", 
                url: "{x["url"]}", 
                extension: "{x["extension"]}"
            }}
        );
    '''
    print(cypher)
    return cypher

def extension2cypher(x):
    cypher = ''
    if x['extension']:
        extension = x['extension'].replace('.', '')
        if len(extension) > 0 and extension[0].isalpha():
            extension_label = extension.upper()
            cypher = f'''
            CREATE (r:Extension {{id: "{extension_label}"}});
            '''
    return cypher

def has_extension2cypher(x):
    cypher = ''
    if x['extension']:
        extension = x['extension'].replace('.', '')
        if len(extension) > 0 and extension[0].isalpha():
            extension_label = extension.upper()
            cypher = f'''
            MATCH (f:Endpoint {{id: "{x["id"]}"}})
            MATCH (t:Extension {{id: "{extension_label}"}})
            CREATE (f)-[:has_extension]->(t);
            '''
    else:
        cypher = ''
    return cypher

def response_type2cypher(x):
    if x["data_type"]:
        data_type_label = x['data_type'].upper()
        cypher = f'''
        CREATE (r:ResponseType {{id: "{data_type_label}"}});
        '''
    else:
        cypher = ''
    return cypher

def has_response_type2cypher(x):
    if x["data_type"] and not x["data_type"].startswith('has'):
        data_type_label = x['data_type'].upper()
        cypher = f'''
        MATCH (f:Endpoint {{id: "{x["id"]}"}})
        MATCH (t:ResponseType {{id: "{data_type_label}"}})
        CREATE (f)-[:has_response]->(t);
        '''
    else:
        cypher = ''
    return cypher



node_types = ['Domain', 'Endpoint', 'ResponseType', 'Extension']

if __name__ == '__main__':
    n_thread = 16
    url = "https://www.cmoney.tw/finance/6916/f00036"
    endpoint_nodes, domain_nodes, domain_endpoint_links = webpage_to_graph(url)
    conn = Neo4jIngestor("neo4j://localhost:7687", "neo4j", "neo4j")
    try:
        conn.ingest(node_types, 
                    lambda node_type: f'CREATE CONSTRAINT unique_id_for_{node_type.lower()} IF NOT EXISTS FOR (n:{node_type}) REQUIRE n.id IS UNIQUE;', 
                    desc='node_constraint'
        )
        conn.ingest(endpoint_nodes, 
                    endpoint2cypher, 
                    desc='endpoints', n_thread=n_thread)
        conn.ingest(endpoint_nodes, 
                    response_type2cypher, 
                    desc='response_type', n_thread=n_thread)
        conn.ingest(endpoint_nodes, 
                    extension2cypher, 
                    desc='extension', n_thread=n_thread)
        conn.ingest(endpoint_nodes, 
                    has_extension2cypher, 
                    desc='has_extension', n_thread=n_thread)
        conn.ingest(endpoint_nodes, 
                    has_response_type2cypher, 
                    desc='has_response_type', n_thread=n_thread)
        conn.ingest(domain_nodes, 
                    lambda x: f'MERGE (n:{x["type"]} {{id: "{x["id"]}"}});', 
                    desc='domain', n_thread=n_thread)
        conn.ingest(domain_endpoint_links, 
                    lambda x: f'MATCH (f:Domain {{id: "{x["source"]}"}}) MATCH (t:Endpoint {{id: "{x["target"]}"}}) CREATE (f)-[:has_endpoint]->(t);'
                    , desc='domain_endpoint_links', n_thread=n_thread)
        html_endpoint_links = []
        for endpoint_node in endpoint_nodes:
            if endpoint_node['data_type'] == 'html':
                top_ids, html_nodes, html_links = html_to_graph(endpoint_node['data'])
                print(f'#html node: {len(html_nodes)} & #html link: {len(html_links)}')
                conn.ingest(html_nodes, html_node_to_cypher, desc='nodes', n_thread=n_thread)
                conn.ingest(html_links, html_link_to_cypher, desc='links', n_thread=n_thread)
                for top_id in top_ids:
                    html_endpoint_links.append(
                        {
                            'source': endpoint_node['id'],
                            'target': top_id
                        }
                    )
        conn.ingest(html_endpoint_links, 
            lambda x: f'MATCH (f:Endpoint {{id: "{x["source"]}"}}) MATCH (t {{id: "{x["target"]}"}}) CREATE (f)-[:has_html]->(t);'
            , desc='has_html_link', n_thread=n_thread)
    finally:
        conn.close()