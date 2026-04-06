"""PII scrubber using regex patterns (Presidio can be added as optional dep)."""
from __future__ import annotations

import re
from typing import Dict, Tuple

# Pattern → replacement tag
PII_PATTERNS: Dict[str, str] = {
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b": "[EMAIL]",
    r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b": "[PHONE]",
    r"\b\d{3}-\d{2}-\d{4}\b": "[SSN]",
    r"\b4[0-9]{12}(?:[0-9]{3})?\b": "[CREDIT_CARD]",
    r"\b(?:25[0-5]|2[0-4]\d|[01]?\d\d?)(?:\.(?:25[0-5]|2[0-4]\d|[01]?\d\d?)){3}\b": "[IP_ADDRESS]",
}


def scrub_pii(text: str) -> Tuple[str, Dict[str, int]]:
    """
    Remove PII from *text* by replacing it with placeholder tags.

    Returns:
        Tuple of (scrubbed_text, {entity_type: count_replaced}).
    """
    counts: Dict[str, int] = {}
    for pattern, tag in PII_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            counts[tag] = len(matches)
            text = re.sub(pattern, tag, text, flags=re.IGNORECASE)
    return text, counts
