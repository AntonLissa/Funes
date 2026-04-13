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
from funes.Storage.rag_system.memory.bm25_index import BM25Index
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

def load_folder(path):
    embedder = SentenceTransformerEmbedding()
    kb_collection = ChromaStore(collection_name="knowledge_base_collection", persist_path="saved_data/chroma_kb")
    chunker = LocalSemanticChunker()
    bm25_index = BM25Index()
    kb_memory = KBMemory(store=kb_collection, bm25_index=bm25_index, embedder=embedder, chunker=chunker)
    kb_memory.clean_all_data()

    cont = 0
    files = get_file_paths(path)
    total = len(files)
    for file_path in files:
        cont += 1
        title = os.path.basename(file_path)
        print(f"\n--- Aggiungo documento alla KB {cont} / {total}: {title} ")
        kb_memory.add(file_path)


def load_jsonl_test():
    import json
    # esempio di caricamento da JSON (simulato)
    with open(r"C:\Users\anton\Documents\python projects\FUNES\Funes\funes\Storage\rag_system\rag_eval_dataset.jsonl", "r") as f:
        data = [json.loads(line) for line in f]
    return data

def run_retrieval_test(rrf = False):
    recall5 = 0
    mrr = 0
    bm25_index = BM25Index()
    questions = load_jsonl_test()
    embedder = SentenceTransformerEmbedding()
    kb_collection = ChromaStore(collection_name="knowledge_base_collection", persist_path="saved_data/chroma_kb")
    chunker = LocalSemanticChunker()
    kb_memory = KBMemory(store=kb_collection, bm25_index=bm25_index, embedder=embedder, chunker=chunker)
    position = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    wrong_counter = 0
    for question in questions:
        if rrf:
            search_results = kb_memory.search_rrf(question['question'], k=5)
        else:
            search_results = kb_memory.search(question['question'], k=5)
        document_title = question['document']
        document_page = question['page']
        for result in search_results:
            title_result = result['metadata']['title']
            page_result = result['metadata']['page_number']
            
            if ((title_result == document_title) and (page_result == document_page)):
                recall5 += 1
                mrr += 1 / (search_results.index(result) + 1)
                position[search_results.index(result) + 1] += 1
                break

    return recall5, mrr, position
       


# Save all data
#load_folder(r"C:\Users\anton\Documents\python projects\FUNES\Funes\data_examples\documenti")


kb_collection = ChromaStore(collection_name="knowledge_base_collection", persist_path="saved_data/chroma_kb")
print(f"-- Testing on {len(kb_collection.get_all())} embeddings --")

recall, mrr, position = run_retrieval_test(rrf=True)
print("TEST RRF")
print(f"Results: Recall@5: {recall}, MRR: {mrr}")
print(f"Position distribution: {position}")



recall, mrr, position = run_retrieval_test(rrf=False)
print("TEST SOLO VECTOR DB:")
print(f"Results: Recall@5: {recall}, MRR: {mrr}")
print(f"Position distribution: {position}")