from pydantic import BaseModel

class FileRequest(BaseModel):
    filename: str
    content_type: str