# Objective:

Return all List nodes where every Record element connected to the list has the exact same set of Field nodes, both in terms of the fields present and their names.

# Graph Structure:

Nodes: AtomicElement, List, Record, Field
Relationships:
(List) -[:has_element]-> (AtomicElement | List | Record)
(Record) -[:has_field]-> (Field)
(Field) -[:has_value]-> (AtomicElement | List | Record)
(List Element) -[:is_in_front_of]-> (List Element)

# Requirements:

Identify List nodes that contain Record nodes as elements.
Ensure that all Record nodes within the same List have identical Field nodes, where "identical" means having the same set of field names.
No Record should have extra fields beyond what is common to all records in that list.

# Expected Outcome:
Lists that satisfy the above conditions should be returned.

# Provided Cypher: 

```cypher
MATCH (l:List)-[:has_element]->(r:Record)-[:has_field]->(f:Field)
WITH l, collect(DISTINCT r) AS records, collect(DISTINCT f.content) AS fieldNames
WHERE ALL(r IN records WHERE 
    SIZE([(r)-[:has_field]->(f) | f]) = SIZE(fieldNames) AND
    ALL(f IN fieldNames WHERE 
        EXISTS((r)-[:has_field]->(:Field {content: f}))
    )
)
RETURN l
```