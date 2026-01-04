from app.tools.base import Tool
from app.rag.embeddings import EmbeddingModel
from app.rag.vectorstore import VectorStore
from app.core.config import settings
from app.observability.logger import JsonLogger

logger = JsonLogger("retrieval-tool")

embedding_model = EmbeddingModel(model_name=settings.EMBEDDING_MODEL)
vector_store = VectorStore(dim=settings.EMBEDDING_DIM)


class RetrievalTool(Tool):
    """Tool for retrieving relevant document chunks from the vector store"""
    
    name = "retrieve_documents"
    description = "Search relevant documents from vector store"
    input_schema = {
        "query": "string",
        "top_k": "integer"
    }

    async def run(self, query: str, top_k: int = None):
        """
        Retrieve relevant document chunks.
        
        Args:
            query: Search query string
            top_k: Number of results to return (defaults to config value)
        
        Returns:
            List of context dictionaries with 'content' and metadata
        """
        if not query or not query.strip():
            logger.log("WARN", "empty_query")
            return []
        
        top_k = top_k or settings.RETRIEVAL_TOP_K
        
        logger.log(
            "INFO",
            "retrieval_started",
            query=query[:100],  # Log first 100 chars
            top_k=top_k
        )

        try:
            # Generate embedding for query (this is CPU-bound, run in thread)
            import asyncio
            embedding = await asyncio.to_thread(
                embedding_model.embed,
                [query.strip()]
            )
            embedding = embedding[0]
            
            # Search vector store (also CPU-bound)
            results = await asyncio.to_thread(
                vector_store.search,
                embedding,
                k=top_k
            )
            
            # Normalize results to ensure 'content' key exists
            normalized_results = []
            for result in results:
                # Handle both 'content' and 'context' keys for compatibility
                content = result.get("content") or result.get("context", "")
                normalized_results.append({
                    "content": content,
                    "document_id": result.get("document_id"),
                    "chunk_index": result.get("chunk_index"),
                    "file_path": result.get("file_path")
                })

            logger.log(
                "INFO",
                "retrieval_completed",
                results_count=len(normalized_results)
            )

            return normalized_results
        
        except Exception as e:
            logger.log(
                "ERROR",
                "retrieval_failed",
                query=query[:100],
                error=str(e)
            )
            return []