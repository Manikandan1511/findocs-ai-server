from fastapi import APIRouter, Query
from app.services.firestore_service import get_document_embeddings
from app.services.vertex_ai import VertexAIService
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

router = APIRouter()
vertex_service = VertexAIService()  # Initialize Vertex AI Service

@router.get("/search/")
async def search_documents(query: str = Query(...)):
    """Handles semantic search with Vertex AI and Firestore embeddings"""
    
    # ✅ Convert user query to embedding
    query_embedding = vertex_service.get_embedding(query)

    if query_embedding is None:
        return {"error": "Failed to generate query embeddings"}
    
    # ✅ Fetch stored embeddings from Firestore
    stored_docs = get_document_embeddings()

    if not stored_docs:
        return {"message": "No documents found in Firestore."}

    # ✅ Compute similarity with stored embeddings
    results = []
    query_embedding_np = np.array(query_embedding).reshape(1, -1)

    for doc in stored_docs:
        if not isinstance(doc["embeddings"], list) or len(doc["embeddings"]) == 0:
            continue  # ✅ Skip documents without valid embeddings

        doc_embedding_np = np.array(doc["embeddings"]).reshape(1, -1)
        similarity = cosine_similarity(query_embedding_np, doc_embedding_np)[0][0]

        results.append({
            "doc_id": doc["doc_id"],
            "text": doc["text"],
            "tags": doc["tags"],
            "similarity": float(similarity),
            "type": doc["type"],
            "name": doc["name"],
            "file_url": doc["file_url"]
        })

    # ✅ Sort by similarity (Descending)
    results.sort(key=lambda x: x["similarity"], reverse=True)

    return {"results": results}