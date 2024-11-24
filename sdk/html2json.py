from bs4 import BeautifulSoup
import html_to_json
import pprint
import json
with open('example.html', 'r') as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
tbody = soup.find_all('table')[0].find_all('tbody')[0]
results = []
for i, child in enumerate(tbody.children):
    child_json = html_to_json.convert(str(child))
    print('No.', i, '============================')
    pprint.pprint(child_json)
    print('============================')
    results.append(child_json)
with open('diff_sample.json', 'w') as f:
    f.write(json.dumps(results, ensure_ascii=False))

    

    