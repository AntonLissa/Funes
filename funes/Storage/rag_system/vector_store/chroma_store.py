from vector_store.vector_store import VectorStore
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
            self.client = chromadb.Client(
                Settings(persist_directory=persist_path)
            )
        else:
            self.client = chromadb.Client()

        # otteniamo o creiamo la collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

    def add(self, ids, documents, embeddings, metadata):
        """
        Aggiunge documenti alla collection.
        """

        # genera id se mancanti
        final_ids = []
        for i in range(len(documents)):
            if ids and ids[i]:
                final_ids.append(ids[i])
            else:
                final_ids.append(str(uuid.uuid4()))

        self.collection.add(
            ids=final_ids,
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
