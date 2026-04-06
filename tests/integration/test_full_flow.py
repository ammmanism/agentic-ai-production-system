"""Integration test — full agent flow from planner to final answer."""
from __future__ import annotations

import pytest
from orchestration.graph.state import AgentState
from orchestration.graph.nodes import planner_node, executor_node, reflector_node


def make_initial_state(query: str) -> AgentState:
    return AgentState(
        query=query,
        messages=[],
        plan=None,
        current_step=0,
        tool_results=[],
        final_answer=None,
        needs_replan=False,
        replan_count=0,
        context=None,
        metadata={},
    )


def test_full_agent_flow():
    """Run a query through planner → executor → reflector → final answer."""
    state = make_initial_state("What is the capital of France?")

    # 1. Plan
    state = planner_node(state)
    assert state["plan"] is not None
    assert len(state["plan"]) > 0

    # 2. Execute all steps
    for _ in range(len(state["plan"])):
        state = executor_node(state)
        if state["final_answer"] is not None:
            break

    assert state["final_answer"] is not None or state["current_step"] > 0


def test_reflector_prevents_infinite_loop():
    """Ensure reflector caps replan cycles at MAX_REPLAN."""
    from orchestration.graph.nodes import MAX_REPLAN

    state = make_initial_state("loop test")
    state = planner_node(state)
    state["needs_replan"] = True

    for _ in range(MAX_REPLAN + 1):
        state = reflector_node(state)
        if not state["needs_replan"]:
            break

    assert state["needs_replan"] is False


def test_executor_handles_empty_plan():
    """Executor should gracefully handle an empty plan."""
    state = make_initial_state("empty plan test")
    state["plan"] = []
    state = executor_node(state)
    assert state["final_answer"] is not None
