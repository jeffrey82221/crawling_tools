from yaml2dot import data_loader,converter

# Load YAML or JSON data from a file
data = data_loader.load_yaml_or_json('../examples/cnyes/funds/jsons/HoldingsCrawler.json')
# or input a python dict directly
# data = {"example":"example"}

# Convert the data to DOT format (default)
dot_output = converter.convert_yaml_or_json_to_format(data)
# Print or save the outputs as needed
with open('example.dot', 'w') as f:
    f.write(dot_output)