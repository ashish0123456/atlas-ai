import uuid
import logging

logger = logging.getLogger(__name__)

class DocumentService:

    def create_document(self, title: str, description: str | None):
        document_id = str(uuid.uuid4())

        logger.info(f"Created document {document_id}")

        return {
            "document_id": document_id,
            "title": title,
            "status": "uploaded"
        }

