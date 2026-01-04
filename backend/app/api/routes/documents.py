from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService
from app.rag.ingest import ingest_document
from app.core.config import settings
from app.observability.logger import JsonLogger
from pathlib import Path
import aiofiles
import asyncio

router = APIRouter(prefix='/documents')
logger = JsonLogger("documents-api")

document_service = DocumentService()

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and ingest a document into the RAG system.
    
    Flow:
    1. Validate file type and size
    2. Create document record
    3. Save file to storage
    4. Trigger background ingestion (chunking, embedding, vector store)
    
    Returns immediately after file save; ingestion runs asynchronously.
    """
    trace_id = None  # Could be added if needed for document uploads
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower() if file.filename else ""
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Validate file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )

        # Create document record
        document = document_service.create_document(
            title=file.filename or "Untitled",
            description=None
        )

        logger.log(
            "INFO",
            "document_upload_started",
            document_id=document["document_id"],
            filename=file.filename,
            file_size=len(content)
        )

        # Save file to storage
        storage_path = Path(settings.DOCUMENT_STORAGE_PATH) / document["document_id"]
        storage_path.mkdir(parents=True, exist_ok=True)
        
        file_path = storage_path / (file.filename or "document")

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        logger.log(
            "INFO",
            "document_saved",
            document_id=document["document_id"],
            file_path=str(file_path)
        )

        # Ingest document asynchronously (don't block response)
        # Use create_task to run in background, but track it for error handling
        ingestion_task = asyncio.create_task(
            asyncio.to_thread(ingest_document, file_path, document["document_id"])
        )
        
        # Add callback to log ingestion completion/failure
        def ingestion_done(task):
            try:
                if task.exception():
                    exception = task.exception()
                    error_msg = str(exception)
                    error_type = type(exception).__name__
                    logger.log(
                        "ERROR",
                        "ingestion_failed",
                        document_id=document["document_id"],
                        error=error_msg,
                        error_type=error_type,
                        traceback=str(exception.__traceback__) if hasattr(exception, '__traceback__') else None
                    )
                else:
                    logger.log(
                        "INFO",
                        "ingestion_completed",
                        document_id=document["document_id"]
                    )
            except Exception as e:
                import traceback
                logger.log(
                    "ERROR",
                    "ingestion_callback_error",
                    document_id=document["document_id"],
                    error=str(e),
                    traceback=traceback.format_exc()
                )
        
        ingestion_task.add_done_callback(ingestion_done)

        logger.log(
            "INFO",
            "document_upload_completed",
            document_id=document["document_id"]
        )

        return DocumentResponse(**document)
    
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        logger.log(
            "ERROR",
            "document_upload_failed",
            filename=file.filename if file else None,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document. Please try again."
        )
