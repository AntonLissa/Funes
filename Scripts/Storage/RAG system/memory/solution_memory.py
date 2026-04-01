from .memory import Memory
from vector_store.vector_store import VectorStore
from embeddings.embedding_model import EmbeddingModel

class SolutionMemory(Memory):
    """
    Memoria che salva problemi e soluzioni.
    Usa un VectorStore per fare retrieval semantico.
    """

    def __init__(self, store: VectorStore, embedder: EmbeddingModel):
        self.store = store
        self.embedder = embedder

    def add(self, problem: str, solution: str):
        """
        Salva un problema e la sua soluzione nella memoria.
        """
        text = f"Problem: {problem}\nSolution: {solution}"

        embedding = self.embedder.embed(text)

        self.store.add(
            ids=[problem],  # o qualche id univoco
            documents=[text],
            embeddings=[embedding],
            metadata=[{"type": "solution"}]
        )

    def search(self, query: str, k: int = 3):
        """
        Cerca le soluzioni più rilevanti per la query.
        """
        embedding = self.embedder.embed(query)
        results = self.store.search(embedding, k=k)

        # results tipicamente è una lista di dict o oggetti con:
        # text, score, metadata
        return results
