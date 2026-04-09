# test.py
"""
Esempio completo di uso del RAG system con:
- SolutionMemory: per problemi e soluzioni
- DocumentMemory: per documenti generici

Mostra:
1. come salvare dati
2. come fare retrieval
3. come costruire contesto per LLM
"""

from embeddings.sentence_transformer import SentenceTransformerEmbedding
from funes.Storage.rag_system.chunker.semantic_chunker import LocalSemanticChunker
from funes.Storage.rag_system.memory.knowledge_base_memory import KBMemory
from vector_store.chroma_store import ChromaStore
from retrieval.simple_retriever import SimpleRetriever

import os

def get_file_paths(folder_path):
    file_paths = []
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_paths.append(os.path.join(root, file))
    
    return file_paths

# --- 1. Configurazione Embedding ---
# L'embedding model trasforma testi in vettori numerici per similarity search
embedder = SentenceTransformerEmbedding()


# --- 2. Configurazione Store ---
kb_collection = ChromaStore(collection_name="knowledge_base_collection", persist_path="saved_data/chroma_kb")


# --- 3. Creazione memorie ---
# SolutionMemory: salva problemi e soluzioni
chunker = LocalSemanticChunker()
kb_memory = KBMemory(store=kb_collection, embedder=embedder, chunker=chunker)

# --- 4. Popolamento delle memorie ---

for path in get_file_paths(r"C:\Users\anton\Documents\python projects\FUNES\Funes\data_examples\documenti"):
    print(f"\n--- Aggiungo documento alla KB: {path} ---")
    kb_memory.add(path)
all_data = kb_collection.get_all()

print("-"*10, f"Total chunks in KB: {len(all_data)}", "-"*10)

while True:
    result = kb_memory.search(input(">> Inserisci ricerca:"), k=3)
    print("\n\nRAG Search Results:")
    for i, res in enumerate(result):
        print(f" [SCORE: {res['score']:.2f}] Title:{res['metadata']['title']} Page: {res['metadata']['page_number']} \n{res['text']} \n", "_"*50)
