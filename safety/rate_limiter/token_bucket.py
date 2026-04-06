"""Token bucket rate limiter (per user / per API key)."""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class _Bucket:
    capacity: float
    refill_rate: float  # tokens per second
    tokens: float = field(init=False)
    last_refill: float = field(init=False)

    def __post_init__(self):
        self.tokens = self.capacity
        self.last_refill = time.monotonic()

    def consume(self, amount: float = 1.0) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= amount:
            self.tokens -= amount
            return True
        return False


class TokenBucketLimiter:
    """
    Per-identity (user_id or IP) token bucket rate limiter.

    Example:
        limiter = TokenBucketLimiter(capacity=60, refill_rate=1.0)
        if not limiter.allow("user-123"):
            raise HTTPException(429, "Rate limit exceeded")
    """

    def __init__(self, capacity: float = 60.0, refill_rate: float = 1.0):
        self._capacity = capacity
        self._refill_rate = refill_rate
        self._buckets: Dict[str, _Bucket] = {}
        self._lock = threading.Lock()

    def allow(self, identity: str, cost: float = 1.0) -> bool:
        with self._lock:
            if identity not in self._buckets:
                self._buckets[identity] = _Bucket(self._capacity, self._refill_rate)
            return self._buckets[identity].consume(cost)

    def reset(self, identity: str) -> None:
        with self._lock:
            self._buckets.pop(identity, None)
