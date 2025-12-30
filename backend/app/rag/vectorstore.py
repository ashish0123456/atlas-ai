import faiss
from pathlib import Path
import pickle

VECTOR_STORE_PATH = Path("storage/vectorstore/index.faiss")
META_PATH = Path("storage/vectorstore/meta.pkl")

class VectorStore:
    def __init__(self, dim: int):
        self.dim = dim

        if VECTOR_STORE_PATH.exists():
            self.index = faiss.read_index(str(VECTOR_STORE_PATH))
            self.metadata = pickle.loads(META_PATH.read_bytes())
        else:
            self.index = faiss.IndexFlatL2(dim)
            self.metadata = []

    def add(self, vectors: list[list[float]], metadatas: list[dict]):
        self.index.add(faiss.vector_to_array(vectors).reshape(len(vectors), self.dim))
        self.metadata.extend(metadatas)
        self._persist()

    def search(self, vector: list[float], k: int = 5):
        distances, indices = self.index.search(faiss.vector_to_array([vector]).reshape(1, self.dim), k)

        results = []
        for idx in indices[0]:
            if idx < len(self.metadata):
                results.append(self.metadata[idx])

        return results
    
    def _persist(self):
        faiss.write_index(self.index, str(VECTOR_STORE_PATH))
        META_PATH.write_bytes(pickle.dumps(self.metadata))