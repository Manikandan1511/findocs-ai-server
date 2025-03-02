from google.cloud import language_v1
from google.oauth2 import service_account

# Load Google NLP credentials
credentials = service_account.Credentials.from_service_account_file("service_account.json")
client = language_v1.LanguageServiceClient(credentials=credentials)

# **Predefined Keywords for Document Type Classification**
DOCUMENT_TYPE_KEYWORDS = {
    "Invoices": ["invoice", "bill", "amount due", "payment due", "purchase order"],
    "Tax Documents": ["tax", "IRS", "income", "tax return", "Form 1040", "GST", "VAT"],
    "Bank Statements": ["account summary", "transaction history", "debit", "credit", "bank statement", "statement", "transaction"],
    "Legal Contracts": ["agreement", "contract", "terms and conditions", "non-disclosure agreement"],
    "Medical Reports": ["diagnosis", "prescription", "medical record", "doctor's note", "hospital"],
    "Receipts": ["receipt", "purchase", "transaction ID", "amount paid"],
    "Employment Letters": ["employment verification", "salary slip", "job offer", "HR"],
    "Academic Certificates": ["degree", "diploma", "certificate", "academic transcript"],
    "Cheque": ["bank", "payee", "bearer"]
}

def extract_tags(text: str):
    """Extracts named entities and document type using Google Cloud NLP API."""
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    response = client.analyze_entities(document=document)

    # Extract metadata (People, Dates, Orgs, etc.)
    tags = {
        "people": [entity.name for entity in response.entities if language_v1.Entity.Type(entity.type_).name == "PERSON"],
        "dates": [entity.name for entity in response.entities if language_v1.Entity.Type(entity.type_).name == "DATE"],
        "organizations": [entity.name for entity in response.entities if language_v1.Entity.Type(entity.type_).name == "ORGANIZATION"],
        "locations": [entity.name for entity in response.entities if language_v1.Entity.Type(entity.type_).name == "LOCATION"],
        "financial_terms": [entity.name for entity in response.entities if language_v1.Entity.Type(entity.type_).name in ["PRICE", "MONEY"]],
    }

    # **Classify Document Type using predefined keywords**
    text_lower = text.lower()
    for doc_type, keywords in DOCUMENT_TYPE_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            tags["doc_type"] = doc_type
            break
    else:
        tags["doc_type"] = "Unknown"

    return tags