from fastapi import APIRouter, UploadFile, File
from app.services.ocr_service import extract_text_from_file
from app.services.tagging_service import extract_tags
from app.services.vertex_ai import VertexAIService
import firebase_admin
from firebase_admin import credentials, firestore

router = APIRouter()
vertex_ai = VertexAIService()  # Initialize Vertex AI Service

# ✅ Load Firebase credentials (Only initialize if not already initialized)
if not firebase_admin._apps:
    cred = credentials.Certificate("service_account.json")  # Ensure correct path
    firebase_admin.initialize_app(cred)

# ✅ Initialize Firestore Client
db = firestore.client()

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

    # ✅ Step 5: Store the document and embeddings in Firestore
    doc_ref = db.collection("documents").document(doc_id)
    doc_ref.set({
        "name": doc_id,
        "type": doc_type,
        "extracted_text": extracted_text,
        "tags": tags,
        "embeddings": embeddings if embeddings else [],  # ✅ Store actual embeddings
    })

    return {
        "message": "Document uploaded & stored successfully!",
        "filename": doc_id,
        "document_type": doc_type,
        "tags": tags,
        "extracted_text": extracted_text,
        "embeddings": embeddings,  # ✅ Ensure embeddings are returned correctly
    }
