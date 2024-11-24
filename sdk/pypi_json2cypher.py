import json
import requests
url = "https://pypi.org/pypi/jskiner/json"
data = requests.get(url).json()
with open('pypi.json', 'w') as f:
    f.write(json.dumps(data))