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

def reciprocal_rank_fusion(
    dense_results: List[dict],
    sparse_results: List[dict],
    alpha: float = 0.5,
    k: int = 60
) -> List[dict]:
    """
    RRF fusion of dense and sparse result ranks.
    dense_results, sparse_results: lists containing {"id": doc_id, ...}
    alpha: weight for dense (1-alpha for sparse)
    k: constant to avoid division by zero
    """
    logger.debug(f"Executing RRF hybrid fusion with alpha={alpha}")
    scores = {}
    
    for rank, doc in enumerate(dense_results):
        doc_id = doc["id"]
        scores[doc_id] = scores.get(doc_id, 0) + alpha / (k + rank + 1)

    for rank, doc in enumerate(sparse_results):
        doc_id = doc["id"]
        scores[doc_id] = scores.get(doc_id, 0) + (1 - alpha) / (k + rank + 1)

    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [{"id": doc_id, "fusion_score": score} for doc_id, score in sorted_docs]
