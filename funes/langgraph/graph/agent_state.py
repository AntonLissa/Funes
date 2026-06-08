from typing import Annotated, Dict, List, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    query: str
    chat_id: str
    messages: Annotated[List[BaseMessage], add_messages]
    tools_to_call: List[str]
    tool_results: Dict[str, str]
    pending_tool_calls: List[Dict]

    investigation_state: Dict
    iteration: int
    final_answer: str
