"""Agent state definition using TypedDict for LangGraph."""
from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict):
    """Typed state for the agent graph."""

    # The original user query
    query: str

    # Chat history as list of dicts with role/content
    messages: List[Dict[str, str]]

    # Plan produced by the planner node
    plan: Optional[List[str]]

    # Current step index in the plan
    current_step: int

    # Results from each tool / executor step
    tool_results: List[Dict[str, Any]]

    # Final synthesised answer
    final_answer: Optional[str]

    # Signal for reflector: should we replan?
    needs_replan: bool

    # Number of replanning cycles (prevents infinite loops)
    replan_count: int

    # Retrieved RAG context
    context: Optional[str]

    # Metadata: model used, cost, latency …
    metadata: Dict[str, Any]
