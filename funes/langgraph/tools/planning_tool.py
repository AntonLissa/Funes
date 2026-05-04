import datetime
import json

from funes.langgraph.tools.base_tool import BaseTool


class PlanningTool(BaseTool):
    def __init__(self, planning_llm, storage_manager):
        self.planning_llm = planning_llm
        self.storage_manager = storage_manager

    @property
    def name(self):
        return "planning_tool"

    def run(self, conversation):

        if not conversation:
            return ""

        query = conversation[-1].content

        # STEP 1: primo payload (senza dati specifici)
        payload = {
            "planning_data": [],
            "datetime": datetime.datetime.now().isoformat(),
            "satellite_passages": None,
            "soe": None,
            "user_query": query,
        }

        llm_response = self.planning_llm.speak(payload)

        try:
            parsed = json.loads(llm_response)
        except Exception:
            # fallback: l’LLM ha deciso di fare arte invece che JSON
            return llm_response

        # STEP 2: se serve interrogare lo storage
        action = parsed.get("action")

        if action not in ["query_storage", "answer"]:
            return "Invalid LLM response format"
        
        if action == "query_storage":

            filters = self._map_parameters(parsed.get("parameters", {}))
            print(f"[PLANNING TOOL] Interrogazione storage con filtri: {filters}")
            data = self.storage_manager.get_data_for_planning(filters)
            return data
            '''print(f"[PLANNING TOOL] Dati ricevuti dallo storage: {data}")

            # STEP 3: seconda chiamata con dati veri
            payload.update(data)

            final_response = self.planning_llm.speak(payload)

            try:
                final_parsed = json.loads(final_response)
                return final_parsed.get("response", final_response)
            except Exception:
                return final_response

        # STEP 4: risposta diretta
        return parsed.get("response", llm_response)'''

    # -----------------------------
    # mapping LLM → storage layer
    # -----------------------------
    def _map_parameters(self, params):
        """
        Traduce i parametri dell'LLM nel formato atteso dallo storage.
        """


        return {
            "date_start": params.get("date_start"),
            "date_end": params.get("date_end"),
            "satellite": params.get("satellite"),
            "time": params.get("time"),
        }
