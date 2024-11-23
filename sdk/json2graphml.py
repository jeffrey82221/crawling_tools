"""
TODO:

Script: 
    - Start Neo4j
        ```bash
        docker run -it --rm \
        --publish=7474:7474 --publish=7687:7687 \
        --env NEO4J_AUTH=none \
        --env NEO4J_PLUGINS='["apoc"]' \
        neo4j:5.25.1
        ```
TODO:
- [ ] Goal : 在 同一個 dictionary 裡面的 keys 要建立橫向連結
    - [ ] 可以讓 List of Diction 裡面的 values 彼此連結
    - [ ] 可以讓 最上層的 values 被綁在一起，類似root的概念
- [ ] 相同層次的資訊必續建立橫向關聯 
    - HOW?
        - [ ] Json裡面的 List 要改成 Dict，並且以 ListItem_0/1/... 為 key!
        - [ ] Cypher 後修：
            - [ ] Step1: Cypher 最後找到所有 ListItem0/1...的節點，
            - [ ] Step2: 用 Cypher 把其中相同 Key 的 Values 互相連結
            - [ ] Step3: 用 Cypher 移除 ListItem0/1/... ，然後把下面相同的key 合併到一起，往上面接
- [ ] 納入 root 節點
    - HOW?
        - [ ] 整個資料放到 root 底下： {"root": original_json)
        - [ ] Cypher 把 root 特別標上標籤 :ROOT
    
"""
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

def convert_list_2_dict(json_instance):
    if isinstance(json_instance, dict):
        results = dict()
        for key, value in json_instance.items():
            results[key] = convert_list_2_dict(value)
        return results
    elif isinstance(json_instance, list):
        results = dict()
        for i, item in enumerate(json_instance):
            results[i] = convert_list_2_dict(item)
        return results
    else:
        return json_instance

# Load YAML or JSON data from a file
data = data_loader.load_yaml_or_json('../examples/cnyes/funds/jsons/nav.json')
data = convert_list_2_dict(data)
print(data)
G = render(data)
G = rm_visual_info(G)
buff = io.StringIO()
nx.write_network_text(G, buff)
buff.seek(0)
print('Networkx Visualization:')
print(buff.read())
nx.write_graphml_xml(G, 'example.graphml')

