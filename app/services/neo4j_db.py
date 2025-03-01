from neo4j import GraphDatabase

# Use your connected database URI
NEO4J_URI = "neo4j+ssc://fdc02495.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Xu1z3dtf1ZVUtT1iym3K_IrGeXCZ2FA6hn3_5ZvWxj8"

class Neo4jManager:
    def __init__(self):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        self._create_constraints()

    def close(self):
        """Close the Neo4j connection"""
        self.driver.close()

    def _create_constraints(self):
        """Ensure indexes are created for fast queries"""
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Embedding) REQUIRE e.id IS UNIQUE")

    def add_document(self, doc_id, doc_type, extracted_text, tags, embedding):
        """Stores document, relationships, and embeddings in Neo4j"""
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

            // Store Embeddings
            MERGE (e:Embedding {id: $doc_id})
            SET e.vector = $embedding
            MERGE (d)-[:HAS_EMBEDDING]->(e)
            """
            session.run(query, doc_id=doc_id, doc_type=doc_type, extracted_text=extracted_text,
                        people=tags.get("people", []),
                        organizations=tags.get("organizations", []),
                        embedding=embedding)

    def search_similar_documents(self, query_embedding):
        """Finds similar documents using cosine similarity in Neo4j"""
        with self.driver.session() as session:
            query = """
            MATCH (e:Embedding)
            WITH e, gds.alpha.similarity.cosine(e.vector, $query_embedding) AS score
            ORDER BY score DESC LIMIT 3
            MATCH (d:Document)-[:HAS_EMBEDDING]->(e)
            RETURN d.id AS doc_id, d.type AS type, d.text AS extracted_text, score
            """
            results = session.run(query, query_embedding=query_embedding)
            return [record for record in results]