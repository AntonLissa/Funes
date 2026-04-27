import json

from funes.AIM.core.agent_factory import AgentFactory
from funes.Storage.storage_manager import StorageManager
from funes.langgraph.tools.base_tool import BaseTool


class LTMemoryTool(BaseTool):
    def __init__(self, lt_memory_llm, storage_manager):
        self.lt_memory_llm = lt_memory_llm
        self.storage_manager = storage_manager

    @property
    def name(self):
        return "long_term_memory_store_tool"

    def run(self, conversation):

        if not conversation:
            return "Error: no conversation provided to LTMemoryTool."


        history_messages = conversation[-10:] 

        history_text = "\n".join(
            f"{'User' if m.type == 'human' else 'Assistant'}: {m.content}"
            for m in history_messages
        )

        data = {
            "conversation_history": history_text
        }

        response = json.loads(self.lt_memory_llm.speak(data))
        if (response['type'] == 'fact' and response['fact'] is not None) or (response['type'] == 'solution' and response['solution'] is not None):
            print(f"[LT MEMORY TOOL] Saving to long term memory: {response}")
            self.storage_manager.save_to_long_term_memory(response)
            return "Data saved to long-term memory."
        return "No actionable information found to save to long-term memory."
