"""Orchestration controllers — planner."""
from __future__ import annotations

import logging
from typing import List

logger = logging.getLogger(__name__)


def decompose_query(query: str) -> List[str]:
    """
    Break a user query into an ordered sequence of sub-tasks.

    In production this calls the LLM with a structured-output prompt
    (e.g., OpenAI function calling / tool output) that returns a JSON list
    of steps.  Here we return a deterministic stub so tests pass without
    API keys.
    """
    logger.info("Planner decomposing query: %s", query)
    return [
        f"Retrieve relevant context for: {query}",
        "Identify key facts and constraints",
        "Synthesise a final, grounded answer",
    ]
