from yaml2dot import data_loader
from yaml2dot.renderer import render
import networkx as nx
import io

def rm_visual_info(G: nx.Graph) -> nx.Graph:
    """
    移除 dot 檔中視覺化的資訊
    """
    node_link_data = nx.node_link_data(G, edges='edges')
    node_link_data['graph'] = {}
    for node in node_link_data['nodes']:
        for key in ['fontname', 'fontsize', 'margin', 'fillcolor', 'penwidth', 'style', 'shape']:
            node['labels'] = ':JSON'
            del node[key]
    for link in node_link_data['edges']:
        for key in ['arrowhead', 'penwidth']:
            del link[key]
    return nx.node_link_graph(node_link_data, edges="edges")

# Load YAML or JSON data from a file
data = data_loader.load_yaml_or_json('../examples/cnyes/funds/jsons/HoldingsCrawler.json')
G = render(data)
G = rm_visual_info(G)
buff = io.StringIO()
nx.write_network_text(G, buff)
buff.seek(0)
print('Networkx Visualization:')
print(buff.read())
nx.write_graphml_xml(G, 'example.graphml')

