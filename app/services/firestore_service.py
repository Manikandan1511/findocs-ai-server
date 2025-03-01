from google.cloud import firestore
from google.oauth2 import service_account

# ✅ Load service account credentials
SERVICE_ACCOUNT_FILE = "service_account.json"  # Ensure this file is in the correct location
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)

# ✅ Initialize Firestore Client
db = firestore.Client(credentials=credentials)

# ✅ Fetch stored document embeddings
def get_document_embeddings():
    try:
        docs_ref = db.collection("documents").stream()  # Fetch all documents
        embeddings_data = []
        
        for doc in docs_ref:
            doc_data = doc.to_dict()
            if "embeddings" in doc_data:
                embeddings_data.append({
                    "doc_id": doc.id,
                    "text": doc_data.get("extracted_text", ""),
                    "embeddings": doc_data["embeddings"],
                    "tags": doc_data.get("tags", {})
                })
        
        return embeddings_data
    except Exception as e:
        print(f"❌ Firestore Error: {e}")
        return []
