"""Toxicity filter — flags harmful content using keyword lists + optional model."""
from __future__ import annotations

import logging
import re
from typing import Tuple

logger = logging.getLogger(__name__)

# Coarse-grained keyword blocklist (extend as needed)
_BLOCKLIST_PATTERNS = [
    r"\b(?:kill|murder|shoot|bomb|terrorist)\b",
    r"\b(?:how to make|how to build|synthesize).{0,30}(?:bomb|weapon|drug|poison)\b",
    r"\b(?:child|minor|underage).{0,20}(?:sexual|nude|explicit)\b",
]


def is_toxic(text: str, threshold: float = 0.8) -> Tuple[bool, float, str]:
    """
    Check whether *text* contains toxic content.

    Args:
        text: User input to evaluate.
        threshold: Toxicity score above which content is flagged (0-1).

    Returns:
        (is_flagged, score, reason)

    Strategy:
    1. Fast regex keyword filter (no model, zero latency).
    2. Optional: ``detoxify`` model for nuanced scoring.
    """
    # 1. Keyword filter
    for pattern in _BLOCKLIST_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            reason = f"Keyword match: {pattern}"
            logger.warning("Toxicity keyword blocked: pattern=%s", pattern)
            return True, 1.0, reason

    # 2. Detoxify model (optional)
    try:
        from detoxify import Detoxify  # type: ignore

        results = Detoxify("original").predict(text)
        score = max(results.values())
        if score >= threshold:
            reason = f"Model toxicity score={score:.2f}"
            logger.warning("Toxicity model blocked: score=%.2f", score)
            return True, score, reason
    except ImportError:
        pass  # Detoxify not installed — keyword-only mode

    return False, 0.0, ""
