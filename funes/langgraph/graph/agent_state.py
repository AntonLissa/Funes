from typing import Annotated, Dict, List, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    query: str
    chat_id: str
    messages: Annotated[List[BaseMessage], add_messages]
    tools_used: List[str]
    tools_to_call: List[str]
    tool_results: Dict[str, str]
    final_answer: str
