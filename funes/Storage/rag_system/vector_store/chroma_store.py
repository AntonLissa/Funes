from funes.Storage.rag_system.vector_store.vector_store import VectorStore
import chromadb
from chromadb.config import Settings
import uuid


class ChromaStore(VectorStore):
    """
    Wrapper per ChromaDB reale.

    Responsabilità:
    - salvare documenti con embedding
    - fare similarity search
    - opzionalmente persistere su disco
    - permettere la pulizia completa della collection
    """

    def __init__(self, collection_name: str, persist_path: str | None = None):
        self.collection_name = collection_name
        self.persist_path = persist_path

        # inizializzazione client
        if persist_path:
            self.client = chromadb.PersistentClient(path=persist_path)
        else:
            self.client = chromadb.EphemeralClient()

        # otteniamo o creiamo la collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

    def get_content_hashes(self) -> set:
        """
        Ritorna l'insieme di tutti i content_hash già presenti nella collection.
        Utile per deduplicare chunk prima di aggiungere.
        """
        results = self.collection.get()
        metas = results.get("metadatas", [])
        content_hashes = set()

        for meta in metas:
            ch = meta.get("content_hash")
            if ch:
                content_hashes.add(ch)

        return content_hashes


    def add(self, ids, documents, embeddings, metadata):
        """
        Aggiunge documenti alla collection.
        """

        
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadata
        )

    def search(self, query_embedding, k=3):
        """
        Esegue similarity search usando Chroma.
        """

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        items = []

        for doc, meta, dist in zip(docs, metas, distances):

            items.append({
                "text": doc,
                "metadata": meta,
                "score": dist
            })

        return items

    def clean_all_data(self):
        """
        Cancella completamente tutti i dati della collection.
        Utile quando usi una memoria persistente e vuoi resettarla.
        """

        # cancelliamo la collection
        self.client.delete_collection(self.collection_name)

        # e la ricreiamo vuota
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )
    
    def get_all(self):
        """
        Ritorna tutti i documenti presenti nella collection.
        Utile per debug o per costruire un indice completo.
        """

        results = self.collection.get()

        docs = results.get("documents", [])
        metas = results.get("metadatas", [])
        ids = results.get("ids", [])

        items = []

        for doc, meta, id in zip(docs, metas, ids):

            items.append({
                "id": id,
                "text": doc,
                "metadata": meta
            })

        return items


if __name__ == "__main__":
    # test rapido
    kb_collection = ChromaStore(collection_name="knowledge_base_collection", persist_path="saved_data/chroma_kb")
    all_data = kb_collection.get_all()
    all_titles = set([item['metadata']['title'] for item in all_data])
    for elem in all_titles:
        print(elem)