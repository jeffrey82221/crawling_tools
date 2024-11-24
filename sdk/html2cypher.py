from bs4 import BeautifulSoup
import uuid
import requests
from neo4j import GraphDatabase
from neo4j.exceptions import CypherSyntaxError
import tqdm

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
                    "name": attr_name,
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
        query = f"CREATE (n:Attribute {{id: '{node['id']}', name: '{node.get('name', '')}', value: {value_str}}})"

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


class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def execute_query(self, query):
        with self.driver.session() as session:
            session.write_transaction(self._execute_single_query, query)

    @staticmethod
    def _execute_single_query(tx, query):
        result = tx.run(query)
        return result.data()
    
# Example Usage
if __name__ == "__main__":
    # Example HTML content
    res = requests.get('https://thaubing.gcaa.org.tw/facility/D32097008938')
    print(res.status_code)
    html_content = res.content.decode('utf-8')
    with open('example.html', 'w') as f:
        f.write(html_content)
    nodes, links = html_to_graph(html_content)
    conn = Neo4jConnection("neo4j://localhost:7687", "neo4j", "neo4j")
    for node in tqdm.tqdm(nodes, desc='nodes'):
        query = node_to_cypher(node)
        try:
            conn.execute_query(query)
        except CypherSyntaxError:
            query = node_to_cypher(node, ignore_text_content=True)
            conn.execute_query(query)
        finally:
            conn.close()

    for link in tqdm.tqdm(links, desc='links'):
        query = link_to_cypher(link)
        try:
            conn.execute_query(query)
        finally:
            conn.close()
    