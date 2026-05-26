from typing import TypedDict, Annotated, List, Optional, Any, Dict
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict, total=False):
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

    # Integrated execution keys
    query: str
    plan: Optional[List[str]]
    current_step: int
    tool_results: List[Dict[str, Any]]
    final_answer: Optional[str]
    needs_replan: bool
    replan_count: int
    context: Optional[Any]
    metadata: Dict[str, Any]
