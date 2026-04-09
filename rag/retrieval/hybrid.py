"""RAG retrieval — hybrid dense + sparse (BM25) search."""
from __future__ import annotations

import logging
import math
from collections import defaultdict
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Minimal BM25 implementation (no external deps)
# ---------------------------------------------------------------------------

class BM25:
    """BM25 sparse retrieval (Robertson et al.)."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self._docs: List[List[str]] = []
        self._df: Dict[str, int] = defaultdict(int)
        self._avgdl: float = 0.0

    def index(self, documents: List[str]) -> None:
        self._docs = [d.lower().split() for d in documents]
        N = len(self._docs)
        self._avgdl = sum(len(d) for d in self._docs) / max(N, 1)
        self._df = defaultdict(int)
        for doc in self._docs:
            for term in set(doc):
                self._df[term] += 1

    def score(self, query: str, doc_idx: int) -> float:
        tokens = query.lower().split()
        doc = self._docs[doc_idx]
        dl = len(doc)
        N = len(self._docs)
        score = 0.0
        for term in tokens:
            tf = doc.count(term)
            df = self._df.get(term, 0)
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
            tf_norm = (tf * (self.k1 + 1)) / (
                tf + self.k1 * (1 - self.b + self.b * dl / self._avgdl)
            )
            score += idf * tf_norm
        return score

    def get_top_k(self, query: str, top_k: int = 5) -> List[int]:
        scores = [(i, self.score(query, i)) for i in range(len(self._docs))]
        scores.sort(key=lambda x: x[1], reverse=True)
        return [i for i, _ in scores[:top_k]]


# ---------------------------------------------------------------------------
# Hybrid retriever
# ---------------------------------------------------------------------------

def hybrid_search(
    query: str,
    dense_results: List[Dict[str, Any]],
    sparse_scores: List[float],
    alpha: float = 0.7,
) -> List[Dict[str, Any]]:
    """
    Combine dense (vector) and sparse (BM25) scores via linear interpolation.

    alpha=1.0 → pure dense; alpha=0.0 → pure sparse.
    """
    logger.debug(f"Executing hybrid fusion with alpha={alpha} for query: {query}")
    if len(dense_results) != len(sparse_scores):
        raise ValueError("dense_results and sparse_scores must have the same length")

    max_dense = max((r.get("score", 0.0) for r in dense_results), default=1.0)
    max_sparse = max(sparse_scores, default=1.0)

    combined = []
    for result, sparse in zip(dense_results, sparse_scores):
        dense_norm = result.get("score", 0.0) / (max_dense or 1.0)
        sparse_norm = sparse / (max_sparse or 1.0)
        combined_score = alpha * dense_norm + (1 - alpha) * sparse_norm
        combined.append({**result, "combined_score": combined_score})

    combined.sort(key=lambda x: x["combined_score"], reverse=True)
    return combined
