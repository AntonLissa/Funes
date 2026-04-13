
task_plan_Acq = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data examples\planning example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\OUTPUT\TASK_PLAN_ACQ_20260317.csv"
time_tagged_data = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data examples\planning example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\OUTPUT\IME01_24032026095915680_TIME_TAGGED.xml"
cmp_data = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data examples\planning example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\INPUT\IME01_PL_PPF_CMP_20260311T133622_20260318T000000_20260320T000000_DEV_001.xml"
orbit = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data examples\planning example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\INPUT\IME01_CTBL_20260316T000000_20260321T000000_001.json"

from datetime import datetime
import json
from funes.Storage.rag_system.chunker.semantic_chunker import LocalSemanticChunker
from funes.Storage.rag_system.embeddings.sentence_transformer import SentenceTransformerEmbedding
from funes.Storage.rag_system.memory.bm25_index import BM25Index
from funes.Storage.rag_system.memory.knowledge_base_memory import KBMemory
from funes.Storage.rag_system.vector_store.chroma_store import ChromaStore
from funes.utils.planning_correlator import get_csv_task_plan


class StorageManager:
    def __init__(self):
        self.storage = {}
        self.kb = self._init_kb()
        self.tags_time_tagged  = ["Mission", "PlanValidityTimeWindow", "Satellite", "Operation"]


    def _init_kb(self):
        bm25_index = BM25Index()
        embedder = SentenceTransformerEmbedding()
        kb_collection = ChromaStore(collection_name="knowledge_base_collection", persist_path="saved_data/chroma_kb")
        chunker = LocalSemanticChunker()
        kb_memory = KBMemory(store=kb_collection, bm25_index=bm25_index, embedder=embedder, chunker=chunker)
        return kb_memory
    

    def get_kb_results(self, query, search_k = 5, final_k = 3):
        search_results = self.kb.reranked_search(query, k=search_k)
        print("SM: risultati trovati:", len(search_results))
        return search_results[0:final_k]

    def get_data_for_planning(self):
        task_plan = self.get_planning_data()
        satellite_passages = self.get_orbit_from_json()

        return {
            "planning_data": self.get_planning_data(),
            "datetime": datetime.now().isoformat(),
            "satellite_passages": self.get_orbit_from_json(),
            "soe": None
        }

    def get_planning_data(self):
        task_path = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data_examples\planning_example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\OUTPUT\TASK_PLAN_NOMINAL_20260318.csv"
    
        return get_csv_task_plan(task_path, date_start="2026-03-18", date_end="2026-03-19", acquisition_filter=True)

    def get_orbit_from_json(self):
        json_path = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data_examples\planning_example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\INPUT\IME01_CTBL_20260316T000000_20260321T000000_001.json"
        with open(json_path, 'r') as f:
            data = json.load(f)
        return json.dumps(data, default=str, separators=(",", ":")) 
    

if __name__ == "__main__":
    storage_manager = StorageManager()
    kb_res  = storage_manager.get_kb_results("architecture and operational interfaces of FOS for HR-MS satellites in the IRIDE ground segment")

    for res in kb_res:
        metadata = res['metadata']
        print(f"Title: {metadata['title']}, page: {metadata['page_number']} \n {res['text']}")
