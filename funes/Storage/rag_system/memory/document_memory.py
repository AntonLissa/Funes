from .memory import Memory
from vector_store.vector_store import VectorStore
from embeddings.embedding_model import EmbeddingModel

class DocumentMemory(Memory):
    """
    Memoria per documenti generici.
    Usa un VectorStore per retrieval semantico.
    """

    def __init__(self, store: VectorStore, embedder: EmbeddingModel):
        self.store = store
        self.embedder = embedder

    def add(self, doc_id: str, text: str, metadata: dict = None):
        """
        Salva un documento nella memoria.
        doc_id: identificatore univoco
        text: contenuto del documento
        metadata: info aggiuntive (tipo documento, data, autore, ecc.)
        """
        embedding = self.embedder.embed(text)

        self.store.add(
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding],
            metadata=[metadata or {"type": "document"}]
        )

    def search(self, query: str, k: int = 3):
        """
        Cerca i documenti più rilevanti per la query.
        """
        embedding = self.embedder.embed(query)
        results = self.store.search(embedding, k=k)

        return results
