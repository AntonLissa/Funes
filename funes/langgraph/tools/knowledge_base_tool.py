from funes.AIM.core.agent_factory import AgentFactory
from funes.Storage.storage_manager import StorageManager
from funes.langgraph.tools.base_tool import BaseTool


class KnowledgeBaseTool(BaseTool):
    def __init__(self, query_llm, kb_llm, storage_manager):
        self.query_llm = query_llm
        self.kb_llm = kb_llm
        self.storage_manager = storage_manager

    @property
    def name(self):
        return "knowledge_base_tool"

    def run(self, conversation):

        if not conversation:
            return ""

        query = conversation[-1].content

        history_messages = conversation[-7:-1]  # ultimi 3 scambi

        history_text = "\n".join(
            f"{'User' if m.type == 'human' else 'Assistant'}: {m.content}"
            for m in history_messages
        )

        data = {
            "user_query": query,
            "conversation_history": history_text
        }

        query_enhanced = self.query_llm.speak(data)

        rag_data = self.storage_manager.get_kb_results(query_enhanced)

        data = {
            "rag_data": rag_data,
            "conversation_history": history_text,
            "user_query": query
        }

        return self.kb_llm.speak(data)
