Give me a python function that convert any HTML into a graph
with the following Node Types and Link Types. 

Node Types for HTML:
Element:
Represents an HTML tag (e.g., <div>, <p>, <img>).
Properties:
tag: The name of the tag (e.g., div, p).
id, class: Optional attributes that can be used for identification.
type: Always Element.
Attribute:
Represents attributes of an HTML tag (e.g., href, src, alt).
Properties:
name: The name of the attribute (e.g., href, src).
value: The value of the attribute (e.g., https://example.com).
type: Always Attribute.
Text:
Represents the text content inside an HTML element.
Properties:
content: The actual text.
type: Always Text.

Link Types for HTML:
contains:
Used to link an Element to its child Element, Text, or Attribute.
Represents the parent-child relationship in the HTML document structure.
has_attribute:
Used to link an Element to its Attribute.
Represents the relationship between an HTML tag and its attributes.

The function should return nodes as list of dictionary and links as list of dictionary. 

Note that the nodes should have unique id as node id, so  for the links.

