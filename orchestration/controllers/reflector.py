"""Orchestration controllers — reflector."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def evaluate_results(
    plan: List[str],
    results: List[Dict[str, Any]],
    query: str,
) -> Dict[str, Any]:
    """
    Self-critique: determine if results are good enough or if replanning is needed.

    Production implementation uses an LLM judge with a rubric prompt.
    Returns a dict with keys:
      - ``needs_replan`` (bool)
      - ``critique`` (str)
      - ``revised_plan`` (list[str] | None)
    """
    logger.info("Reflector evaluating %d results for query: %s", len(results), query)

    failed_steps = [r for r in results if r.get("status") != "success"]

    if failed_steps:
        logger.warning("Reflector detected %d failed steps, triggering replan", len(failed_steps))
        return {
            "needs_replan": True,
            "critique": f"{len(failed_steps)} step(s) failed. Revising plan.",
            "revised_plan": None,  # Planner will re-generate
        }

    return {
        "needs_replan": False,
        "critique": "All steps succeeded. Answer quality appears sufficient.",
        "revised_plan": None,
    }
