# Goal:

convert all semi-structured format (e.g., json) 
into graph 

# Steps: 

# Step 1: define the nodes and links of the format



# Step 2: ask POE to generate a function to develop a function for generating the nodes and links: 

Give me a python function that convert any json into a graph
with the following node types: 
AtomicElement:
- Number
- String
- Boolean
Object:
- List
- Record
Field
, and follwing link types:
(List) -> has_element -> (AtomicElement/List/Records)
(Record) -> has_field -> (Field)
(Field) -> has_value -> (AtomicElement/List/Records)



The function should return nodes as list of dictionary and links as 
list of dictionary. 
The nodes should have id, content, type as the field of dictionary, so as for the links.

