MATCH (n:JSON) DETACH DELETE n;
CALL apoc.import.graphml(
  "https://raw.githubusercontent.com/jeffrey82221/crawling_tools/refs/heads/main/sdk/example.graphml", 
  {
     defaultRelationshipType: 'HAS_CHILD',
     storeNodeIds: True
  }
 );
MATCH (n) WHERE n.labels = ':JSON' SET n:JSON;
MATCH (n:JSON) SET n.labels = NULL;