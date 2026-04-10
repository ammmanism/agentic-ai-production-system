"""LangGraph node functions: planner, executor, reflector."""
from __future__ import annotations

import logging
import os
from typing import Any, Dict

from .state import AgentState
from orchestration.controllers.planner import decompose_query
from orchestration.controllers.executor import run_step

logger = logging.getLogger(__name__)

MAX_REPLAN = 3  # Guard against infinite loops


# ---------------------------------------------------------------------------
# Planner node
# ---------------------------------------------------------------------------

def planner_node(state: AgentState) -> AgentState:
    """Decompose the user query into an ordered list of executable steps."""
    logger.info("planner_node: decomposing query=%s", state["query"])

    plan = decompose_query(state["query"])

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

    result = run_step(current_step, state)

    tool_results = list(state.get("tool_results") or [])
    tool_results.append(result)

    needs_replan = result.get("status") != "success"

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

    should_replan = state.get("needs_replan", False)

    return {
        **state,
        "replan_count": replan_count,
        "needs_replan": should_replan,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _synthesise(state: AgentState) -> str:
    """Combine tool results into a final answer via LLM synthesis if available."""
    results = state.get("tool_results") or []
    outputs = [r.get("output", "") for r in results]
    context = "\\n".join(str(o) for o in outputs)
    
    if os.getenv("OPENAI_API_KEY"):
        try:
            from langchain.chat_models import init_chat_model
            from langchain.schema import HumanMessage
            
            llm = init_chat_model("gpt-3.5-turbo", model_provider="openai")
            prompt = f"Synthesize a helpful answer to the user's query '{state['query']}' using ONLY the following execution logs context:\\n{context}"
            response = llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            logger.warning(f"Synthesis failed, using fallback: {e}")

    return " | ".join(outputs) if outputs else "No answer generated."
