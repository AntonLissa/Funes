import datetime
import json
from funes.Storage import storage_manager
from funes.utils.utils import remove_json_strings

from funes.langgraph.tools.base_tool import BaseTool


class PlanningTool(BaseTool):
    def __init__(self, planning_llm, storage_manager):
        self.planning_llm = planning_llm
        self.storage_manager = storage_manager

    @property
    def name(self):
        return "planning_tool"

    def run(self, query):

        if not query:
            return "Planning tool error: no query provided"


        # STEP 1: primo payload (senza dati specifici)
        payload = {
            "user_query": query,
        }


        llm_response = self.planning_llm.speak(payload)

        try:
            parsed = json.loads(remove_json_strings(llm_response))
        except Exception:
            # fallback: l’LLM ha deciso di fare arte invece che JSON
            return llm_response

        start_date = parsed.get("date_start")
        end_date = parsed.get("date_end")
        satellite = parsed.get("satellite")
        station = parsed.get("station")
        print(f"[PLANNING TOOL] Parsed response from planning LLM: {parsed}")
        result = self.storage_manager.get_planning_data(date_start=start_date, date_end=end_date, satellite=satellite, station=station)

        print(f"[PLANNING TOOL] Retrieved data for planning: \n{result}")
        return result
