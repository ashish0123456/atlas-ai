from app.rag.embeddings import EmbeddingModel
from app.rag.vectorstore import VectorStore
import logging

logger = logging.getLogger(__name__)
embedding_model = EmbeddingModel()
vector_store = VectorStore(dim=384)

class QueryService: 

    def process_query(self, question: str):
        logger.info(f"Received query: {question}")

        query_embedding = embedding_model.embed([question])[0]

        contexts = vector_store.search(query_embedding, k=5)

        return {
            "answer": "Context retrieved successfully",
            "confidence": 0.0,
            "contexts": contexts
        }
