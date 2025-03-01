from fastapi import APIRouter, UploadFile, File
from app.services.ocr_service import extract_text_from_file
from app.services.tagging_service import extract_tags
from app.services.neo4j_db import Neo4jManager

router = APIRouter()
neo4j_manager = Neo4jManager()  # Initialize Neo4j connection

@router.post("/upload/")
async def upload_handler(file: UploadFile = File(...)):
    """Handles document processing: OCR, tagging, classification, and Neo4j storage."""

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

    # Step 4: Store document relationships in Neo4j for relationship-based search
    neo4j_manager.add_document(doc_id, doc_type, extracted_text, tags)

    # ✅ Step 5: Return processed data (Frontend stores this in Firestore)
    return {
        "message": "Document processed successfully!",
        "filename": doc_id,
        "document_type": doc_type,
        "tags": tags,
        "extracted_text": extracted_text
    }
