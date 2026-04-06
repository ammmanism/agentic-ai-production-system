"""Exact-match TTL cache for deterministic LLM calls."""
from __future__ import annotations

import hashlib
import time
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class ExactCache:
    """
    Simple exact-match cache keyed on a hash of the request.

    Backed by a Python dict for local dev; swap out for Redis in prod:
        r = redis.Redis.from_url(os.getenv("REDIS_URL"))
        r.setex(key, ttl, value)
    """

    def __init__(self, ttl_seconds: int = 600):
        self._store: Dict[str, Tuple[str, float]] = {}
        self._ttl = ttl_seconds

    @staticmethod
    def _make_key(prompt: str, model: str) -> str:
        payload = f"{model}::{prompt}"
        return hashlib.sha256(payload.encode()).hexdigest()

    def get(self, prompt: str, model: str = "default") -> Optional[str]:
        key = self._make_key(prompt, model)
        entry = self._store.get(key)
        if entry is None:
            return None
        value, ts = entry
        if time.time() - ts > self._ttl:
            del self._store[key]
            return None
        logger.info("ExactCache HIT key=%s", key[:16])
        return value

    def set(self, prompt: str, answer: str, model: str = "default") -> None:
        key = self._make_key(prompt, model)
        self._store[key] = (answer, time.time())
        logger.info("ExactCache SET key=%s", key[:16])

    def invalidate(self, prompt: str, model: str = "default") -> None:
        key = self._make_key(prompt, model)
        self._store.pop(key, None)
