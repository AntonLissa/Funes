import pickle
import os
import re
from rank_bm25 import BM25Okapi
import numpy as np

class BM25Index:
    def __init__(self, storage_path="data/bm25_index.pkl"):
        self.storage_path = storage_path
        self.corpus = []       
        self.doc_ids = []      
        self.metadatas = []    
        self.doc_ids_set = set() 
        self.bm25 = None
        
        self._load()

    # ... (metodi _preprocess, _save, _load, add, search identici a prima)

    def clean_all_data(self):
        """
        Cancella completamente l'indice sia dalla memoria che dal disco.
        """
        # 1. Svuota le strutture dati in memoria
        self.corpus = []
        self.doc_ids = []
        self.metadatas = []
        self.doc_ids_set = set()
        self.bm25 = None
        
        # 2. Elimina il file fisico dal disco se esiste
        if os.path.exists(self.storage_path):
            try:
                os.remove(self.storage_path)
                print(f"BM25: File {self.storage_path} eliminato con successo.")
            except Exception as e:
                print(f"BM25: Errore durante l'eliminazione del file: {e}")
        
        print("BM25: Indice completamente resettato.")

    # Riporto qui per comodità i metodi aggiornati nel messaggio precedente:
    
    def _preprocess(self, text):
        return re.findall(r"\b\w+\b", text.lower())

    def _save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        data = {
            "corpus": self.corpus,
            "doc_ids": self.doc_ids,
            "metadatas": self.metadatas
        }
        with open(self.storage_path, "wb") as f:
            pickle.dump(data, f)
        print(f"BM25: Indice salvato.")

    def _load(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "rb") as f:
                data = pickle.load(f)
                self.corpus = data.get("corpus", [])
                self.doc_ids = data.get("doc_ids", [])
                self.metadatas = data.get("metadatas", [])
                self.doc_ids_set = set(self.doc_ids)
            
            if self.corpus:
                tokenized_corpus = [self._preprocess(doc) for doc in self.corpus]
                self.bm25 = BM25Okapi(tokenized_corpus)

    def add(self, new_chunks):
        added_count = 0
        for chunk in new_chunks:
            c_id = chunk.metadata.get('chunk_id')
            if c_id not in self.doc_ids_set:
                self.corpus.append(chunk.page_content)
                self.doc_ids.append(c_id)
                self.metadatas.append(chunk.metadata)
                self.doc_ids_set.add(c_id)
                added_count += 1
        
        if added_count > 0:
            tokenized_corpus = [self._preprocess(doc) for doc in self.corpus]
            self.bm25 = BM25Okapi(tokenized_corpus)
            self._save()

    def search(self, query: str, k: int = 3):
        if not self.bm25 or not self.corpus:
            return []
        tokenized_query = self._preprocess(query)
        scores = self.bm25.get_scores(tokenized_query)
        top_n = np.argsort(scores)[::-1][:k]
        results = []
        for i in top_n:
            if scores[i] > 0:
                results.append({
                    "chunk_id": self.doc_ids[i],
                    "text": self.corpus[i],
                    "metadata": self.metadatas[i],
                    "score": scores[i]
                })
        return results