from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.observability.logger import JsonLogger
import logging

# Suppress sentence-transformers info logs
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

logger = JsonLogger("embedding-model")


class EmbeddingModel:
    """Wrapper for sentence-transformers embedding model"""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        logger.log("INFO", "loading_embedding_model", model=self.model_name)
        self.model = SentenceTransformer(self.model_name)
        logger.log("INFO", "embedding_model_loaded", model=self.model_name)
    
    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
        
        Returns:
            List of embedding vectors (each is a list of floats)
        """
        if not texts:
            return []
        
        try:
            embeddings = self.model.encode(
                texts,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            return embeddings.tolist()
        except Exception as e:
            logger.log(
                "ERROR",
                "embedding_failed",
                texts_count=len(texts),
                error=str(e)
            )
            raise