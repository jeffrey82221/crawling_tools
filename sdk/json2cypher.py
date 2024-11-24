"""
Convert Json into 
a graph in neo4j by generating a cypher 
to ingest the data

Developed by prompt: https://poe.com/s/iGsAR5d8qzsI6DATAqMd
"""

import json
import uuid
import tqdm
from neo4j import GraphDatabase

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

def convert_to_cyphers(nodes, links):
    """
    Converts nodes and links into Cypher queries for Neo4j.

    Parameters:
        nodes (list): A list of nodes, where each node is a dictionary with keys 'id', 'content', and 'type'.
        links (list): A list of links, where each link is a dictionary with keys 'id', 'source', 'target', and 'type'.

    Returns:
        str: A Cypher query string to create the nodes and links in Neo4j.
    """
    cypher_queries = []

    # Create nodes
    for node in nodes:
        node_query = f"CREATE (:{node['type']} {{id: '{node['id']}', content: '{node['content']}', type: '{node['type']}'}});"
        cypher_queries.append(node_query)

    # Create links
    for link in links:
        link_query = (
            f"MATCH (a {{id: '{link['source']}'}}), (b {{id: '{link['target']}'}}) "
            f"CREATE (a)-[:{link['type']} {{id: '{link['id']}'}}]->(b);"
        )
        cypher_queries.append(link_query)

    # Combine all queries into one script
    return cypher_queries

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
    
# Example usage
if __name__ == "__main__":
    sample_json = json.load(open('../examples/cnyes/funds/jsons/RegionCrawler.json', 'r'))
    nodes, links = json_to_graph(sample_json)
    conn = Neo4jConnection("neo4j://localhost:7687", "neo4j", "neo4j")
    cyphers = convert_to_cyphers(nodes, links)
    for query in tqdm.tqdm(cyphers, desc='cyphers'):
        try:
            conn.execute_query(query)
        finally:
            conn.close()
    