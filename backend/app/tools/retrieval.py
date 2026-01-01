from app.tools.base import Tool
from app.rag.embeddings import EmbeddingModel
from app.rag.vectorstore import VectorStore
from app.observability.logger import JsonLogger

logger = JsonLogger("retrieval-tool")

embedding_model = EmbeddingModel()
vector_store = VectorStore(dim=384)

class RetrievalTool(Tool):
    name = "retrieve_documents"
    description = "Search relevant documents from vector store"
    input_schema = {
        "query": "string",
        "top_k": "integer"
    }

    def run(self, query: str, top_k: int = 5):
        logger.log(
            "INFO",
            "retrieval_started",
            query=query,
            top_k=top_k
        )

        embedding = embedding_model.embed([query])[0]
        results = vector_store.search(embedding, k=top_k)

        logger.log(
            "INFO",
            "retrieval_completed",
            results_count=len(results)
        )

        return results