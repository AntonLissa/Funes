import hashlib
import os

from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
import re
from funes.Storage.rag_system.chunker.base_chunker import BaseChunker
from pathlib import Path
from typing import List
from funes.Storage.rag_system.chunker.base_chunker import BaseChunker
from funes.utils.utils import clean_documents
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    PyMuPDFLoader,
    UnstructuredPDFLoader,
    Docx2txtLoader,
    TextLoader
)
from unstructured.partition.pdf import partition_pdf
import fitz
import pymupdf4llm
from funes.utils.utils import get_repetitive_patterns, similar

class LocalSemanticChunker(BaseChunker):
    def __init__(self):
        # Inizializza gli embeddings in locale
        # Questo scaricherà il modello (~100MB) la prima volta
        print("- smart chunker: loading local embedding model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'} # o 'cuda' se hai una GPU
        )
        
        # Inizializza lo splitter semantico
        self.splitter = SemanticChunker(
            self.embeddings,
            # 'percentile' divide dove la distanza tra frasi è nel top X%
            # 'gradient' guarda dove il cambio di argomento è più brusco
            # 'standard_deviation' guarda dove la distanza è significativamente più alta della media
            breakpoint_threshold_type="standard_deviation",
            breakpoint_threshold_amount=1.5, # più alto = chunk più grandi, più basso = chunk più piccoli
            buffer_size=5, # per evitare chunk troppo piccoli
            add_start_index=True
        )
    
    def load_document(self, file_path: str) -> List[Document]:
        ext = Path(file_path).suffix.lower()

        if ext == ".pdf":
            loader = PyMuPDFLoader(file_path)
        elif ext == ".docx":
            loader = Docx2txtLoader(file_path)
        elif ext == ".txt":
            loader = TextLoader(file_path)
        else:
            raise ValueError(f"Formato non supportato: {ext}")

        return loader.load()
    
    def get_pdf_info(self, file_path):
        doc = fitz.open(file_path)
        metadata = doc.metadata  # Dizionario con title, author, creationDate, modDate, etc.
        doc.close()
        return metadata
    

    def chunk(self, file_path: str, sample_n: int = 10):
        print("- SEMANTIC CHUNKER: initializing metadata and sampling...")
        doc_info = self.get_pdf_info(file_path)
        source_name = Path(file_path).name
        doc_hash = hashlib.md5(source_name.encode()).hexdigest()[:8]

        # 1. FASE DI CAMPIONAMENTO (per trovare header/footer)
        # Estraiamo le pagine necessarie per il confronto
        all_raw_pages = pymupdf4llm.to_markdown(file_path, page_chunks=True)
        
        # Gestiamo il caso in cui il documento sia più corto del campione
        sample_limit = min(sample_n, len(all_raw_pages))
        sample_pages_text = [p["text"] for p in all_raw_pages[:sample_limit]]
        
        print(f"- SEMANTIC CHUNKER: scanning first {sample_limit} pages for noise...")
        # Troviamo i pattern ripetitivi usando la tua funzione logica
        # Nota: passiamo solo i testi, non i Document
        repetitive_patterns = get_repetitive_patterns(sample_pages_text) 

        print(f"- SEMANTIC CHUNKER: processing full document...")

        # 2. FASE DI GENERAZIONE
        for i, p in enumerate(all_raw_pages):
            page_num = p.get("page", i + 1)
            raw_text = p["text"]

            # Applichiamo la rimozione dei pattern ripetitivi alla pagina corrente
            lines = raw_text.splitlines()
            cleaned_lines = []
            for line in lines:
                line_s = line.strip()
                # Se la linea è simile a uno dei pattern trovati, la scartiamo
                if any(similar(line_s, p_rep) >= 0.95 for p_rep in repetitive_patterns):
                    continue
                cleaned_lines.append(line)
            
            clean_page_text = "\n".join(cleaned_lines)

            # Integriamo con la tua funzione clean_documents per la pulizia finale (spazi, etc)
            temp_doc = Document(page_content=clean_page_text, metadata={"page": page_num})
            final_clean_docs = clean_documents([temp_doc])
            
            if not final_clean_docs:
                continue
                
            page_text_for_splitting = final_clean_docs[0].page_content

            # 3. SPLITTING SEMANTICO
            page_chunks = self.splitter.split_text(page_text_for_splitting)

            for j, chunk_text in enumerate(page_chunks):
                text = chunk_text.strip()

                if len(text) < 50 or len(text.split()) < 8:
                    continue

                normalized = " ".join(text.split())
                content_hash = hashlib.sha1(normalized.encode()).hexdigest()
                chunk_id = f"{doc_hash}_p{page_num}_c{j+1}"

                # Tutti i tuoi metadati preservati
                metadata = {
                    "chunk_id": chunk_id,
                    "content_hash": content_hash,
                    "source": source_name,
                    "title": doc_info.get("title") or "N/A",
                    "author": doc_info.get("author") or "N/A",
                    "last_modified": doc_info.get("modDate") or "N/A",
                    "page_number": page_num,
                    "chunk_index_in_page": j + 1,
                    "chunk_size": len(text),
                    "format": "markdown"
                }

                yield Document(page_content=text, metadata=metadata)       


if __name__ == "__main__":
    # Inizializza il nuovo chunker semantico
    # Nota: la prima volta scaricherà il modello (~100MB), sii paziente.
    os.environ["TRANSFORMERS_VERBOSITY"] = "error"
    chunker = LocalSemanticChunker() 
    
    # Path del file (usa le raw string r"" per i path di Windows per evitare errori con i backslash)
    path_file = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data_examples\documenti\Annex 2 – FOS Architecture.pdf"
    
    count = 0
    # Iteriamo direttamente sul generatore
    for c in chunker.chunk(path_file):
        count += 1
        chunk_id = c.metadata.get('chunk_id')
        size = c.metadata.get('chunk_size')

        print("title:", c.metadata.get('title'))
        
        # Stampiamo un feedback rapido per ogni chunk prodotto
        #print(f"Generato Chunk {count} | ID: {chunk_id} | Size: {size} chars | Content: {c.page_content[:100]}...{c.page_content[-100:]}")
        
        # Se vuoi vedere il testo (solo primi 100 caratteri per non intasare):
        # print(f"Content: {c.page_content[:100]}...")