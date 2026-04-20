from typing import TypedDict, List, Dict, Callable
from langgraph.graph import StateGraph, END

from funes.AIM.config.config_loader import ConfigLoader
from funes.AIM.core.agent_factory import AgentFactory
from funes.AIM.llm.provider.groq_provider import GroqProvider
from funes.Storage.storage_manager import StorageManager
import funes.AIM.core.register_agents
from funes.AIM.core.agent_registry import registry


# -------------------------
# INIT INFRA
# -------------------------

config_loader = ConfigLoader()
provider = GroqProvider(config_loader.load_api_key())

factory = AgentFactory(
    registry=registry,
    config_loader=config_loader,
    provider=provider
)

storage_manager = StorageManager(light_mode=False)


# -------------------------
# STATE
# -------------------------

class AgentState(TypedDict):
    query: str
    tools_to_call: List[str]
    tool_results: Dict[str, str]
    final_answer: str


# -------------------------
# TOOL FACTORY (CORE FIX)
# -------------------------

def build_tools(llms):
    kb_llm = llms['kb']
    query_llm = llms['query']

    def telemetry_tool(query: str):
        return "Telemetry: no anomalies detected in last 24h"

    def ticketing_llm_tool(query: str):
        return "Ticket OPS-231: intermittent power fluctuation reported"

    def network_monitor(query: str):
        return "Network: packet loss detected during pass 14"

    def planning_tool(query: str):
        return "Planning: pass 14 overlapped with maintenance window"

    def fds_tool(query: str):
        return "FDS: maneuver executed yesterday 18:42 UTC"

    def knowledge_base_tool(conversation, query: str):
        query_enhanced = query_llm.speak(conversation, query)
        rag_data = storage_manager.get_kb_results(query)
        kb_llm.add_user_message(query)
        return kb_llm.speak(rag_data)

    return {
        "telemetry_tool": telemetry_tool,
        "ticketing_llm_tool": ticketing_llm_tool,
        "network_monitor": network_monitor,
        "planning_tool": planning_tool,
        "fds_tool": fds_tool,
        "knowledge_base_tool": knowledge_base_tool,
    }


# -------------------------
# DISPATCHER NODE
# -------------------------

def dispatcher_node(state: AgentState, dispatcher_llm):

    result = dispatcher_llm.get_reasoning_and_tools(state["query"])

    print("\n[DISPATCHER ANALYSIS]")
    print(result["analysis"])
    print("[TOOLS]", result["tools"])

    return {
        "tools_to_call": result.get("tools", [])
    }


# -------------------------
# TOOL NODE
# -------------------------

def tool_node(state: AgentState, tool_registry: Dict[str, Callable]):

    results = {}

    for tool_name in state["tools_to_call"]:
        tool = tool_registry.get(tool_name)

        if tool:
            results[tool_name] = tool(state["query"])

    return {
        **state,
        "tool_results": results
    }


# -------------------------
# MASTER NODE
# -------------------------

def master_node(state: AgentState, master_llm):

    response = master_llm.speak({
        "query": state["query"],
        "tool_results": state.get("tool_results", {})
    })

    return {
        "final_answer": response
    }


# -------------------------
# GRAPH BUILDER
# -------------------------

def build_graph(llms, tool_registry):
    dispatcher_llm = llms['dispatcher']
    master_llm = llms['master']
    query_llm = llms['query']

    graph = StateGraph(AgentState)

    graph.add_node(
        "dispatcher",
        lambda s: dispatcher_node(s, dispatcher_llm)
    )

    graph.add_node(
        "tools",
        lambda s: tool_node(s, tool_registry)
    )

    graph.add_node(
        "master",
        lambda s: master_node(s, master_llm)
    )

    graph.set_entry_point("dispatcher")

    graph.add_edge("dispatcher", "tools")
    graph.add_edge("tools", "master")
    graph.add_edge("master", END)

    return graph.compile()


# -------------------------
# MAIN
# -------------------------

if __name__ == "__main__":

    factory = AgentFactory(registry, config_loader, provider)

    dispatcher_llm = factory.create_agent("dispatcher")
    master_llm = factory.create_agent("master")
    kb_llm = factory.create_agent("kb")
    query_llm = factory.create_agent('query')

    tools_llm = {'query': query_llm, "kb": kb_llm}
    general_llms = {'master': master_llm, "dispatcher": dispatcher_llm }
    # 👇 dependency injection pulita
    tool_registry = build_tools(tools_llm)

    app = build_graph(
        llms=general_llms, 
        tool_registry=tool_registry
    )

    while True:
        query = input(">>>")
        if query == 'exit': break

        result = app.invoke({
            "query": query,
            "tools_to_call": [],
            "tool_results": {},
            "final_answer": ""
        })

        print("\n================ FINAL ANSWER ================\n")
        print(result["final_answer"])

