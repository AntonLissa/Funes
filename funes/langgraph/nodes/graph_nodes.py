import json
from pyexpat.errors import messages
from typing import Dict
from langchain_core.messages import AIMessage

from funes.langgraph.graph.agent_state import AgentState
from funes.langgraph.tools.tool_executor import ToolExecutor
from funes.utils.utils import conversation_to_text


class GraphNodes:
    def __init__(self, llms: Dict, tool_executor: ToolExecutor):
        self.llms = llms
        self.tool_executor = tool_executor

    def dispatcher_node(self, state: AgentState):
        messages = state["messages"]  # Prendi solo gli ultimi 10 messaggi per il contesto
        conversation_history = conversation_to_text(messages[-10:-1])
        last_user_message = messages[-1].content

        result = self.llms["dispatcher"].get_reasoning_and_tools(query = last_user_message, conversation_history = conversation_history)

        return {
            "tools_to_call": result["tools"]
        }


    def tool_node(self, state: AgentState):

        results = state.get("tool_results", {})

        tool_calls = state.get("tools_to_call", [])

        for tool_call in tool_calls:
            results[tool_call] = self.tool_executor.execute(
                tool_call,
                state.get("messages", [])
            )
            print(f'Executed tool {tool_call} with result {results[tool_call]}')

        return {
            "tool_results": results,
            "tools_to_call": []
        }

    def master_node(self, state: AgentState):

        messages = state["messages"]
        history_text = conversation_to_text(messages[-3:])


        response = self.llms["master"].speak({
            "conversation_history": history_text,
            "user_query": messages[-1].content,
            "tool_results": state.get("tool_results", {}),
            "investigation_state": state.get("investigation_state", {})
        })

        print('Running master', response)

        parsed = self.extract_json(response)

        
        return {
            "investigation_state": parsed.get("updated_state", {}),
            "tools_to_call": parsed["decision"].get("tool_calls", []),
 
            "iteration": state["iteration"] + 1 
        }
    
    def extract_json(self, text: str):
        # 1. elimina code fences
        text = text.replace("```json", "").replace("```", "").strip()

        # 2. trova primo blocco JSON plausibile
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON found")

        json_str = text[start:end+1]

        # 3. parse
        return json.loads(json_str)
