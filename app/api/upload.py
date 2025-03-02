from fastapi import APIRouter, UploadFile, File
from app.services.ocr_service import extract_text_from_file
from app.services.tagging_service import extract_tags
from app.services.vertex_ai import VertexAIService
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
from datetime import datetime

router = APIRouter()
vertex_ai = VertexAIService()  # Initialize Vertex AI Service

# ✅ Load Firebase credentials (Only initialize if not already initialized)
if not firebase_admin._apps:
    cred = credentials.Certificate("service_account.json")  # Ensure correct path
    firebase_admin.initialize_app(cred)

# ✅ Initialize Firestore Client
db = firestore.client()

# 🚨 High-Risk Keywords List
HIGH_RISK_KEYWORDS = [
    "urgent transfer", "wire to new account", "cash payment", "no tax", "unregistered vendor"
]

def detect_fraud(extracted_text, doc_metadata):
    """Detects possible fraud in financial documents"""
    alerts = []

    # 🛑 1. Detect Duplicate Invoice
    text_hash = hashlib.sha256(extracted_text.encode()).hexdigest()
    docs_ref = db.collection("documents").where("text_hash", "==", text_hash).get()
    if len(docs_ref) > 0:
        alerts.append("🚨 Duplicate Invoice Detected")

    # 🛑 3. Validate Total Amount
    total_amount = doc_metadata.get("total", 0)
    subtotal = doc_metadata.get("subtotal", 0)
    tax = doc_metadata.get("tax", 0)
    if subtotal + tax != total_amount:
        alerts.append("❌ Invoice Total Doesn't Match Line Items")

    # 🛑 4. Check High-Risk Keywords
    for keyword in HIGH_RISK_KEYWORDS:
        if keyword.lower() in extracted_text.lower():
            alerts.append(f"⚠️ High-Risk Keyword Detected: {keyword}")

    return alerts

@router.post("/upload/")
async def upload_handler(file: UploadFile = File(...)):
    """Handles document processing: OCR, tagging, classification, embeddings, and fraud detection"""

    # ✅ Step 1: Read file contents
    file_content = await file.read()
    doc_id = file.filename

    # ✅ Step 2: Extract text using OCR
    extracted_text = extract_text_from_file(file_content, doc_id)

    # ✅ Step 3: Extract metadata (People, Dates, Organizations, etc.)
    tags_info = extract_tags(extracted_text)
    doc_type = tags_info["doc_type"]
    doc_metadata = {
        "date": tags_info.get("dates", [""])[0],
        "vendor": tags_info.get("organizations", [""])[0],
        "total": tags_info.get("total", 0),
        "subtotal": tags_info.get("subtotal", 0),
        "tax": tags_info.get("tax", 0),
    }

    # ✅ Step 4: Generate embeddings for semantic search
    embeddings = vertex_ai.get_embedding(extracted_text)

    # ✅ Step 5: Fraud Detection
    fraud_alerts = detect_fraud(extracted_text, doc_metadata)

    # ✅ Step 6: Store document, embeddings & fraud alerts in Firestore
    doc_ref = db.collection("documents").document(doc_id)
    doc_ref.set({
        "name": doc_id,
        "type": doc_type,
        "extracted_text": extracted_text,
        "tags": tags_info,
        "embeddings": embeddings if embeddings else [],  # Store actual embeddings
        "text_hash": hashlib.sha256(extracted_text.encode()).hexdigest(),
        "fraud_alerts": fraud_alerts,  # Store fraud alerts
    })

    return {
        "message": "Document uploaded & stored successfully!",
        "extracted_text": extracted_text,
        "filename": doc_id,
        "document_type": doc_type,
        "tags": tags_info,
        "fraud_alerts": fraud_alerts,  
        "embeddings": embeddings,
    }