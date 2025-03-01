import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load a pre-trained sentence transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# FAISS Index setup
dimension = 384  # Model output dimension
index = faiss.IndexFlatL2(dimension)  
documents = []  # Store original text

def add_document(text):
    """Converts text to an embedding and stores it in FAISS."""
    vector = model.encode([text])[0]
    index.add(np.array([vector], dtype=np.float32))
    documents.append(text)

def search(query, top_k=3):
    """Searches for similar documents using FAISS."""
    query_vector = model.encode([query])[0].reshape(1, -1)
    distances, indices = index.search(query_vector, top_k)
    results = [documents[i] for i in indices[0] if i < len(documents)]
    return results
