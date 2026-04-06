"""Simple in-memory rate limiter middleware (token bucket per IP)."""
from __future__ import annotations

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

RATE_LIMIT = 60   # requests per window
WINDOW_SEC = 60   # seconds


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit: int = RATE_LIMIT, window: int = WINDOW_SEC):
        super().__init__(app)
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._rate_limit = rate_limit
        self._window = window

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Remove expired timestamps
        self._hits[client_ip] = [
            t for t in self._hits[client_ip] if now - t < self._window
        ]

        if len(self._hits[client_ip]) >= self._rate_limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please retry later."},
            )

        self._hits[client_ip].append(now)
        return await call_next(request)
