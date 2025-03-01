from neo4j import GraphDatabase

# Use your connected database URI
NEO4J_URI = "neo4j+ssc://fdc02495.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Xu1z3dtf1ZVUtT1iym3K_IrGeXCZ2FA6hn3_5ZvWxj8"

class Neo4jManager:
    def __init__(self):
        """Initialize the Neo4j connection"""
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        self._create_constraints()  # Ensure indexes are created

    def close(self):
        """Close the database connection"""
        self.driver.close()

    def _create_constraints(self):
        """Create constraints for faster lookups (only runs once)"""
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (o:Organization) REQUIRE o.name IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (dt:Date) REQUIRE dt.name IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (loc:Location) REQUIRE loc.name IS UNIQUE")

    def add_document(self, doc_id, doc_type, extracted_text, tags):
        """Stores a document in Neo4j and links entities."""
        with self.driver.session() as session:
            query = """
            MERGE (d:Document {id: $doc_id})
            SET d.type = $doc_type, d.text = $extracted_text

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
        """Finds related documents based on shared entities."""
        with self.driver.session() as session:
            query = """
            CALL db.index.fulltext.queryNodes("entityIndex", $query_text) YIELD node
            MATCH (d:Document)-[r]->(node)
            RETURN d.text AS related_docs, d.type AS type, collect(node.name) AS related_entities
            LIMIT 5
            """
            results = session.run(query, query_text=query_text)
            return [record for record in results]

    def create_fulltext_index(self):
        """Creates a full-text search index to optimize text-based queries."""
        with self.driver.session() as session:
            session.run("CREATE FULLTEXT INDEX entityIndex IF NOT EXISTS FOR (e) ON EACH [e.name]")

