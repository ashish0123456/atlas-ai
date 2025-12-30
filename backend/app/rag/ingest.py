from pathlib import Path
from app.rag.loader import load_document
from app.rag.chunker import chunk_text
from app.rag.embeddings import EmbeddingModel
from app.rag.vectorstore import VectorStore

embedding_model = EmbeddingModel()
vector_store = VectorStore(dim=384)

def ingest_document(file_path: Path, document_id: str):
    text = load_document(file_path)
    chunks = chunk_text(text)

    embeddings = embedding_model.embed(chunks)

    metadatas = [
        {
            "document_id": document_id,
            "content": chunk
        }
        for chunk in chunks
    ]

    vector_store.add(embeddings, metadatas)