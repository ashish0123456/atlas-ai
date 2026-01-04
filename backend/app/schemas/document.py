from pydantic import BaseModel


class DocumentResponse(BaseModel):
    document_id: str 
    title: str
    status: str
