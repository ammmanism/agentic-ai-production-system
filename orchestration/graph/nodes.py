"""LangGraph node functions: planner, executor, reflector."""
from __future__ import annotations

import logging
from typing import Any, Dict

from .state import AgentState

logger = logging.getLogger(__name__)

MAX_REPLAN = 3  # Guard against infinite loops


# ---------------------------------------------------------------------------
# Planner node
# ---------------------------------------------------------------------------

def planner_node(state: AgentState) -> AgentState:
    """Decompose the user query into an ordered list of executable steps."""
    logger.info("planner_node: decomposing query=%s", state["query"])

    # In production: call the LLM with a structured-output prompt.
    # Here we create a simple deterministic plan for demonstration.
    plan = [
        f"Step 1: Retrieve relevant context for '{state['query']}'",
        "Step 2: Analyse context and identify key facts",
        "Step 3: Synthesise a concise answer",
    ]

    return {
        **state,
        "plan": plan,
        "current_step": 0,
        "needs_replan": False,
    }


# ---------------------------------------------------------------------------
# Executor node
# ---------------------------------------------------------------------------

def executor_node(state: AgentState) -> AgentState:
    """Execute the current plan step using available tools."""
    plan = state.get("plan") or []
    step_idx = state.get("current_step", 0)

    if step_idx >= len(plan):
        logger.info("executor_node: plan complete, synthesising final answer")
        answer = _synthesise(state)
        return {**state, "final_answer": answer, "needs_replan": False}

    current_step = plan[step_idx]
    logger.info("executor_node: executing step %d — %s", step_idx, current_step)

    # Simulate tool execution (replace with real tool dispatch)
    result: Dict[str, Any] = {
        "step": current_step,
        "output": f"[simulated result for: {current_step}]",
    }

    tool_results = list(state.get("tool_results") or [])
    tool_results.append(result)

    # Decide if we need a replan (e.g., tool failed)
    needs_replan = False

    return {
        **state,
        "tool_results": tool_results,
        "current_step": step_idx + 1,
        "needs_replan": needs_replan,
    }


# ---------------------------------------------------------------------------
# Reflector node
# ---------------------------------------------------------------------------

def reflector_node(state: AgentState) -> AgentState:
    """Self-critique the executor output and decide whether to replan."""
    replan_count = state.get("replan_count", 0) + 1
    logger.info("reflector_node: replan cycle %d", replan_count)

    if replan_count >= MAX_REPLAN:
        logger.warning("reflector_node: max replan cycles reached, forcing answer")
        return {
            **state,
            "replan_count": replan_count,
            "needs_replan": False,
            "final_answer": "Unable to produce a confident answer after multiple attempts.",
        }

    # In production: use an LLM to decide whether the results are good enough.
    should_replan = False  # Placeholder logic

    return {
        **state,
        "replan_count": replan_count,
        "needs_replan": should_replan,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _synthesise(state: AgentState) -> str:
    """Combine tool results into a final answer (stub — replace with LLM)."""
    results = state.get("tool_results") or []
    outputs = [r.get("output", "") for r in results]
    return " | ".join(outputs) if outputs else "No answer generated."
