from fastapi import APIRouter, UploadFile, File
from app.services.ocr_service import extract_text_from_file
from app.services.tagging_service import extract_tags
from app.services.neo4j_db import Neo4jManager

router = APIRouter()
neo4j_manager = Neo4jManager()

@router.post("/upload/")
async def upload_handler(file: UploadFile = File(...)):
    """Handles full document processing: OCR, tagging, classification, and storage in Neo4j."""

    # Step 1: Extract text using OCR
    extracted_text = extract_text_from_file(await file.read(), file.filename)

    # Step 2: Extract metadata (People, Dates, Organizations, etc.)
    tags = extract_tags(extracted_text)

    # Step 3: Get document type from extracted tags
    doc_type = tags.get("doc_type", "Unknown")  

    # Step 4: Generate unique document ID
    doc_id = f"doc-{file.filename}"

    # Step 5: Store document & relationships in Neo4j
    neo4j_manager.add_document(doc_id, doc_type, extracted_text, tags)

    return {
        "message": "Document processed successfully!",
        "doc_id": doc_id,
        "type": doc_type,
        "tags": tags
    }