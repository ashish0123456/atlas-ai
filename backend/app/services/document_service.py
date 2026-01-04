import uuid
from app.observability.logger import JsonLogger

logger = JsonLogger("document-service")


class DocumentService:
    """Service for managing document operations"""

    def create_document(self, title: str, description: str | None = None) -> dict:
        """
        Create a new document record.
        
        Args:
            title: Document title
            description: Optional document description
        
        Returns:
            Dictionary with document_id, title, and status
        """
        document_id = str(uuid.uuid4())

        logger.log(
            "INFO",
            "document_created",
            document_id=document_id,
            title=title[:100] if title else None
        )

        return {
            "document_id": document_id,
            "title": title or "Untitled",
            "status": "uploaded"
        }

