from typing import TypedDict, Annotated, List, Optional, Any
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """
    Type-safe execution state mapped exactly to the LangGraph node boundaries.
    """
    messages: Annotated[List[BaseMessage], operator.add]
    session_id: str
    current_thought: Optional[str]
    retrieved_context: Optional[List[dict]]
    tool_calls: Optional[List[dict]]
    error: Optional[str]
    is_summarized: bool
    flops_estimate: float
