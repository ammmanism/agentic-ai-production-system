"""Conversation summariser — compresses past turns to save context window."""
from __future__ import annotations

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def summarise_history(history: List[Dict[str, str]], max_tokens: int = 500) -> str:
    """
    Compress a list of chat messages into a concise paragraph.

    Production: call the LLM with a summarisation prompt.
    Stub: extract the last assistant turn.
    """
    if not history:
        return ""

    # Simple extractive summary: join last few messages
    tail = history[-6:]  # last 3 turns
    lines = [f"{m['role'].upper()}: {m['content']}" for m in tail]
    summary = "\n".join(lines)

    logger.info("Summariser produced %d-char summary", len(summary))
    return summary
