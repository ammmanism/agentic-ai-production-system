import logging
from typing import Literal
from langgraph.graph import StateGraph, END

from .state import AgentState
from .nodes import planner_node, executor_node, reflector_node

logger = logging.getLogger(__name__)

def route_after_planner(state: AgentState) -> str:
    """Route from planner node."""
    return "executor"

def route_after_executor(state: AgentState) -> str:
    """Route after executor node. Loop if steps remain, otherwise reflect."""
    plan = state.get("plan") or []
    step_idx = state.get("current_step", 0)
    if step_idx >= len(plan):
        return "reflector"
    return "executor"

def route_after_reflector(state: AgentState) -> str:
    """Route after reflection. Re-plan if flagged, otherwise terminate."""
    if state.get("needs_replan", False):
        return "planner"
    return END

def get_agent_graph() -> StateGraph:
    """
    Compiles the production graph.
    Connects planner, executor, and reflector nodes using deterministic state routing.
    """
    workflow = StateGraph(AgentState)

    # 1. Add all functional nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("reflector", reflector_node)

    # 2. Configure topology
    workflow.set_entry_point("planner")

    workflow.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "executor": "executor"
        }
    )

    workflow.add_conditional_edges(
        "executor",
        route_after_executor,
        {
            "executor": "executor",
            "reflector": "reflector"
        }
    )

    workflow.add_conditional_edges(
        "reflector",
        route_after_reflector,
        {
            "planner": "planner",
            "end": END
        }
    )

    return workflow.compile()
