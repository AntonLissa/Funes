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
from funes.Storage.rag_system.chunker.smart_chunker import SmartChunker
from memory.solution_memory import SolutionMemory
from funes.Storage.rag_system.memory.knowledge_base_memory import KBMemory
from vector_store.vector_store import VectorStore
from vector_store.chroma_store import ChromaStore
from retrieval.simple_retriever import SimpleRetriever
from retrieval.context_builder import ContextBuilder


test_string = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse maximus semper libero varius porta. Morbi metus massa, rhoncus a sem bibendum, auctor pellentesque ex. Aliquam efficitur dui at eros convallis pellentesque. Praesent ullamcorper mauris orci, quis bibendum tellus fringilla ut. Integer a sodales est, lacinia tempor mauris. Etiam sit amet magna ac ipsum placerat lacinia. Aenean nec semper dui, ut imperdiet diam. Fusce ut mauris maximus, tempor nunc id, euismod ex. In ornare imperdiet erat euismod congue. Proin ac ante vel nisi mollis ultricies. Mauris lacinia pulvinar dui. Nam tristique sagittis ex, eget pulvinar justo auctor vel. Suspendisse pretium metus eu libero lacinia accumsan. Aenean feugiat enim purus, vestibulum fermentum risus blandit vitae.

Curabitur convallis finibus fringilla. Cras vel diam sagittis, condimentum lorem vel, consectetur velit. Sed ullamcorper, turpis quis dignissim sollicitudin, felis erat laoreet sapien, dignissim fringilla orci quam in nisi. Pellentesque sit amet facilisis nulla, in scelerisque lorem. Morbi lacus turpis, feugiat vitae leo sit amet, rutrum viverra mi. Donec condimentum, magna rutrum malesuada tincidunt, est justo rutrum augue, eget elementum neque tellus quis diam. Proin mollis sagittis odio id fermentum. Ut vel cursus odio. Maecenas luctus ultricies justo, ut pharetra ex aliquam eu. Etiam aliquam pharetra est vel accumsan. Integer tristique nec purus sit amet tincidunt. Vivamus porttitor dolor id ante suscipit blandit. Donec volutpat erat vitae metus condimentum, eu faucibus ex scelerisque. Aliquam sagittis, urna vitae imperdiet imperdiet, leo felis aliquam ipsum, nec sagittis lacus justo sed augue."""


# --- 1. Configurazione Embedding ---
# L'embedding model trasforma testi in vettori numerici per similarity search
embedder = SentenceTransformerEmbedding()


# --- 2. Configurazione Store ---
kb_collection = ChromaStore(collection_name="knowledge_base_collection")


# --- 3. Creazione memorie ---
# SolutionMemory: salva problemi e soluzioni
chunker = SmartChunker()
kb_memory = KBMemory(store=kb_collection, embedder=embedder, chunker=chunker)

# --- 4. Popolamento delle memorie ---
kb_memory.add(
    doc_id="doc_1",
    text=test_string,
    metadata={"category": "test", "subsystem": "test"}
)


print(kb_memory.get_all())
