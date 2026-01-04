from pathlib import Path
from app.rag.loader import load_document
from app.rag.chunker import chunk_text
from app.rag.embeddings import EmbeddingModel
from app.rag.vectorstore import VectorStore
from app.core.config import settings
from app.observability.logger import JsonLogger

logger = JsonLogger("rag-ingest")

embedding_model = EmbeddingModel(model_name=settings.EMBEDDING_MODEL)
vector_store = VectorStore(dim=settings.EMBEDDING_DIM)

EMBED_BATCH_SIZE = 512

def ingest_document(file_path: Path, document_id: str):
    """Ingest a document into the vector store"""
    try:
        logger.log("INFO", "ingestion_started", document_id=document_id, file_path=str(file_path), batch_size=EMBED_BATCH_SIZE)
        
        # Load document
        text = load_document(file_path)
        if not text or not text.strip():
            raise ValueError(f"Document {file_path} is empty or could not be loaded")
        
        # Chunk text
        batch_chunks = []
        batch_metadatas = []

        total_chunks = 0
        total_vectors = 0

        logger.log("INFO", "creating_chunks", document_id=document_id)

        for idx, chunk in enumerate(
            chunk_text(
                text,
                chunk_size=settings.CHUNK_SIZE,
                overlap=settings.CHUNK_OVERLAP
            )
        ):
            batch_chunks.append(chunk)
            batch_metadatas.append({
                "document_id": document_id,
                "content": chunk,
                "chunk_index": idx,
                "file_path": str(file_path)
            })

            total_chunks += 1

            if len(batch_chunks) >= EMBED_BATCH_SIZE:
                logger.log(
                    "INFO",
                    "embedding_batch_started",
                    document_id=document_id,
                    batch_size=len(batch_chunks),
                    processed_chunks=total_chunks
                )

                embeddings = embedding_model.embed(batch_chunks)
                vector_store.add(embeddings, batch_metadatas, persist=False)

                total_vectors += len(embeddings)

                logger.log(
                    "INFO",
                    "embedding_batch_completed",
                    document_id=document_id,
                    batch_vectors=len(embeddings),
                    total_vectors=total_vectors
                )

                batch_chunks.clear()
                batch_metadatas.clear()
        
        # Process final batch
        if batch_chunks:
            logger.log(
                "INFO",
                "embedding_final_batch_started",
                document_id=document_id,
                batch_size=len(batch_chunks)
            )

            embeddings = embedding_model.embed(batch_chunks)
            vector_store.add(embeddings, batch_metadatas, persist=False)

            total_vectors += len(embeddings)

            logger.log(
                "INFO",
                "embedding_final_batch_completed",
                document_id=document_id,
                batch_vectors=len(embeddings),
                total_vectors=total_vectors
            )

        # Persist into vector store
        vector_store._persist()

        logger.log(
            "INFO",
            "ingestion_completed",
            document_id=document_id,
            total_chunks=total_chunks,
            total_vectors=total_vectors
        )

    except Exception as e:
        import traceback
        logger.log(
            "ERROR",
            "ingestion_failed",
            document_id=document_id,
            file_path=str(file_path),
            error=str(e),
            error_type=type(e).__name__,
            traceback=traceback.format_exc()
        )
        raise