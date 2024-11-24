MATCH (d)-[:has_value]->(l:List)-[:has_element]->(r:Record)-[:has_field]->(f:Field)
WITH d, l, collect(DISTINCT r) AS records, collect(DISTINCT f.content) AS fieldNames
WHERE ALL(r IN records WHERE 
    SIZE([(r)-[:has_field]->(f) | f]) = SIZE(fieldNames) AND
    ALL(f IN fieldNames WHERE 
        EXISTS((r)-[:has_field]->(:Field {content: f}))
    )
)
RETURN d, l