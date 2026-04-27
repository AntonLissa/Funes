from pyexpat.errors import messages
from typing import Dict
from langchain_core.messages import AIMessage

from funes.langgraph.graph.agent_state import AgentState
from funes.langgraph.tools.tool_executor import ToolExecutor


class GraphNodes:
    def __init__(self, llms: Dict, tool_executor: ToolExecutor):
        self.llms = llms
        self.tool_executor = tool_executor

    def dispatcher_node(self, state: AgentState):

        messages = state["messages"]
        last_user_message = messages[-1].content

        result = self.llms["dispatcher"].get_reasoning_and_tools(last_user_message)



        return {
            "tools_to_call": result["tools"]
        }


    def tool_node(self, state: AgentState):

       

        results = {}

        for tool_name in state["tools_to_call"]:
            results[tool_name] = self.tool_executor.execute(tool_name,  state["messages"])

        print(f"[TOOL RESULTS]\n {results}")
        return {
            "tool_results": results
        }

    def master_node(self, state: AgentState):

        messages = state["messages"]

        tool_results = state.get("tool_results", {})

        response = self.llms["master"].speak({
            "conversation_history": messages,
            "user_query": messages[-1].content,
            "tool_results": tool_results
        })

        return {
            "messages": [AIMessage(content=response)],
        }
