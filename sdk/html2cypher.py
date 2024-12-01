"""
TODO:
- [ ] Identify repeating part of the HTML
    - [ ] Add beautifulsoup element object into `nodes` dictionary. 
    - [ ] Avoid adding beautifulsoup element object into cypher. 
    - [ ] Using neo4j to find the id of the repeating component.
    - [ ] Store the repeating component part of HTML for further processing.
    - [ ] Develop algorithm to find difference between similar element in the list
        See: diff_extractor.py
"""
from bs4 import BeautifulSoup
import uuid
import requests
from neo4j import GraphDatabase
from neo4j.exceptions import CypherSyntaxError
import tqdm
import threading


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

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Process each top-level element
    element_ids = []
    for element in soup.contents:
        element_id = process_element(element)
        if element_id is not None:
            element_ids.append(element_id)
    # Connect element one after another
    connect_sequential_elements(element_ids)

    return nodes, links


def node_to_cypher(node, ignore_text_content=False) -> str:
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


def link_to_cypher(link) -> str:
    query = f"MATCH (a {{id: '{link['source']}'}}), (b {{id: '{link['target']}'}}) CREATE (a)-[:{link['type'].upper()}]->(b)"
    return query


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
        
# Example Usage
if __name__ == "__main__":
    # Example HTML content
    res = requests.get('https://thaubing.gcaa.org.tw/facility/D32097008938')
    print(res.status_code)
    html_content = res.content.decode('utf-8')
    with open('example.html', 'w') as f:
        f.write(html_content)
    nodes, links = html_to_graph(html_content)
    conn = Neo4jIngestor("neo4j://localhost:7687", "neo4j", "neo4j")
    try:
        conn.ingest(nodes, node_to_cypher, desc='nodes', n_thread=8)
        conn.ingest(links, link_to_cypher, desc='links', n_thread=8)
    finally:
        conn.close()