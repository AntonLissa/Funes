import datetime

from funes.AIM.core.agent_factory import AgentFactory
from funes.Storage.storage_manager import StorageManager
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

        planning_data = self.storage_manager.get_data_for_planning()
        print(f"[PLANNING DATA]:\n {planning_data}")
        planning_data['user_query'] = query
        

        return self.planning_llm.speak(planning_data)
