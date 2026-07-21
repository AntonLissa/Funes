from langgraph.graph import StateGraph, END

from funes.AIM.core.agent_factory import AgentFactory
from funes.langgraph.graph.agent_state import AgentState
from funes.Storage.storage_manager import StorageManager
from funes.langgraph.nodes.graph_nodes import GraphNodes
from funes.langgraph.tools.knowledge_base_tool import KnowledgeBaseTool
from funes.langgraph.tools.lt_memory_tool import LTMemoryTool
from funes.langgraph.tools.network_tool import NetworkTool
from funes.langgraph.tools.ticket_tool import TicketTool
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

from pprint import pprint
class GraphEngine:
    def __init__(self, factory, storage_manager):
        self.factory = factory
        self.storage_manager = storage_manager
        
        # 1. Creiamo gli agenti necessari al grafo
        self.llms = {
            "master": self.factory.create_agent("master"),
            "kb": self.factory.create_agent("kb"),
            "query": self.factory.create_agent("query"),
            "planning_llm": self.factory.create_agent("planning_llm"),
            "planner_llm": self.factory.create_agent("planner_llm"),
            'critic_llm': self.factory.create_agent("critic_llm"),
            
            'ticket_llm': self.factory.create_agent("ticket_llm")
        }

        # 2. Setup dei Tool
        self.tool_executor = ToolExecutor()
        kb_tool = KnowledgeBaseTool(
            query_llm=self.llms["query"],
            kb_llm=self.llms["kb"],
            storage_manager=self.storage_manager
        )
        self.tool_executor.register(kb_tool)

        planning_tool = PlanningTool(planning_llm=self.llms["planning_llm"], storage_manager=self.storage_manager)
        self.tool_executor.register(planning_tool)

        network_tool = NetworkTool(storage_manager=self.storage_manager)
        self.tool_executor.register(network_tool)

        ticket_tool = TicketTool(ticket_llm=self.llms["ticket_llm"], storage_manager=self.storage_manager)
        self.tool_executor.register(ticket_tool)


        # 3. Setup dei Nodi (usando la tua classe GraphNodes)
        self.nodes = GraphNodes(self.llms, self.tool_executor)

        # 4. Costruzione del Grafo
        self.app = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("dispatcher", self.nodes.dispatcher_node)
        workflow.add_node("tools", self.nodes.tool_node)
        workflow.add_node("master", self.nodes.master_node)
        workflow.add_node("critic", self.nodes.critic_node)

        workflow.set_entry_point("dispatcher")

        workflow.add_edge("dispatcher", "tools")
        workflow.add_edge("tools", "master")
        workflow.add_edge("master", "critic")

        workflow.add_conditional_edges(
            "critic",
            self.after_critic,
            {
                "continue": "dispatcher",
                "finish": END,
            }
)

        memory = MemorySaver()

        return workflow.compile(checkpointer=memory)

    def run(self, user_query: str, chat_id: str):

        initial_state = {
            "messages": [HumanMessage(content=user_query)],
            "plan_reasoning": [],
            "execution_plan": [],
            "critic_feedback": {},
            "remaining_iterations": 2
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
    
    def after_critic(self, state):

        feedback = state.get("critic_feedback", {})

        if feedback.get("investigation_complete", False) or  state["remaining_iterations"] <= 0:
            pprint('======= FINAL STATE ========', state)
            return "finish"

        return "continue"



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
    storage_manager = StorageManager(light_mode=True)

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