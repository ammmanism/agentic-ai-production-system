"""RAG ingestion — batch text embedder."""
from __future__ import annotations

import logging
import os
from typing import List

logger = logging.getLogger(__name__)


def embed_texts(texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:
    """
    Embed a list of text strings into dense vectors.

    Uses the OpenAI Embeddings API when OPENAI_API_KEY is set,
    otherwise returns stub zero-vectors for local dev / CI.
    """
    if not texts:
        return []

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set — returning stub embeddings (dim=1536)")
        return [[0.0] * 1536 for _ in texts]

    try:
        import openai  # type: ignore

        client = openai.OpenAI(api_key=api_key)
        response = client.embeddings.create(input=texts, model=model)
        return [item.embedding for item in response.data]
    except Exception as exc:  # noqa: BLE001
        logger.error("Embedding failed: %s", exc)
        return [[0.0] * 1536 for _ in texts]
