import faiss
from pathlib import Path
import pickle
import numpy as np
from app.core.config import settings

VECTOR_STORE_PATH = Path(settings.VECTOR_STORE_PATH) / "index.faiss"
META_PATH = Path(settings.VECTOR_STORE_PATH) / "meta.pkl"

class VectorStore:
    def __init__(self, dim: int):
        self.dim = dim
        # Ensure storage directory exists
        VECTOR_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)

        if VECTOR_STORE_PATH.exists() and META_PATH.exists():
            try:
                self.index = faiss.read_index(str(VECTOR_STORE_PATH))
                self.metadata = pickle.loads(META_PATH.read_bytes())
            except Exception:
                # If loading fails, create new index
                self.index = faiss.IndexFlatL2(dim)
                self.metadata = []
        else:
            self.index = faiss.IndexFlatL2(dim)
            self.metadata = []

    def add(self, vectors: list[list[float]], metadatas: list[dict], persist: bool = False):
        if not vectors or not metadatas:
            raise ValueError("Vectors and metadatas must not be empty")
        
        if len(vectors) != len(metadatas):
            raise ValueError("Vectors and metadatas must have the same length")
        
        vectors_np = np.array(vectors, dtype="float32")
        # Ensure correct shape
        if vectors_np.ndim != 2 or vectors_np.shape[1] != self.dim:
            raise ValueError(f"Vectors must be 2D array with shape (n, {self.dim})")
        
        self.index.add(vectors_np)
        self.metadata.extend(metadatas)

        if persist:
            self._persist()

    def search(self, vector: list[float], k: int = 5):
        if not vector or len(vector) != self.dim:
            raise ValueError(f"Vector must have dimension {self.dim}")
        
        if self.index.ntotal == 0:
            return []
        
        # Ensure k doesn't exceed available vectors
        k = min(k, self.index.ntotal)
        
        query_vector = np.array([vector], dtype="float32")
        distances, indices = self.index.search(query_vector, k)

        results = []
        for idx in indices[0]:
            if 0 <= idx < len(self.metadata):
                results.append(self.metadata[idx])

        return results
    
    def _persist(self):
        """Persist index and metadata to disk"""
        try:
            VECTOR_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, str(VECTOR_STORE_PATH))
            META_PATH.write_bytes(pickle.dumps(self.metadata))
        except Exception as e:
            # Log error but don't fail the operation
            import logging
            import traceback
            logging.error(f"Failed to persist vector store: {e}\n{traceback.format_exc()}")