"""Semantic cache — deduplicate LLM calls using embedding similarity."""
from __future__ import annotations

import hashlib
import logging
import os
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_SIMILARITY_THRESHOLD = 0.95


class SemanticCache:
    """
    Cache LLM responses for semantically near-duplicate queries.

    In production: store embeddings in Redis and run approximate nearest-neighbour
    search (e.g., redis-py with RediSearch + vector index).
    This stub uses a Python list for portability.
    """

    def __init__(self, ttl_seconds: int = 3600, threshold: float = _SIMILARITY_THRESHOLD):
        self._entries: List[Dict[str, Any]] = []
        self._ttl = ttl_seconds
        self._threshold = threshold

    def _embed(self, text: str) -> List[float]:
        """Return embedding (stub: hash-based pseudo-vector for CI)."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Deterministic stub vector from SHA-256 hash
            digest = hashlib.sha256(text.encode()).digest()
            return [b / 255.0 for b in digest]  # 32-dim stub
        from rag.ingestion.embedder import embed_texts  # lazy import
        return embed_texts([text])[0]

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        if len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        return dot / (norm_a * norm_b + 1e-9)

    def get(self, query: str) -> Optional[str]:
        """Return a cached answer if a semantically similar query exists."""
        now = time.time()
        vec = self._embed(query)

        for entry in self._entries:
            if now - entry["timestamp"] > self._ttl:
                continue
            similarity = self._cosine(vec, entry["vector"])
            if similarity >= self._threshold:
                logger.info("SemanticCache HIT (similarity=%.3f)", similarity)
                return entry["answer"]

        return None

    def set(self, query: str, answer: str) -> None:
        """Store a query-answer pair in the cache."""
        vec = self._embed(query)
        self._entries.append({"query": query, "vector": vec, "answer": answer, "timestamp": time.time()})
        logger.info("SemanticCache SET for query: %s…", query[:60])
