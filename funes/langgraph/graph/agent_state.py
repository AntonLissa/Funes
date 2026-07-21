from typing import Annotated, Dict, List, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    query: str
    chat_id: str
    messages: Annotated[List[BaseMessage], add_messages]
    plan_reasoning: List[str]
    execution_plan: List[Dict[str, str]]
    remaining_iterations: int
    tool_results: Dict[str, str]
    synthesized_response: str
    critic_feedback: Dict[str, str]
    called_tools: List[str]
