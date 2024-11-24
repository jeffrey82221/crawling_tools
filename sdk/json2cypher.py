"""
Convert Json into 
a graph in neo4j by generating a cypher 
to ingest the data

Developed by prompt: https://poe.com/s/iGsAR5d8qzsI6DATAqMd
"""

import json
import uuid
import tqdm
import threading
from neo4j import GraphDatabase
from neo4j.exceptions import CypherSyntaxError

def json_to_graph(json_data):
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
    def generate_id():
        """Generates a unique ID for each node."""
        return str(uuid.uuid4())

    def create_node(node_id, content, node_type):
        """Creates a node dictionary."""
        return {"id": node_id, "content": content, "type": node_type}

    def create_link(source_id, target_id, link_type):
        """Creates a link dictionary."""
        return {"id": generate_id(), "source": source_id, "target": target_id, "type": link_type}

    nodes = []
    links = []

    def process_element(element, parent_id=None, link_type=None):
        """
        Processes a JSON element recursively, creating nodes and links.

        Parameters:
            element: The current JSON element to process.
            parent_id: The ID of the parent node (if any).
            link_type: The link type connecting the parent to this element (if any).
        """
        if isinstance(element, (int, float, bool, str)) or element is None:
            # AtomicElement node
            content = str(element) if element is not None else "null"
            node_type = "Number" if isinstance(element, (int, float)) else \
                        "Boolean" if isinstance(element, bool) else \
                        "String"
            node_id = generate_id()
            nodes.append(create_node(node_id, content, node_type))

            # Create a link to the parent node (if applicable)
            if parent_id and link_type:
                links.append(create_link(parent_id, node_id, link_type))

            return node_id

        elif isinstance(element, list):
            # List node
            node_id = generate_id()
            nodes.append(create_node(node_id, "List", "List"))

            # Create a link to the parent node (if applicable)
            if parent_id and link_type:
                links.append(create_link(parent_id, node_id, link_type))

            # Process each element in the list
            item_ids = []
            for item in element:
                item_id = process_element(item, parent_id=node_id, link_type="has_element")
                item_ids.append(item_id)

            # Connect List element one after another
            for i, item_id in enumerate(item_ids):
                if i > 0:
                    links.append(create_link(item_ids[i-1], item_id, 'is_in_front_of'))
            return node_id

        elif isinstance(element, dict):
            # Record node
            node_id = generate_id()
            nodes.append(create_node(node_id, "Record", "Record"))

            # Create a link to the parent node (if applicable)
            if parent_id and link_type:
                links.append(create_link(parent_id, node_id, link_type))

            # Process each key-value pair in the dictionary
            for key, value in element.items():
                # Create a Field node for the key
                field_id = generate_id()
                field_node = create_node(field_id, key, "Field")
                nodes.append(field_node)

                # Link the Record to the Field
                links.append(create_link(node_id, field_id, "has_field"))

                # Process the value and link the Field to the value
                value_id = process_element(value)
                links.append(create_link(field_id, value_id, "has_value"))

            return node_id

        else:
            raise ValueError(f"Unsupported JSON element type: {type(element)}")

    # Start processing the JSON data
    process_element(json_data)

    return nodes, links

def node_to_cypher(node, ignore_text_content=False) -> str:
    """
    Parameters:
        - node is a dictionary with keys 'id', 'content', and 'type'.
    """
    if ignore_text_content:
        content = '[CANNOT ATTACH TO CYPHER]'
        node_query = f"CREATE (:{node['type']} {{id: '{node['id']}', content: '{content}', type: '{node['type']}'}});"
    else:
        node_query = f"CREATE (:{node['type']} {{id: '{node['id']}', content: '{node['content']}', type: '{node['type']}'}});"
    return  node_query

def link_to_cypher(link) -> str:
    """
    Parameters:
        - link is a dictionary with keys 'id', 'source', 'target', and 'type'.
    """
    link_query = (
            f"MATCH (a {{id: '{link['source']}'}}), (b {{id: '{link['target']}'}}) "
            f"CREATE (a)-[:{link['type']} {{id: '{link['id']}'}}]->(b);"
        )
    return link_query

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

node_types = ['Field', 'List', 'Number', 'Record', 'String']
link_types = ['has_element', 'has_field', 'has_value', 'is_in_front_of']


def get_node_constraint_cyphers():
    cyphers = []
    for node_type in node_types:
        cyphers.append()
    return cyphers

def get_link_constraint_cyphers():
    cyphers = []
    for link_type in link_types:
        cyphers.append(f'CREATE CONSTRAINT unique_id_for_{link_type.lower()} FOR ()-[n:{link_type})-() REQUIRE n.id IS UNIQUE;')
    return cyphers
    


# Example usage
if __name__ == "__main__":
    # sample_json = json.load(open('../examples/cnyes/funds/jsons/RegionCrawler.json', 'r'))
    sample_json = json.load(open('pypi.json', 'r'))
    nodes, links = json_to_graph(sample_json)
    conn = Neo4jIngestor("neo4j://localhost:7687", "neo4j", "neo4j")
    try:
        conn.ingest(node_types, 
                    lambda node_type: f'CREATE CONSTRAINT unique_id_for_{node_type.lower()} FOR (n:{node_type}) REQUIRE n.id IS UNIQUE;', 
                    desc='node_constraint'
        )
        conn.ingest(link_types, 
                    lambda link_type: f'CREATE CONSTRAINT unique_id_for_{link_type.lower()} FOR ()-[n:{link_type}]-() REQUIRE n.id IS UNIQUE;', 
                    desc='link_constraint'
        )
        conn.ingest(nodes, node_to_cypher, desc='nodes', n_thread=16)
        conn.ingest(links, link_to_cypher, desc='links', n_thread=16)
    finally:
        conn.close()