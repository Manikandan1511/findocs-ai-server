from neo4j import GraphDatabase

# Use your connected database URI
NEO4J_URI = "neo4j+ssc://fdc02495.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Xu1z3dtf1ZVUtT1iym3K_IrGeXCZ2FA6hn3_5ZvWxj8"

class Neo4jManager:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def add_document(self, doc_id, doc_type, extracted_text, tags):
        """Stores a document in Neo4j and links entities."""
        with self.driver.session() as session:
            query = """
            MERGE (d:Document {id: $doc_id, type: $doc_type, text: $extracted_text})
            FOREACH (person IN $people |
                MERGE (p:Person {name: person})
                MERGE (d)-[:MENTIONS]->(p)
            )
            FOREACH (org IN $organizations |
                MERGE (o:Organization {name: org})
                MERGE (d)-[:RELATED_TO]->(o)
            )
            FOREACH (date IN $dates |
                MERGE (dt:Date {name: date})
                MERGE (d)-[:DATED]->(dt)
            )
            FOREACH (location IN $locations |
                MERGE (loc:Location {name: location})
                MERGE (d)-[:LOCATED_IN]->(loc)
            )
            """
            session.run(query, doc_id=doc_id, doc_type=doc_type, extracted_text=extracted_text, 
                        people=tags.get("people", []), 
                        organizations=tags.get("organizations", []),
                        dates=tags.get("dates", []),
                        locations=tags.get("locations", []))

    def find_related_documents(self, query_text):
        """Finds related documents based on similar tags/entities."""
        with self.driver.session() as session:
            query = """
            MATCH (d:Document)-[r]->(e)
            WHERE e.name CONTAINS $query_text
            RETURN d.text AS related_docs, d.type AS type, collect(e.name) AS related_entities
            LIMIT 5
            """
            results = session.run(query, query_text=query_text)
            return [record for record in results]
