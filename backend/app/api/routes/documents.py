from fastapi import APIRouter, UploadFile, File
from app.schemas.document import DocumentResponse, DocumentUploadRequest
from app.services.document_service import DocumentService
from app.rag.ingest import ingest_document
from pathlib import Path

router = APIRouter(prefix='/documents')

document_servive = DocumentService()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    document = document_servive.create_document(
        title=file.filename,
        description=None
    )

    storage_path = Path("storage/documents") / document["document_id"]
    storage_path.mkdir(parents=True, exist_ok=True)
    
    file_path = storage_path / file.filename

    with open(file_path, "wb") as f:
        f.write(await file.read())

    ingest_document(file_path, document["document_id"])

    return document