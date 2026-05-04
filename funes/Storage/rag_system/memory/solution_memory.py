import uuid

from sentence_transformers import CrossEncoder

from funes.Storage.rag_system.memory.bm25_index import BM25Index

from .memory import Memory
from vector_store.vector_store import VectorStore
from embeddings.embedding_model import EmbeddingModel

class SolutionMemory(Memory):
    """
    Memoria che salva problemi e soluzioni.
    Usa un VectorStore per fare retrieval semantico.
    """

    def __init__(self, store: VectorStore, bm25_index: BM25Index, embedder: EmbeddingModel):
        self.store = store
        self.bm25_index = bm25_index
        self.embedder = embedder
        self.reranker = CrossEncoder('BAAI/bge-reranker-base')


    def add(self, data):
        to_embed = data.get('solution') or data.get('fact')
        if not to_embed:
            print("[SOLUTION MEMORY]: No 'solution' or 'fact' found in data, skipping add to memory.")
            return

        embedding = self.embedder.embed(to_embed)  # dovrebbe essere un vettore

        self.store.add(
            ids=[str(uuid.uuid4())],
            documents=[to_embed],
            embeddings=[embedding],
            metadatas=[data]
        )

        self.bm25_index.add([to_embed])  # meglio lista




    def search(self, query: str, k: int = 3):
        """
        Cerca i documenti più rilevanti per la query.
        """
        embedding = self.embedder.embed(query)
        results = self.store.search(embedding, k=k)

        return results
    
    def search_rrf(self, query: str, k: int = 3, rrf_k: int = 60):
        """
        Esegue la ricerca ibrida usando Reciprocal Rank Fusion.
        rrf_k: costante (default 60) per bilanciare l'influenza dei rank bassi.
        """
        # 1. Ottieni risultati da entrambi (prendine un po' più di 'k' per la fusione)
        num_candidates = k * 2
        vector_results = self.store.search(self.embedder.embed(query), k=num_candidates)
        bm25_results = self.bm25_index.search(query, k=num_candidates)

        # 2. Dizionario per accumulare i punteggi RRF
        # { "chunk_id": { "score": 0.0, "data": ... } }
        rrf_scores = {}

        # 3. Processa risultati Vettoriali
        for rank, res in enumerate(vector_results):
            # Assicurati di estrarre l'ID correttamente in base alla tua implementazione
            uid = res.get('metadata', {}).get('chunk_id') or res.get('id')
            if uid not in rrf_scores:
                rrf_scores[uid] = {"score": 0.0, "data": res}
            
            # Formula RRF: 1 / (k + rank)
            rrf_scores[uid]["score"] += 1.0 / (rrf_k + (rank + 1))

        # 4. Processa risultati BM25
        for rank, res in enumerate(bm25_results):
            uid = res.get('chunk_id')
            if uid not in rrf_scores:
                # Se non era nei vettoriali, lo aggiungiamo
                rrf_scores[uid] = {"score": 0.0, "data": res}
            
            rrf_scores[uid]["score"] += 1.0 / (rrf_k + (rank + 1))

        # 5. Ordina per punteggio RRF decrescente
        sorted_results = sorted(
            rrf_scores.values(), 
            key=lambda x: x["score"], 
            reverse=True
        )

        # Restituisci solo i dati dei primi k
        return [item["data"] for item in sorted_results[:k]]
    
    def reranked_search(self, query: str, k: int = 3):
        # 1. Ottieni i candidati dalla tua funzione RRF (prendine di più, es. 10-15)
        initial_results = self.search_rrf(query, k)
        
        # 2. Prepara le coppie (Query, Documento) per il reranker
        # Assumendo che 'data' contenga il testo del chunk
        pairs = [[query, res['text']] for res in initial_results]
        
        # 3. Calcola i punteggi di pertinenza reali
        scores = self.reranker.predict(pairs)
        
        # 4. Riallinea i punteggi ai risultati e ordina
        for i, res in enumerate(initial_results):
            res['rerank_score'] = scores[i]
            
        final_results = sorted(initial_results, key=lambda x: x['rerank_score'], reverse=True)
        
        # 5. Restituisci i top k finali
        return final_results[:k]

    def get_all(self):
        """
        Ritorna tutti i documenti presenti nella memoria.
        Utile per debug o per costruire un indice completo.
        """
        return self.store.get_all()

    def clean_all_data(self):
        """
        Cancella completamente tutti i dati della memoria.
        Utile quando usi una memoria persistente e vuoi resettarla.
        """
        
        self.store.clean_all_data()
        self.bm25_index.clean_all_data()



if __name__ == "__main__":
    from vector_store.vector_store import VectorStore
    from embeddings.embedding_model import EmbeddingModel
    from funes.Storage.rag_system.memory.bm25_index import BM25Index
    from funes.Storage.rag_system.chunker.semantic_chunker import LocalSemanticChunker
    from funes.Storage.rag_system.embeddings.sentence_transformer import SentenceTransformerEmbedding
    from vector_store.chroma_store import ChromaStore
    data = {'type': 'fact', 'context': 'user introduction', 'problem': None, 'solution': None, 'fact': "user's preferred name is Pappalardo", 'tags': ['user preference'], 'confidence': 1}
    embedder = SentenceTransformerEmbedding()
    kb_collection = ChromaStore(collection_name="knowledge_base_collection", persist_path="saved_data/chroma_kb")
    chunker = LocalSemanticChunker()
    bm25_index = BM25Index()
    memory = SolutionMemory(store=None, bm25_index=None, embedder=embedder)


    memory.add(data)

    search_results = memory.search("What is the user's preferred name?", k=3)
    print("Search results:", search_results)

