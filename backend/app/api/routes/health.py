from fastapi import APIRouter
from app.core.config import settings
from pathlib import Path

router = APIRouter()


@router.get('/health')
async def health_check():
    """Health check endpoint with dependency checks"""
    health_status = {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": "1.0.0"
    }
    
    # Check vector store accessibility
    try:
        vector_store_path = Path(settings.VECTOR_STORE_PATH)
        health_status["vector_store"] = "accessible" if vector_store_path.exists() else "not_initialized"
    except Exception:
        health_status["vector_store"] = "error"
    
    # Check document storage
    try:
        doc_storage_path = Path(settings.DOCUMENT_STORAGE_PATH)
        health_status["document_storage"] = "accessible" if doc_storage_path.exists() else "not_initialized"
    except Exception:
        health_status["document_storage"] = "error"
    
    return health_status