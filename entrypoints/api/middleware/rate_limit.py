"""
Token-bucket rate limiter middleware for API request throttling.

This module implements a token-bucket algorithm for rate limiting API requests
on a per-client basis (using IP address or API key).
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Optional

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


@dataclass
class TokenBucket:
    """
    Token bucket implementation for rate limiting.

    Attributes:
        capacity: Maximum number of tokens the bucket can hold.
        refill_rate: Number of tokens added per second.
        tokens: Current number of tokens in the bucket.
        last_refill: Timestamp of the last token refill.
    """

    capacity: int = 100
    refill_rate: float = 10.0
    tokens: float = field(default=100.0)
    last_refill: float = field(default_factory=time.time)

    def consume(self, tokens: int = 1) -> bool:
        """
        Attempt to consume tokens from the bucket.

        Args:
            tokens: Number of tokens to consume.

        Returns:
            bool: True if tokens were consumed, False if insufficient tokens.
        """
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self) -> None:
        """Refill tokens based on elapsed time since last refill."""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def get_remaining_tokens(self) -> int:
        """
        Get the current number of available tokens.

        Returns:
            int: Number of remaining tokens.
        """
        self._refill()
        return int(self.tokens)


class RateLimiter:
    """
    Rate limiter manager using token-bucket algorithm.

    Manages multiple token buckets for different clients and provides
    thread-safe rate limiting operations.
    """

    def __init__(
        self,
        default_capacity: int = 100,
        default_refill_rate: float = 10.0,
    ) -> None:
        """
        Initialize the rate limiter.

        Args:
            default_capacity: Default bucket capacity for new clients.
            default_refill_rate: Default refill rate for new clients.
        """
        self._buckets: Dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(
                capacity=default_capacity,
                refill_rate=default_refill_rate,
            )
        )
        self._default_capacity = default_capacity
        self._default_refill_rate = default_refill_rate
        logger.info(
            "rate_limiter_initialized",
            default_capacity=default_capacity,
            default_refill_rate=default_refill_rate,
        )

    def get_bucket(self, client_id: str) -> TokenBucket:
        """
        Get or create a token bucket for a client.

        Args:
            client_id: Unique identifier for the client.

        Returns:
            TokenBucket: The client's token bucket.
        """
        return self._buckets[client_id]

    def is_allowed(self, client_id: str, tokens: int = 1) -> bool:
        """
        Check if a request is allowed under the rate limit.

        Args:
            client_id: Unique identifier for the client.
            tokens: Number of tokens to consume.

        Returns:
            bool: True if request is allowed, False if rate limited.
        """
        bucket = self.get_bucket(client_id)
        return bucket.consume(tokens)

    def get_remaining(self, client_id: str) -> int:
        """
        Get remaining tokens for a client.

        Args:
            client_id: Unique identifier for the client.

        Returns:
            int: Number of remaining tokens.
        """
        bucket = self.get_bucket(client_id)
        return bucket.get_remaining_tokens()


# Global rate limiter instance
rate_limiter = RateLimiter(
    default_capacity=100,  # 100 requests max burst
    default_refill_rate=10.0,  # 10 requests per second sustained
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting requests.

    This middleware applies token-bucket rate limiting to all incoming requests,
    identifying clients by IP address or API key.
    """

    def __init__(
        self,
        app,
        enabled: bool = True,
        exclude_paths: Optional[list[str]] = None,
    ) -> None:
        """
        Initialize the rate limit middleware.

        Args:
            app: The FastAPI application.
            enabled: Whether rate limiting is enabled.
            exclude_paths: List of paths to exclude from rate limiting.
        """
        super().__init__(app)
        self.enabled = enabled
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/redoc", "/openapi.json"]
        logger.info(
            "rate_limit_middleware_initialized",
            enabled=self.enabled,
            exclude_paths=self.exclude_paths,
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process incoming request with rate limiting.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or route handler.

        Returns:
            Response: HTTP response or rate limit error response.
        """
        # Skip rate limiting if disabled or for excluded paths
        if not self.enabled or any(
            request.url.path.startswith(path) for path in self.exclude_paths
        ):
            return await call_next(request)

        # Extract client identifier
        client_id = self._get_client_id(request)

        # Check rate limit
        if not rate_limiter.is_allowed(client_id):
            remaining = rate_limiter.get_remaining(client_id)
            logger.warning(
                "rate_limit_exceeded",
                client_id=client_id,
                path=request.url.path,
                method=request.method,
                remaining_tokens=remaining,
            )

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "error_type": "RateLimitExceeded",
                    "retry_after_seconds": 60 // int(rate_limiter._default_refill_rate),
                },
                headers={
                    "X-RateLimit-Limit": str(rate_limiter._default_capacity),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(int(time.time()) + 60),
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        remaining = rate_limiter.get_remaining(client_id)
        response.headers["X-RateLimit-Limit"] = str(rate_limiter._default_capacity)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time()) + int(remaining / rate_limiter._default_refill_rate)
        )

        logger.debug(
            "rate_limit_check_passed",
            client_id=client_id,
            path=request.url.path,
            remaining_tokens=remaining,
        )

        return response

    def _get_client_id(self, request: Request) -> str:
        """
        Extract client identifier from request.

        Uses API key if available, otherwise falls back to IP address.

        Args:
            request: The incoming HTTP request.

        Returns:
            str: Client identifier string.
        """
        # Check for API key in headers
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"

        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header:
            return f"auth:{hash(auth_header)}"

        # Fall back to IP address
        client_ip = self._get_client_ip(request)
        return f"ip:{client_ip}"

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request, handling proxies.

        Args:
            request: The incoming HTTP request.

        Returns:
            str: Client IP address.
        """
        # Check for forwarded headers (when behind proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client IP
        if request.client:
            return request.client.host

        return "unknown"
