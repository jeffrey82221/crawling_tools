from bs4 import BeautifulSoup

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
    node_id_counter = 1  # Counter for generating unique node IDs
    link_id_counter = 1  # Counter for generating unique link IDs

    def get_unique_node_id():
        """Generates a unique node ID."""
        nonlocal node_id_counter
        unique_id = node_id_counter
        node_id_counter += 1
        return str(unique_id)

    def get_unique_link_id():
        """Generates a unique link ID."""
        nonlocal link_id_counter
        unique_id = link_id_counter
        link_id_counter += 1
        return str(unique_id)

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
            for child in element.children:
                process_element(child, element_id)

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

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Process each top-level element
    for element in soup.contents:
        process_element(element)

    return nodes, links


def graph_to_cypher(nodes, links):
    """
    Converts graph nodes and links into Cypher queries for Neo4j.
    Properties are flattened so that each property becomes a direct property of the node.

    Parameters:
        nodes (list): A list of dictionaries representing nodes.
        links (list): A list of dictionaries representing links.

    Returns:
        str: A string containing the Cypher queries.
    """
    cypher_queries = []

    # Create nodes
    for node in nodes:
        # Start with the mandatory properties
        if node["type"] == "Element":
            # Flatten properties for Element nodes
            properties = node.get("properties", {})
            flattened_properties = ", ".join(
                f'{key.replace("-", "_")}: "{value}"' for key, value in properties.items()
            )
            query = f"CREATE (n:Element {{id: '{node['id']}', tag: '{node.get('tag', '')}'"
            if flattened_properties:
                query += f", {flattened_properties}"
            query += "})"

        elif node["type"] == "Attribute":
            value = node.get('value', '')
            value_str = f'"{value}"'
            query = f"CREATE (n:Attribute {{id: '{node['id']}', name: '{node.get('name', '')}', value: {value_str}}})"

        elif node["type"] == "Text":
            query = f"CREATE (n:Text {{id: '{node['id']}', content: '{node.get('content', '')}'}})"

        else:
            continue  # Skip unknown node types

        cypher_queries.append(query)

    # Create relationships
    for link in links:
        query = f"MATCH (a {{id: '{link['source']}'}}), (b {{id: '{link['target']}'}}) CREATE (a)-[:{link['type'].upper()}]->(b)"
        cypher_queries.append(query)

    # Combine all queries into a single string
    return ";\n".join(cypher_queries)

# Example Usage
if __name__ == "__main__":
    # Example HTML content
    html_content = """
    <html>
        <head>
            <title>Example Domain</title>
        </head>
        <body>
            <h1>Example Domain</h1>
            <p>This domain is for use in illustrative examples in documents.</p>
            <p>More information...</p>
        </body>
    </html>
    """
    nodes, links = html_to_graph(html_content)
    cypher = graph_to_cypher(nodes, links)
    with open('html.cypher', 'w') as f:
        f.write(cypher)