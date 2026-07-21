import json
from pprint import pprint
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

        messages = state["messages"]
        last_user_message = messages[-1].content

        data = {
            "conversation_history": "",
            "user_query": last_user_message,
            "critic_feedback": state.get("critic_feedback", {}).get("recommended_tool_calls", ""),
            "called_tools": state.get("called_tools", [])
        }


        result = self.llms["planner_llm"].get_reasoning_and_tools(data)

        print("[DISPATCHER NODE]:", result, '\n\n',data)

        return {
            "plan_reasoning": [
                result.get("plan_reasoning", "")
            ],
            "execution_plan": result.get("execution_plan", []),
            "tools_to_call": result.get("execution_plan", []),
            "called_tools":state.get("called_tools", []) + self.extract_tools(result.get("execution_plan", []))
    }

    def extract_tools(self, plan):
        tools = []
        for elem in plan:
            tools.append(elem['tool_name'])
        return tools




    def tool_node(self, state: AgentState):

        results = state.get("tool_results", {})

        tool_and_inputs = self.get_tools_to_call(state)
        print(f"[TOOL NODE] Tools to call: {tool_and_inputs}")
        for tool_call in tool_and_inputs:
            result = self.tool_executor.execute(
                tool_call["tool_name"],
                tool_call["tool_input"]
            )
            results[tool_call["tool_name"]] = result

        return {
            "tool_results": results,
            "tools_to_call": []
        }

    def get_tools_to_call(self, state: AgentState):
        tools_inputs = []
        execution_plan = state.get("execution_plan", [])
        for element in execution_plan:
            print(f'- Processing Tool: {element["tool_name"]}, Parameters: {element["tool_input"]}')
            tools_inputs.append({"tool_name": element["tool_name"], "tool_input": element["tool_input"]})
        return tools_inputs

    def master_node(self, state: AgentState):

        messages = state["messages"]
        history_text = conversation_to_text(messages[-3:])



        print(f">>[MASTER NODE]: Inputs ")
        data = state.get("tool_results", {})
        for elem in data:
            print("\n  >>", elem, ":", data[elem])

        response = self.llms["master"].speak({
            "user_query": messages[-1].content,
            "tool_results": data
        })

        print(f"[MASTER NODE] Response: \n {response}")

        return {"synthesized_response": response}
    
    def critic_node(self, state: AgentState):
        messages = state["messages"]

        response = self.llms["critic_llm"].speak({
            "user_query": messages[-1].content,
            "tools_called": state.get("execution_plan", []),
            "final_answer": state.get("synthesized_response", "")
        })


        try:
            json_response = self.extract_json(response)
            print(f"[CRITIC NODE]:\n {response}")
        except ValueError as e:
            print(f"[CRITIC NODE] Error extracting JSON: {e}")
            json_response = {}


        return {
                "critic_feedback": json_response,
                "remaining_iterations": state["remaining_iterations"] - 1
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
