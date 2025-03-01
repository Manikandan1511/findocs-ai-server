from fastapi import APIRouter, UploadFile, File
from app.services.ocr_service import extract_text_from_file
from app.services.tagging_service import extract_tags

router = APIRouter()

@router.post("/ocr/")
async def ocr_handler(file: UploadFile = File(...)):
    extracted_text = extract_text_from_file(await file.read(), file.filename)
    tags = extract_tags(extracted_text)
    return {"extracted_text": extracted_text, "tags": tags}
