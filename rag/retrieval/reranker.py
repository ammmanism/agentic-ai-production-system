"""RAG retrieval — cross-encoder reranker."""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def rerank(
    query: str,
    candidates: List[Dict[str, Any]],
    top_k: int = 3,
    model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
) -> List[Dict[str, Any]]:
    """
    Rerank *candidates* using a cross-encoder model.

    Requires the ``sentence-transformers`` package.
    Falls back to identity (original order) when not installed.
    """
    try:
        logger.debug(f"Attempting to rerank {len(candidates)} candidates using cross-encoder.")
        from sentence_transformers import CrossEncoder  # type: ignore

        encoder = CrossEncoder(model)
        pairs = [(query, c.get("payload", {}).get("text", "")) for c in candidates]
        scores = encoder.predict(pairs)

        for candidate, score in zip(candidates, scores):
            candidate["rerank_score"] = float(score)

        reranked = sorted(candidates, key=lambda x: x.get("rerank_score", 0.0), reverse=True)
        return reranked[:top_k]

    except ImportError:
        logger.warning("sentence-transformers not installed — skipping reranking")
        return candidates[:top_k]
    except Exception as exc:  # noqa: BLE001
        logger.error("Reranking failed: %s", exc)
        return candidates[:top_k]
