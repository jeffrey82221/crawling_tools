# Objective:

Return repeated component within a webpage by extracting 
the repeated nodes with same neighbors in graph representing the html.

# Graph Structure:

a graph
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
is_in_front_of:
Used to link an Element to its next Element for Elements in a sequence.
The function should return nodes as list of dictionary and links as list of dictionary. 


# Requirements:

Identify Element with previous and next Element (link to the element by `is_in_front_of`) with 
children (linked by `contains`) having the same attributes (linked by `has_attribute`).

# Expected Outcome:
Lists that satisfy the above conditions should be returned.

# Provided Cypher: 

## Try 1:

```cypher
MATCH (e1:Element)-[:CONTAINS]->(child1),
      (e2:Element)-[:CONTAINS]->(child2),
      (e1)-[:IS_IN_FRONT_OF]->(e2),
      (child1)-[:HAS_ATTRIBUTE]->(attr1),
      (child2)-[:HAS_ATTRIBUTE]->(attr2)
WHERE e1.tag = e2.tag AND
      child1.tag = child2.tag AND
      attr1.name = attr2.name
RETURN e1, e2, child1, child2, attr1, attr2
```

### my comment 
Good, now you found element with similar nearby elements. However, the cypher only consider the directly connected elements. Extend the cypher such that it identify at least three consecutive elements being similar.

## Try 2: 

```cypher
MATCH 
  (e1:Element)-[:CONTAINS]->(child1),
  (e2:Element)-[:CONTAINS]->(child2),
  (e3:Element)-[:CONTAINS]->(child3),
  (e1)-[:IS_IN_FRONT_OF]->(e2),
  (e2)-[:IS_IN_FRONT_OF]->(e3),
  (child1)-[:HAS_ATTRIBUTE]->(attr1),
  (child2)-[:HAS_ATTRIBUTE]->(attr2),
  (child3)-[:HAS_ATTRIBUTE]->(attr3)
WHERE 
  e1.tag = e2.tag AND e2.tag = e3.tag AND
  child1.tag = child2.tag AND child2.tag = child3.tag AND
  attr1.name = attr2.name AND attr2.name = attr3.name
RETURN 
  e1, e2, e3, child1, child2, child3, attr1, attr2, attr3
```

### my comment:

Good, now you have identified pattern in a webpage. However, for easier usage, I want you to return the Element containing the pattern rather than the elements constitute the pattern. That is, you should return element CONTAINS e1, e2, e3 rather than e1, e2, e3


## Try 3:

```cypher
MATCH 
  (e1:Element)-[:CONTAINS]->(child1),
  (e2:Element)-[:CONTAINS]->(child2),
  (e3:Element)-[:CONTAINS]->(child3),
  (e1)-[:IS_IN_FRONT_OF]->(e2),
  (e2)-[:IS_IN_FRONT_OF]->(e3),
  (child1)-[:HAS_ATTRIBUTE]->(attr1),
  (child2)-[:HAS_ATTRIBUTE]->(attr2),
  (child3)-[:HAS_ATTRIBUTE]->(attr3),
  (parent:Element)-[:CONTAINS]->(e1),
  (parent:Element)-[:CONTAINS]->(e2),
  (parent:Element)-[:CONTAINS]->(e3)
WHERE 
  e1.tag = e2.tag AND e2.tag = e3.tag AND
  child1.tag = child2.tag AND child2.tag = child3.tag AND
  attr1.name = attr2.name AND attr2.name = attr3.name
RETURN 
  parent
```

### my comment

Good, now you have identify the component contains the repeating pattern (aka `parent`). 
Show me all the ancenstors of `parent` such that the path to the component can be 
easily trace upon. 

```cypher
MATCH 
  (e1:Element)-[:CONTAINS]->(child1),
  (e2:Element)-[:CONTAINS]->(child2),
  (e3:Element)-[:CONTAINS]->(child3),
  (e1)-[:IS_IN_FRONT_OF]->(e2),
  (e2)-[:IS_IN_FRONT_OF]->(e3),
  (child1)-[:HAS_ATTRIBUTE]->(attr1),
  (child2)-[:HAS_ATTRIBUTE]->(attr2),
  (child3)-[:HAS_ATTRIBUTE]->(attr3),
  (parent:Element)-[:CONTAINS]->(e1),
  (parent:Element)-[:CONTAINS]->(e2),
  (parent:Element)-[:CONTAINS]->(e3),
  path=(root:Element)-[:CONTAINS*]->(parent:Element)
WHERE 
  e1.tag = e2.tag AND e2.tag = e3.tag AND
  child1.tag = child2.tag AND child2.tag = child3.tag AND
  attr1.name = attr2.name AND attr2.name = attr3.name
RETURN 
  path
```


```
MATCH 
  path=(root:Element)-[:CONTAINS*]->(parent:Element)-[:contains]->(e1:Element)-[:contains]->(child1),
  (e1)-[:is_in_front_of]->(e2:Element)-[:contains]->(child2),
  (e2)-[:is_in_front_of]->(e3:Element)-[:contains]->(child3),
  (child1)-[:has_attribute]->(attr1),
  (child2)-[:has_attribute]->(attr2),
  (child3)-[:has_attribute]->(attr3)
WHERE 
  e1.tag = e2.tag AND e2.tag = e3.tag AND
  child1.tag = child2.tag AND child2.tag = child3.tag AND
  attr1.name = attr2.name AND attr2.name = attr3.name AND
  attr1.value = attr2.value AND attr2.value = attr3.value
RETURN 
  path
  ```