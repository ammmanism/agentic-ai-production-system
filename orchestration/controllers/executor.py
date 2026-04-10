"""Orchestration controllers — executor."""
from __future__ import annotations

import logging
from typing import Any, Dict, List
from execution.tools.registry import execute, list_tools

logger = logging.getLogger(__name__)


def run_step(step: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single plan step using the appropriate tool.

    The executor looks up the tool registry and dispatches the step to the
    correct tool (web search, calculator, code interpreter, etc.).
    """
    logger.info("Executor running step: %s", step)

    # Simplified heuristic parser for tool dispatch
    tools = list_tools()
    called_tool = None
    args = {"query": step}
    
    for tool_name in tools.keys():
        if tool_name.lower() in step.lower():
            called_tool = tool_name
            break
            
    try:
        if called_tool:
            output = execute(called_tool, **args)
        else:
            output = f"[Simulated output for step: {step}]"
            
        return {
            "step": step,
            "status": "success",
            "output": output,
        }
    except Exception as e:
        logger.error(f"Error executing tool: {e}")
        return {
            "step": step,
            "status": "error",
            "output": f"Tool execution failed: {e}",
        }


def execute_plan(plan: List[str], context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Run all steps in a plan sequentially."""
    results = []
    for step in plan:
        result = run_step(step, context)
        results.append(result)
        if result.get("status") != "success":
            logger.warning("Step failed, stopping execution: %s", step)
            break
    return results
