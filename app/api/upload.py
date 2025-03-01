from fastapi import APIRouter, UploadFile, File
from app.services.ocr_service import extract_text_from_file
from app.services.tagging_service import extract_tags
from app.services.vertex_ai import VertexAIService

router = APIRouter()
vertex_ai = VertexAIService()  # Initialize Vertex AI Service

@router.post("/upload/")
async def upload_handler(file: UploadFile = File(...)):
    """Handles document processing: OCR, tagging, classification, embeddings"""

    # Step 1: Read file contents
    file_content = await file.read()
    doc_id = file.filename

    # Step 2: Extract text using OCR
    extracted_text = extract_text_from_file(file_content, doc_id)

    # Step 3: Extract metadata (People, Dates, Organizations, etc.)
    tags_info = extract_tags(extracted_text)
    doc_type = tags_info["doc_type"]
    tags = {
        "people": tags_info.get("people", []),
        "organizations": tags_info.get("organizations", []),
        "dates": tags_info.get("dates", []),
        "locations": tags_info.get("locations", []),
    }

    # Step 4: Generate document embeddings using Vertex AI
    embeddings = vertex_ai.get_embedding(extracted_text)

    # ✅ Step 5: Return data to the frontend (Frontend will store in Firestore)
    return {
        "filename": doc_id,
        "document_type": doc_type,
        "extracted_text": extracted_text,
        "tags": tags,
        "embeddings": embeddings,  # Frontend should store this in Firestore
    }
