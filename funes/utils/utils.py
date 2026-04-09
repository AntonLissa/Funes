import json
import re
from langchain_core.documents import Document

def print_json(data):
    obj = json.loads(data)

    print(json.dumps(obj, indent=2))


from difflib import SequenceMatcher
from typing import List

def similar(a: str, b: str) -> float:
    """Ritorna la similarità tra 0 e 1"""
    return SequenceMatcher(None, a, b).ratio()

def clear_repetitive_stuff(pages: List[str], similarity_threshold: float = 0.95, verbose: bool = False) -> List[str]:
    """
    Rimuove testi ripetitivi tra le pagine (es. header/footer, tabelle ricorrenti)
    Args:
        pages: lista di stringhe, una per pagina
        similarity_threshold: soglia di similarità per considerare testo ripetitivo
        verbose: se True, stampa i pattern ripetitivi trovati
    Returns:
        Lista di pagine ripulite
    """
    cleaned_pages = []
    repetitive_patterns = set()
    
    # Step 1: crea lista di blocchi da ogni pagina (puoi usare righe o paragrafi)
    page_blocks = [page.splitlines() for page in pages]

    # Step 2: cerca blocchi ripetitivi
    for i, blocks_i in enumerate(page_blocks):
        new_blocks = []
        for block in blocks_i:
            block_clean = block.strip()
            if not block_clean:
                continue

            # confronta con tutte le altre pagine
            is_repetitive = False
            for j, blocks_j in enumerate(page_blocks):
                if i == j:
                    continue
                for b in blocks_j:
                    if similar(block_clean, b.strip()) >= similarity_threshold:
                        is_repetitive = True
                        repetitive_patterns.add(block_clean)
                        break
                if is_repetitive:
                    break

            if not is_repetitive:
                new_blocks.append(block_clean)

        cleaned_pages.append("\n".join(new_blocks))
    
    if verbose:
        print("Pattern ripetitivi trovati e rimossi:")
        for p in repetitive_patterns:
            print(f"- {p}\n")

    return cleaned_pages


def clean_documents(docs: List[Document]) -> List[Document]:
        """
        Applica clear_repetitive_stuff a ciascun documento.
        Funziona pagina per pagina.
        """
        pages = [doc.page_content for doc in docs]
        cleaned_pages = clear_repetitive_stuff(pages, similarity_threshold=0.95)

        # ricostruisci Document con stesso metadata
        cleaned_docs = []
        for doc, text in zip(docs, cleaned_pages):
            cleaned_docs.append(Document(page_content=text, metadata=doc.metadata))
        return cleaned_docs
def get_repetitive_patterns(pages: List[str], similarity_threshold: float = 0.95) -> set:
    """
    Analizza un gruppo di pagine per trovare blocchi che si ripetono.
    """
    repetitive_patterns = set()
    page_blocks = [page.splitlines() for page in pages]

    for i, blocks_i in enumerate(page_blocks):
        for block in blocks_i:
            block_clean = block.strip()
            if not block_clean or len(block_clean) < 10: # Evita di eliminare linee troppo corte
                continue

            # Confronta con le altre pagine nel campione
            for j, blocks_j in enumerate(page_blocks):
                if i == j: continue
                if any(similar(block_clean, b.strip()) >= similarity_threshold for b in blocks_j):
                    repetitive_patterns.add(block_clean)
                    break
    return repetitive_patterns

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()