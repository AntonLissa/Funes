from langgraph.graph import StateGraph, END

from funes.AIM.core.agent_factory import AgentFactory
from funes.langgraph.graph.agent_state import AgentState
from funes.Storage.storage_manager import StorageManager
from funes.langgraph.nodes.graph_nodes import GraphNodes
from funes.langgraph.tools.knowledge_base_tool import KnowledgeBaseTool
from funes.langgraph.tools.lt_memory_tool import LTMemoryTool
from funes.langgraph.tools.tool_executor import ToolExecutor
from funes.AIM.config.config_loader import ConfigLoader
from funes.AIM.core.agent_factory import AgentFactory
from funes.AIM.llm.provider.groq_provider import GroqProvider
from funes.Storage.storage_manager import StorageManager
import funes.AIM.core.register_agents
from funes.AIM.core.agent_registry import registry
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from funes.langgraph.tools.planning_tool import PlanningTool

class GraphEngine:
    def __init__(self, factory, storage_manager):
        self.factory = factory
        self.storage_manager = storage_manager
        
        # 1. Creiamo gli agenti necessari al grafo
        self.llms = {
            "master": self.factory.create_agent("master"),
            "kb": self.factory.create_agent("kb"),
            "query": self.factory.create_agent("query"),
            "planning": self.factory.create_agent("planning"),
            "lt_memory": self.factory.create_agent("long_term_memory")
        }

        # 2. Setup dei Tool
        self.tool_executor = ToolExecutor()
        kb_tool = KnowledgeBaseTool(
            query_llm=self.llms["query"],
            kb_llm=self.llms["kb"],
            storage_manager=self.storage_manager
        )
        self.tool_executor.register(kb_tool)

        planning_tool = PlanningTool(planning_llm=self.llms["planning"], storage_manager=self.storage_manager)
        self.tool_executor.register(planning_tool)

        lt_memory_tool = LTMemoryTool(lt_memory_llm=self.llms["lt_memory"], storage_manager=self.storage_manager)
        self.tool_executor.register(lt_memory_tool)

        # 3. Setup dei Nodi (usando la tua classe GraphNodes)
        self.nodes = GraphNodes(self.llms, self.tool_executor)

        # 4. Costruzione del Grafo
        self.app = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        #workflow.add_node("dispatcher", self.nodes.dispatcher_node)
        workflow.add_node("agent", self.nodes.master_node)
        workflow.add_node("tools", self.nodes.tool_node)

        workflow.set_entry_point("agent")

        workflow.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "call_tools": "tools",
                "final": END
            }
        )

        workflow.add_edge("tools", "agent")

        memory = MemorySaver()

        return workflow.compile(checkpointer=memory)

    def run(self, user_query: str, chat_id: str):

        initial_state = {
            "messages": [HumanMessage(content=user_query)],
            "tools_to_call": [],
            "tool_results": {},
            "investigation_state": {},
            "final_answer": "",
            "iteration": 0
        }

        final_state = self.app.invoke(
            initial_state,
            config={"configurable": {"thread_id": chat_id}}
        )

        return final_state["messages"][-1].content
    
    def load_chat_state(self, chat_id, messages):
        self.app.update_state(
            config={"configurable": {"thread_id": chat_id}},
            values={"messages": messages}
        )
    
    def should_continue(self, state: AgentState):
        print('Checking if should continue with tools', state.get("tools_to_call", []))
        if state.get("tools_to_call") and state["iteration"] < 3:
            return "call_tools"
 
        return "final"



if __name__ == '__main__':
    print("--- [INIT] Avvio Infrastruttura funes ---")

    # 1. Setup Infrastruttura di base (Dependency Injection)
    config_loader = ConfigLoader()
    api_key = config_loader.load_api_key()
    provider = GroqProvider(api_key)
    
    # Factory per creare gli agenti
    factory = AgentFactory(
        registry=registry, 
        config_loader=config_loader, 
        provider=provider
    )
    
    # Manager per il database/vettore
    storage_manager = StorageManager(light_mode=False)

    # 2. Inizializzazione del GraphEngine
    # Questo passaggio crea gli LLM, registra i Tool e compila il Grafo
    engine = GraphEngine(factory, storage_manager)
    
    print("--- [READY] Sistema pronto. Scrivi 'exit' per uscire. ---")

    # 3. Loop di interazione (Simula le chiamate API di Flask)
    while True:
        user_input = input("\nUtente >>> ")
        
        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            # L'unica riga necessaria per far girare tutta la logica LangGraph
            risposta_finale = engine.run(user_input, chat_id="test_chat_1")
            
            print(f"\nAssistant AI >>> {risposta_finale}")
            
        except Exception as e:
            print(f"Errore durante l'esecuzione del grafo: {e}")