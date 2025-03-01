from google.cloud import storage
from app.core.config import BUCKET_NAME

storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

def generate_signed_url(filename: str, content_type: str):
    """Generate a signed URL for uploading a file to GCS."""
    blob = bucket.blob(f"uploads/{filename}")
    
    signed_url = blob.generate_signed_url(
        version="v4",
        expiration=600,
        method="PUT",
        content_type=content_type
    )

    return signed_url
