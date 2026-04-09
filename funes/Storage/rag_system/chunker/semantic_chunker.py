import hashlib

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
    
    def chunk(self, file_path: str) -> List[Document]:
    

        print("- smart chunker: loading document and extracting metadata...")
        doc_info = self.get_pdf_info(file_path)

        source_name = Path(file_path).name
        doc_hash = hashlib.md5(source_name.encode()).hexdigest()[:8]

        print("- smart chunker: extracting pages with PyMuPDF4LLM...")
        raw_pages = pymupdf4llm.to_markdown(file_path, page_chunks=True)

        docs_to_clean = [
            Document(page_content=p["text"], metadata={"page": p.get("page", i + 1)})
            for i, p in enumerate(raw_pages)
        ]

        cleaned_docs = clean_documents(docs_to_clean)

        final_chunks = []

        for doc in cleaned_docs:
            page_num = doc.metadata.get("page", -1)

            page_chunks = self.splitter.split_text(doc.page_content)

            for i, chunk_text in enumerate(page_chunks):
                text = chunk_text.strip()

                if len(text) < 50 or len(text.split()) < 8:
                    continue

                normalized = " ".join(text.split())

                content_hash = hashlib.sha1(normalized.encode()).hexdigest()

                chunk_id = f"{doc_hash}_p{page_num}_c{i+1}"

                metadata = {
                    "chunk_id": chunk_id,
                    "content_hash": content_hash,
                    "source": source_name,
                    "title": doc_info.get("title") or "N/A",
                    "author": doc_info.get("author") or "N/A",
                    "last_modified": doc_info.get("modDate") or "N/A",
                    "page_number": page_num,
                    "chunk_index_in_page": i + 1,
                    "chunk_size": len(text),
                    "format": "markdown"
                }

                final_chunks.append(
                    Document(page_content=text, metadata=metadata)
                )

        return final_chunks

                


if __name__ == "__main__":
    # Inizializza il nuovo chunker semantico
    # Nota: la prima volta scaricherà il modello (~100MB), sii paziente.
    chunker = LocalSemanticChunker() 
    
    # Path del file (usa le raw string r"" per i path di Windows per evitare errori con i backslash)
    path_file = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data_examples\documenti\Annex 2 – FOS Architecture.pdf"
    
    # Chiamata al metodo chunk
    # Assicurati che nella classe il metodo si chiami 'chunk' e non 'chunk_file'
    chunks = chunker.chunk(path_file)

    print(f"\n--- Elaborazione completata: {len(chunks)} chunk generati ---\n")

    for c in chunks: 
        # Recuperiamo i metadata con dei fallback (None o "N/A") per evitare errori di stampa
        title = c.metadata.get('title', 'Unknown Title')
        author = c.metadata.get('author', 'Unknown Author')
        chunk_id = c.metadata.get('chunk_id')
        size = c.metadata.get('chunk_size')
        date = c.metadata.get('last_modified', 'Unknown Date')
        
        print(f"Title: {title} | ID: {chunk_id} | Author: {author} | Date: {date} |Size: {size} chars")
        print(c.page_content) # Stampo solo l'inizio per non intasare la console
        print("-" * 50)