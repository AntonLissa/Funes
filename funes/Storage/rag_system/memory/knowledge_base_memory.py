from funes.Storage.rag_system.chunker.base_chunker import BaseChunker

from .memory import Memory
from vector_store.vector_store import VectorStore
from embeddings.embedding_model import EmbeddingModel
class KBMemory(Memory):
    """
    Memoria per documenti generici.
    Usa un VectorStore per retrieval semantico.
    """

    def __init__(self, store: VectorStore, embedder: EmbeddingModel, chunker: BaseChunker):
        self.store = store
        self.embedder = embedder
        self.chunker = chunker
        self.required_metadata = [] # da definire

    def _validate_metadata(self, metadata: dict):
        missing = [f for f in self.required_metadata if f not in metadata]
        if missing:
            raise ValueError(f"Missing (i) field(i) in metadata: {missing}")
        return metadata

    def add(self, path: str):
        chunks = self.chunker.chunk(path)

        # 1. recupera content_hash già presenti nello store
        existing_hashes = self.store.get_content_hashes() 

        # 2. filtra chunk già presenti
        new_chunks = []
        for chunk in chunks:
            if chunk.metadata['content_hash'] not in existing_hashes:
                new_chunks.append(chunk)
                #print(f"KBMEMORY: Nuovo chunk da aggiungere (hash {chunk.metadata['chunk_id']})")

        if not new_chunks:
            print("KBMEMORY: Nessun chunk nuovo da aggiungere.")
            return

        # 3. genera embedding solo per i chunk nuovi
        embeddings = [self.embedder.embed(chunk.page_content) for chunk in new_chunks]
        metadatas = [self._validate_metadata(chunk.metadata) for chunk in new_chunks]
        ids = [f"{chunk.metadata.get('chunk_id')}" for chunk in new_chunks]  # non più titolo incluso

        # 4. aggiungi allo store
        self.store.add(
            ids=ids,
            documents=[chunk.page_content for chunk in new_chunks],
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