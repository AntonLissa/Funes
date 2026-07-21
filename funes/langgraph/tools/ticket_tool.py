import datetime
import json
import time
from funes.Storage import storage_manager
from funes.utils.utils import remove_json_strings

from funes.langgraph.tools.base_tool import BaseTool


class TicketTool(BaseTool):
    def __init__(self, ticket_llm, storage_manager):
        self.ticket_llm = ticket_llm
        self.storage_manager = storage_manager

    @property
    def name(self):
        return "ticket_tool"

    def run(self, query):
        print(f"[TICKET LLM]: {query}")

        if not query:
            return "Ticket tool error: no query provided"


        # STEP 1: primo payload (senza dati specifici)
        payload = {
            "user_query": query,
            "tickets": self.storage_manager.get_tickets()
        }

        print(f"[TICKET LLM] payload: {payload}")
        llm_response = self.ticket_llm.speak(payload)
        
        tickets_found = llm_response
        return tickets_found
