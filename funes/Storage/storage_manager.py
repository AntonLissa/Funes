
task_plan_Acq = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data examples\planning example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\OUTPUT\TASK_PLAN_ACQ_20260317.csv"
time_tagged_data = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data examples\planning example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\OUTPUT\IME01_24032026095915680_TIME_TAGGED.xml"
cmp_data = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data examples\planning example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\INPUT\IME01_PL_PPF_CMP_20260311T133622_20260318T000000_20260320T000000_DEV_001.xml"
orbit = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data examples\planning example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\INPUT\IME01_CTBL_20260316T000000_20260321T000000_001.json"

from datetime import datetime
import json

import numpy as np
import pandas as pd
from funes.Storage.chat_storage.chat_storage import ChatStorage
from funes.Storage.rag_system.chunker.semantic_chunker import LocalSemanticChunker
from funes.Storage.rag_system.embeddings.sentence_transformer import SentenceTransformerEmbedding
from funes.Storage.rag_system.memory.bm25_index import BM25Index
from funes.Storage.rag_system.memory.knowledge_base_memory import KBMemory
from funes.Storage.rag_system.vector_store.chroma_store import ChromaStore
from funes.utils.planning_correlator import get_all_plans, get_csv_task_plan, get_passages_from_xml

class StorageManager:
    def __init__(self, light_mode = True):
        self.storage = {}
        self.light_mode = light_mode
        if not light_mode:
            self.kb = self._init_kb()
        self.chat = ChatStorage( )
        self.tags_time_tagged  = ["Mission", "PlanValidityTimeWindow", "Satellite", "Operation"]



    def _init_kb(self):
        bm25_index = BM25Index()
        embedder = SentenceTransformerEmbedding()
        kb_collection = ChromaStore(collection_name="knowledge_base_collection", persist_path="saved_data/chroma_kb")
        chunker = LocalSemanticChunker()
        kb_memory = KBMemory(store=kb_collection, bm25_index=bm25_index, embedder=embedder, chunker=chunker)
        return kb_memory
    

    def save_to_long_term_memory(self, data):
        # Here you would implement the logic to save the data to your long-term storage solution.
        # This could be a database, a file system, or any other storage mechanism you choose.
        # For demonstration purposes, we'll just print the data to the console.
        print(f"Saving to long-term memory: {data}")

    def get_kb_results(self, query, search_k = 5, final_k = 3):
        if self.light_mode: return ''
        search_results = self.kb.reranked_search(query, k=search_k)
        return search_results[0:final_k]

    def get_data_for_planning(self, filters=None):

        filters = filters or {}

        planning_data = self.get_planning_data(
            date_start=filters.get("date_start"),
            date_end=filters.get("date_end"),
            satellite=filters.get("satellite"),
        )
        
        return {
            "planning_data": planning_data,
            "datetime": datetime.now().isoformat(),
            "satellite_passages": "",
            "soe": ""
        }

    def get_planning_data(self, date_start=None, date_end=None, satellite=None, station=None):
        return get_all_plans(date_start=date_start, date_end=date_end, satellite=satellite, station=station)
    
    def get_orbit_from_json(self):
        json_path = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data_examples\planning_example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\INPUT\IME01_CTBL_20260316T000000_20260321T000000_001.json"
        with open(json_path, 'r') as f:
            data = json.load(f)
        return json.dumps(data, default=str, separators=(",", ":")) 
    

    # TICKET FUNCTIONALITIES
    def get_tickets(self):
        # Implement logic to create a ticket in your ticketing system
        ticket_list = pd.read_excel(r"C:\Users\anton\Documents\python projects\FUNES\Funes\data_examples\ticket\Ticket_MOC.xls")
        # return 5 random tickets with seed for reproducibility
        np.random.seed(19)
        ticket_list = ticket_list.sample(5)
        ticket_list = ticket_list[["Code", "Title", "Creation Date", "Description", "Status"]]
        # add a fake ticket
        fake_ticket = pd.DataFrame({
            "Code": ["T001725"],
            "Title": ["Antenna malfunction"],
            "Creation Date": ["2026-03-15"],
            "Description": ["Antenna malfunction detected in station A40P. Based on current telemetry and physical inspection requirements, the antenna will remain degraded or completely unavailable for at least the next 2 hours. This will impact all planned acquisitions for the next 2 hours. The issue is currently being investigated by the engineering team, and updates will be provided as soon as more information is available."],
            "Status": ["Open"]
        })

        ticket_list = pd.concat([ticket_list, fake_ticket], ignore_index=True)

        return ticket_list.to_dict(orient="records")
    
    # CHAT FUNCTIONALITIES
    def create_chat(self, chat_id, user_id, agent):
        return  self.chat.create_chat(chat_id, user_id, agent)

    def save_message(self, chat_id, user_id, role, content):
         self.chat.save_message(chat_id, user_id, role, content)

    def list_user_chats(self, user_id):
        return  self.chat.list_user_chats(user_id)

    def get_chat_messages(self, chat_id):
        return  self.chat.get_messages(chat_id)
    

if __name__ == "__main__":
    storage_manager = StorageManager(light_mode=True)
    data = storage_manager.get_data_for_planning({
        "date_start": "2026-03-17",
        "date_end": "2026-03-18",
        "satellite": None})
    
    print(data)