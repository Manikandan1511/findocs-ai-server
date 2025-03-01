import firebase_admin
from firebase_admin import credentials, firestore

# ✅ Load Firebase credentials
SERVICE_ACCOUNT_FILE = "service_account.json"  # Ensure this file exists

# ✅ Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred)

# ✅ Initialize Firestore Client
db = firestore.client()

def get_document_embeddings():
    """Fetch stored document embeddings from Firestore"""
    try:
        docs_ref = db.collection("documents").stream()  # Fetch all documents
        embeddings_data = []
        
        for doc in docs_ref:
            doc_data = doc.to_dict()
            if "embeddings" in doc_data and isinstance(doc_data["embeddings"], list):  # ✅ Ensure valid embeddings
                embeddings_data.append({
                    "doc_id": doc.id,
                    "text": doc_data.get("extracted_text", ""),
                    "embeddings": doc_data["embeddings"],  # ✅ Return as-is, numpy conversion happens in search.py
                    "tags": doc_data.get("tags", {})
                })
        
        return embeddings_data
    except Exception as e:
        print(f"❌ Firestore Error: {e}")
        return []