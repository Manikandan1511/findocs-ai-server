import os
from google.cloud import aiplatform
from sentence_transformers import SentenceTransformer

# Initialize GCP Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account.json"
aiplatform.init(project="findocs-622a4", location="us-central1")

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

class VertexAIService:
    def __init__(self, endpoint_name="your-endpoint-name"):
        """Initialize Vertex AI Matching Engine."""
        self.index = aiplatform.MatchingEngineIndex(endpoint_name=endpoint_name)

    def store_embedding(self, doc_id, doc_text):
        """Encodes document and stores embedding in Vertex AI."""
        embedding = model.encode(doc_text).tolist()
        self.index.upsert(datapoints=[{"id": doc_id, "embedding": embedding}])
        print(f"✅ Stored embedding for {doc_id}")

    def search_documents(self, query_text, top_k=3):
        """Finds similar documents using Vertex AI Matching Engine."""
        query_embedding = model.encode(query_text).tolist()
        response = self.index.find_neighbors(queries=[query_embedding], num_neighbors=top_k)
        return response
