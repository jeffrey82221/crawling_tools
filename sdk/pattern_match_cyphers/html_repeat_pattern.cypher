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
WITH parent
MATCH path=(root:Element)-[:CONTAINS*]->(parent:Element)
SET parent:Highlighted
RETURN path