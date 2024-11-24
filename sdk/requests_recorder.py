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
from urllib.parse import urlparse


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
        res = requests.request(
            url=url,
            params=record['request']['params'] if record['request']['method'] == 'POST' else None,
            method=method,
            headers=record['request']['headers']
        )
        assert res.status_code == 200, f'{method} {url} {res.status_code}'
        records[i]['response']['status_code_v2'] = res.status_code
        try:
            data = res.json()
            data_type = 'json'
        except JSONDecodeError as e:
            if 'html' in res.text:
                data = BeautifulSoup(res.text, "html.parser")
                data_type = 'html'
            else:
                data = res.text
                data_type = 'text'
        except BaseException as e:
            data = None
            data_type = 'unknown'
            raise e
        print(f"ENDPOINT No.{i} {data_type} {res.status_code} {method} from {url}")
        records[i]['response']['data'] = data
        records[i]['response']['data_type'] = data_type
    return records


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
                'method': record['request']['method'],
                'data_type': record['response']['data_type'],
                'type': 'Endpoint'
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
                    session.run(query)
                except CypherSyntaxError:
                    query = callback_func(item, ignore_text_content=True)
                    session.run(query)

node_types = ['Domain', 'Endpoint']

if __name__ == '__main__':
    url = "https://fund.cnyes.com/detail/%E6%99%AF%E9%A0%86%E5%85%A8%E6%AD%90%E6%B4%B2%E4%BC%81%E6%A5%AD%E5%9F%BA%E9%87%91A%E8%82%A1%20%E6%AD%90%E5%85%83/B16%2C009/"
    endpoint_nodes, domain_nodes, links = webpage_to_graph(url)
    conn = Neo4jIngestor("neo4j://localhost:7687", "neo4j", "neo4j")
    try:
        conn.ingest(node_types, 
                    lambda node_type: f'CREATE CONSTRAINT IF NOT EXISTS unique_id_for_{node_type.lower()} FOR (n:{node_type}) REQUIRE n.id IS UNIQUE;', 
                    desc='node_constraint'
        )
        conn.ingest(endpoint_nodes, 
                    lambda x: f'CREATE (n:{x["type"]}:{x["method"]}:{x["data_type"]} {{id: "{x["id"]}", path: "{x["path"]}"}});', 
                    desc='endpoints', n_thread=2)
        conn.ingest(domain_nodes, 
                    lambda x: f'MERGE (n:{x["type"]} {{id: "{x["id"]}"}});', 
                    desc='endpoints', n_thread=2)
        conn.ingest(links, 
                    lambda x: f'MATCH (f:Domain {{id: "{x["source"]}"}}) MATCH (t:Endpoint {{id: "{x["target"]}"}}) CREATE (f)-[:has_endpoint]->(t);'
                    , desc='links', n_thread=2)
    finally:
        conn.close()

    