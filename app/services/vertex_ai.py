import vertexai
from vertexai.language_models import TextEmbeddingModel
from google.oauth2 import service_account
import numpy as np

credentials = service_account.Credentials.from_service_account_file("service_account.json")

# ✅ Initialize Vertex AI with credentials
PROJECT_ID = "findocs-622a4"
REGION = "us-central1"

vertexai.init(project=PROJECT_ID, location=REGION, credentials=credentials)

class VertexAIService:
    def __init__(self):
        """Initialize Vertex AI embedding model"""
        self.model = TextEmbeddingModel.from_pretrained("textembedding-gecko")

    def get_embedding(self, text):
        """Generates embeddings using Vertex AI"""
        try:
            print(f"🔍 Generating Embeddings for: {text}")
            embeddings = self.model.get_embeddings([text])[0].values
            print(f"✅ Embeddings generated successfully!")
            return list(embeddings)  # ✅ Convert to list before storing in Firestore
        except Exception as e:
            print(f"❌ Vertex AI Error: {e}")
            return None

    def cosine_similarity(self, vec1, vec2):
        """Computes cosine similarity between two embeddings"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))