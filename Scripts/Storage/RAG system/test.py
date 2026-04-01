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
from memory.solution_memory import SolutionMemory
from memory.document_memory import DocumentMemory
from vector_store.vector_store import VectorStore
from vector_store.chroma_store import ChromaStore
from retrieval.simple_retriever import SimpleRetriever
from retrieval.context_builder import ContextBuilder


# --- 1. Configurazione Embedding ---
# L'embedding model trasforma testi in vettori numerici per similarity search
embedder = SentenceTransformerEmbedding()


# --- 2. Configurazione VectorStore ---
# Qui useremo Chroma come DB vettoriale mockup
solution_store = ChromaStore(collection_name="solution_collection")
document_store = ChromaStore(collection_name="document_collection")


# --- 3. Creazione memorie ---
# SolutionMemory: salva problemi e soluzioni
solution_memory = SolutionMemory(store=solution_store, embedder=embedder)

# DocumentMemory: salva documenti generici
document_memory = DocumentMemory(store=document_store, embedder=embedder)


# --- 4. Popolamento delle memorie ---
solution_memory.add(
    problem="""
CI/CD pipeline fails during deploy stage with error:
'Missing required environment variable: APP_ENV'.
The issue appears only in the production workflow on GitHub Actions,
while staging works correctly. Logs show that the container starts
but the configuration loader crashes before initialization.
""",
    solution="""
Ensure that the APP_ENV variable is explicitly defined in the production
deployment step. In GitHub Actions add it under 'env' or pass it through
the deployment script. Example:

env:
  APP_ENV: production

Also verify that the Dockerfile does not override it with a default value.
"""
)

solution_memory.add(
    problem="""
Application intermittently fails to connect to PostgreSQL with timeout errors.
Stack trace indicates connection pool exhaustion and occasional DNS resolution
failures. The issue started after migrating the service to Kubernetes and
deploying multiple replicas.
""",
    solution="""
Check the database connection pool configuration and ensure that the max
connections allowed by PostgreSQL are not exceeded. Reduce pool size per pod
or introduce a connection proxy (e.g., PgBouncer).

Additionally verify Kubernetes DNS stability and ensure the DB hostname
resolves correctly inside the cluster.
"""
)

solution_memory.add(
    problem="""
API requests to the authentication service return HTTP 401 even with valid
JWT tokens. The tokens appear correct when decoded but the service logs
show 'invalid signature'. The problem appeared after rotating signing keys.
""",
    solution="""
Ensure the authentication service is using the updated public key for JWT
verification. If keys are fetched from a JWKS endpoint, verify the cache
expiration and force a refresh. Restart the service or clear the key cache
to ensure the new signing key is loaded.
"""
)



# --- 5. Configurazione Retriever ---
# Il retriever interroga tutte le memorie e restituisce risultati semantici
memories = [solution_memory, document_memory]
retriever = SimpleRetriever(memories=memories, top_k=1)


# --- 6. Configurazione ContextBuilder ---
# Costruisce il contesto da passare a un LLM
context_builder = ContextBuilder()


# --- 7. Funzione di test chatbot ---
def test_chatbot(query: str):
    """
    Simula il flusso di un chatbot RAG:
    1. Retrieval dai vari tipi di memoria
    2. Costruzione contesto
    3. (Qui non c'è LLM, stampiamo il contesto)
    """
    print(f"\n--- User query ---\n{query}\n")

    # Step 1: Retrieval dai diversi tipi di memoria
    retrieved_items = retriever.retrieve(query)

    # Step 2: Costruzione del contesto
    context = context_builder.build(retrieved_items)

    # Step 3: Mostriamo il contesto che verrebbe passato all'LLM
    print("--- Retrieved Context ---")
    print(context)


# --- 8. Test delle query ---
# Query che dovrebbe richiamare sia SolutionMemory che DocumentMemory
test_chatbot("Cosa devo fare se la pipeline fallisce perché manca una variabile?")

# Query che richiama DocumentMemory
test_chatbot("Come faccio il backup giornaliero del database?")

# Query che richiama SolutionMemory
test_chatbot("Database connection timeout error")
