from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings

from funes.Storage.rag_system.chunker.base_chunker import BaseChunker
from pathlib import Path
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from funes.Storage.rag_system.chunker.base_chunker import BaseChunker
from funes.utils.utils import clean_documents
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    Docx2txtLoader,
    TextLoader
)

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
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=70
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

    def chunk(self, file_path: str) -> List[Document]:
        # 1. Caricamento e pulizia (usi i tuoi metodi già pronti)
        docs = self.load_document(file_path)
        docs_cleaned = clean_documents(docs)
        
        # 2. Uniamo le pagine per non rompere il contesto semantico tra p. 1 e p. 2
        full_text = "\n\n".join([d.page_content for d in docs_cleaned])
        
        # 3. Splitting Semantico
        # Crea i chunk basandosi sul "cambio di significato" invece che sui caratteri
        chunks = self.splitter.create_documents([full_text])
        
        # 4. Arricchimento metadata
        enriched_chunks = []
        for i, chunk in enumerate(chunks):
            metadata = docs[0].metadata.copy() # Prendiamo i metadati base
            metadata.update({
                "chunk_id": i,
                "chunk_size": len(chunk.page_content),
                "source": Path(file_path).name
            })
            enriched_chunks.append(Document(page_content=chunk.page_content, metadata=metadata))
            
        return enriched_chunks
    

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
        date = c.metadata.get('creationdate', 'Unknown Date')
        
        print(f"Title: {title} | ID: {chunk_id} | Size: {size} chars")
        print(c.page_content) # Stampo solo l'inizio per non intasare la console
        print("-" * 50)