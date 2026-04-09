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
path_file = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data_examples\documenti\Annex 2 – FOS Architecture.pdf"
#kb_memory.add(path_file)


all_data = kb_collection.get_all()

print(f"Total chunks in KB: {len(all_data)}")
print("Sample chunk metadata:")
for elem in all_data:
    print(f"Metadata: {elem['text']}")
    print("-"*50)

result = kb_memory.search("What is the moc?", k=3)
print("\n\nRAG Search Results:")
for i, res in enumerate(result):
    print(f" [SCORE: {res['score']:.2f}]\n{res['text']} \n", "_"*50)
