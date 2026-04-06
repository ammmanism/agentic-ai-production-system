"""RAG retrieval — LLM-based context compressor."""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

_COMPRESS_PROMPT = """Given the following retrieved passages and a user query, extract only the
sentences that are relevant to answering the query. Keep it concise.

Query: {query}

Passages:
{passages}

Relevant context:"""


def compress_context(
    query: str,
    passages: List[Dict[str, Any]],
    max_tokens: int = 400,
) -> str:
    """
    Use an LLM to remove irrelevant sentences from retrieved passages.

    Falls back to naive truncation when no API key is configured.
    """
    texts = [p.get("payload", {}).get("text", str(p)) for p in passages]
    combined = "\n\n".join(texts)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set — returning raw passages (truncated)")
        return combined[:max_tokens * 4]

    try:
        import openai  # type: ignore

        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": _COMPRESS_PROMPT.format(query=query, passages=combined),
                }
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:  # noqa: BLE001
        logger.error("Context compression failed: %s", exc)
        return combined[:max_tokens * 4]
