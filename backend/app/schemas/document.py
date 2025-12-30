from pydantic import BaseModel
from typing import Optional

class DocumentUploadRequest(BaseModel):
    title : str
    description: Optional[str] = None

class DocumentResponse(BaseModel):
    document_id: str 
    title: str
    status: str

    