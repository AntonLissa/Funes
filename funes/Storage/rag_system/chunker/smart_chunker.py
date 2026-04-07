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

class SmartChunker(BaseChunker):

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True,
            separators=[
                "\n\n", ". ", ""
            ]
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
        # 1. Carica documento
        docs = self.load_document(file_path)

        # 2. Pulisci da testi ripetitivi
        docs_cleaned = clean_documents(docs)

        # 3. Chunking
        chunks = self.splitter.split_documents(docs_cleaned)

        # 4. Enrichment dei metadata
        enriched_chunks = []
        for i, chunk in enumerate(chunks):
            metadata = chunk.metadata.copy()
            metadata.update({
                "chunk_id": i,
                "chunk_size": len(chunk.page_content),
                "page": metadata.get("page", None),
                "source": Path(file_path).name  # meglio usare solo nome file
            })
            enriched_chunks.append(Document(page_content=chunk.page_content, metadata=metadata))

        return enriched_chunks


if __name__ == "__main__":

    '''
    {'producer': 'Microsoft® Word per Microsoft 365', 
    'creator': 'Microsoft® Word per Microsoft 365', 
    'creationdate': '2022-11-04T13:45:02+01:00', 
    'title': 'FOS Architecture', 
    'author': 'Massimo Vitta', 
    'total_pages': 5, 
    'page': 0, 
    'page_label': '1', 
    'chunk_id': 1, 
    'chunk_size': 187}
    '''


    # test
    chunker = SmartChunker()
    chunks = chunker.chunk(r"C:\Users\anton\Documents\python projects\FUNES\Funes\data_examples\documenti\Annex 2 – FOS Architecture.pdf")

    for c in chunks: 
        print(f"\n Title: {c.metadata.get('title')}, Author: {c.metadata.get('author')}, Chunk ID: {c.metadata.get('chunk_id')},  Size: {c.metadata.get('chunk_size')}, Date: {c.metadata.get('creationdate')}\n")
        print(c.page_content)
        print("----")