"""RAG ingestion — recursive + semantic text chunker."""
from __future__ import annotations

from typing import List
import logging

logger = logging.getLogger(__name__)


def chunk_text(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
    separator: str = "\n\n",
) -> List[str]:
    """
    Split *text* into overlapping chunks using a recursive separator strategy.

    Strategy:
    1. Split on double newlines (paragraph breaks).
    2. If a paragraph still exceeds *chunk_size*, split on single newlines.
    3. Finally, split on spaces.

    Returns a list of non-empty string chunks.
    """
    separators = [separator, "\n", " ", ""]

    def _split(text: str, seps: List[str]) -> List[str]:
        if not seps or len(text) <= chunk_size:
            return [text] if text.strip() else []
        sep, *rest_seps = seps
        parts = text.split(sep) if sep else list(text)
        chunks: List[str] = []
        current = ""
        for part in parts:
            candidate = (current + sep + part).lstrip(sep) if current else part
            if len(candidate) > chunk_size and current:
                chunks.append(current)
                current = part
            else:
                current = candidate
        if current:
            chunks.append(current)

        result: List[str] = []
        for chunk in chunks:
            if len(chunk) > chunk_size:
                result.extend(_split(chunk, rest_seps))
            else:
                result.append(chunk)
        return result

    raw_chunks = _split(text, separators)

    # Add overlap between consecutive chunks
    if chunk_overlap <= 0 or len(raw_chunks) <= 1:
        return raw_chunks

    overlapping: List[str] = [raw_chunks[0]]
    for i in range(1, len(raw_chunks)):
        prev_tail = raw_chunks[i - 1][-chunk_overlap:]
        overlapping.append(prev_tail + raw_chunks[i])

    return overlapping
