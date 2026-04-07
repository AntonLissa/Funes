from .memory import Memory
from vector_store.vector_store import VectorStore
from embeddings.embedding_model import EmbeddingModel

class KBMemory(Memory):
    """
    Memoria per documenti generici.
    Usa un VectorStore per retrieval semantico.
    """

    def __init__(self, store: VectorStore, embedder: EmbeddingModel, chunker=None):
        self.store = store
        self.embedder = embedder
        self.chunker = chunker
        self.required_metadata = [] # da definire

    def _validate_metadata(self, metadata: dict):
        missing = [f for f in self.required_metadata if f not in metadata]
        if missing:
            raise ValueError(f"Missing (i) field(i) in metadata: {missing}")
        return metadata

    def add(self, doc_id: str, text: str, metadata: dict = None):
        """
        Salva un documento nella memoria.
        doc_id: identificatore univoco
        text: contenuto del documento
        metadata: info aggiuntive (tipo documento, data, autore, ecc.)
        """
        self._validate_metadata(metadata)
        chunks = self.chunker.chunk(text)
        
        embeddings = [self.embedder.embed(chunk) for chunk in chunks]
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]  # id unici per chunk
        metadatas = [metadata.copy() for _ in chunks]        # stessa metadata per ogni chunk

        self.store.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadata=metadatas
        )


    def search(self, query: str, k: int = 3):
        """
        Cerca i documenti più rilevanti per la query.
        """
        embedding = self.embedder.embed(query)
        results = self.store.search(embedding, k=k)

        return results

    def get_all(self):
        """
        Ritorna tutti i documenti presenti nella memoria.
        Utile per debug o per costruire un indice completo.
        """
        return self.store.get_all()