from fastapi import APIRouter, Query
from app.services.faiss_service import FAISSService

router = APIRouter()
faiss_service = FAISSService()  # Initialize FAISS

@router.get("/search/")
async def search_documents(query: str = Query(..., description="Search query")):
    """Search for documents using FAISS"""
    print(f"🔍 Received search query: {query}")

    # Run FAISS search
    search_results = faiss_service.search_similar(query)

    return {"query": query, "results": search_results}
