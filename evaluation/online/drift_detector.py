"""Online evaluation — detect distribution drift in user queries."""
from __future__ import annotations

import logging
import math
from collections import Counter
from typing import List

logger = logging.getLogger(__name__)


class DriftDetector:
    """
    Monitor input query distributions and alert on significant shifts.

    Uses Jensen-Shannon divergence (symmetric KL divergence) between
    a reference distribution and a sliding window of recent queries.
    A JS divergence > threshold indicates drift.
    """

    def __init__(self, window_size: int = 100, threshold: float = 0.15):
        self._window_size = window_size
        self._threshold = threshold
        self._reference: Counter = Counter()
        self._recent: List[str] = []

    def set_reference(self, queries: List[str]) -> None:
        """Establish the baseline distribution from a corpus of known-good queries."""
        tokens = " ".join(queries).lower().split()
        self._reference = Counter(tokens)
        logger.info("DriftDetector: reference set with %d unique tokens", len(self._reference))

    def update(self, query: str) -> float:
        """
        Add a new query to the sliding window and return current JS divergence.

        Returns a float in [0, 1]. Values above ``threshold`` suggest drift.
        """
        self._recent.append(query)
        if len(self._recent) > self._window_size:
            self._recent.pop(0)

        recent_tokens = " ".join(self._recent).lower().split()
        recent_counter = Counter(recent_tokens)
        divergence = self._js_divergence(self._reference, recent_counter)

        if divergence > self._threshold:
            logger.warning(
                "Query drift detected! JS divergence=%.4f > threshold=%.2f",
                divergence,
                self._threshold,
            )
        return divergence

    @staticmethod
    def _js_divergence(p: Counter, q: Counter) -> float:
        vocab = set(p) | set(q)
        total_p = sum(p.values()) or 1
        total_q = sum(q.values()) or 1

        def kl(a: Counter, b: Counter, total_a: int, total_b: int) -> float:
            result = 0.0
            for token in vocab:
                pa = a.get(token, 0) / total_a
                pb = b.get(token, 0) / total_b
                m = (pa + pb) / 2
                if pa > 0 and m > 0:
                    result += pa * math.log(pa / m)
            return result

        return (kl(p, q, total_p, total_q) + kl(q, p, total_q, total_p)) / 2
