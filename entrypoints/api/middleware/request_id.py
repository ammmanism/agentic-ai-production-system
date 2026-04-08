"""
Request ID middleware for distributed tracing correlation.

This module provides middleware that injects and propagates correlation IDs
(request IDs) across all requests for distributed tracing and log aggregation.
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware for injecting and propagating request correlation IDs.

    This middleware ensures every request has a unique identifier that can be
    used for:
    - Distributed tracing across microservices
    - Log aggregation and filtering
    - Request debugging and auditing
    - Performance monitoring

    The request ID is:
    1. Extracted from incoming headers if present (X-Request-ID or X-Correlation-ID)
    2. Generated as a new UUID if not present
    3. Added to request state for use in route handlers
    4. Included in all response headers
    5. Added to all log records via context
    """

    def __init__(
        self,
        app,
        header_name: str = "X-Request-ID",
        correlation_header_name: str = "X-Correlation-ID",
    ) -> None:
        """
        Initialize the Request ID middleware.

        Args:
            app: The FastAPI application.
            header_name: Primary header name for request ID.
            correlation_header_name: Secondary header name for correlation ID.
        """
        super().__init__(app)
        self.header_name = header_name
        self.correlation_header_name = correlation_header_name
        logger.info(
            "request_id_middleware_initialized",
            header_name=self.header_name,
            correlation_header_name=self.correlation_header_name,
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request with request ID injection and propagation.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or route handler.

        Returns:
            Response: HTTP response with request ID headers.
        """
        # Extract or generate request ID
        request_id = self._extract_request_id(request)

        # Store in request state for use in route handlers
        setattr(request.state, "request_id", request_id)

        # Add to log context for structured logging
        with logger.contextualize(request_id=request_id):
            logger.debug(
                "request_started",
                method=request.method,
                path=request.url.path,
                query=str(request.url.query) if request.url.query else None,
                client_ip=self._get_client_ip(request),
            )

            try:
                # Process the request
                response = await call_next(request)

                # Add request ID to response headers
                response.headers[self.header_name] = request_id
                response.headers[self.correlation_header_name] = request_id

                logger.debug(
                    "request_completed",
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    request_id=request_id,
                )

                return response

            except Exception as e:
                logger.error(
                    "request_failed",
                    method=request.method,
                    path=request.url.path,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    request_id=request_id,
                    exc_info=True,
                )
                raise

    def _extract_request_id(self, request: Request) -> str:
        """
        Extract request ID from headers or generate a new one.

        Priority:
        1. X-Request-ID header
        2. X-Correlation-ID header
        3. Generate new UUID

        Args:
            request: The incoming HTTP request.

        Returns:
            str: Request ID string.
        """
        # Check primary header
        request_id = request.headers.get(self.header_name)
        if request_id:
            logger.debug("request_id_extracted_from_header", header_name=self.header_name)
            return request_id

        # Check correlation header
        correlation_id = request.headers.get(self.correlation_header_name)
        if correlation_id:
            logger.debug(
                "correlation_id_extracted_from_header",
                header_name=self.correlation_header_name,
            )
            return correlation_id

        # Generate new UUID
        request_id = f"req_{uuid.uuid4().hex[:16]}"
        logger.debug("request_id_generated", request_id=request_id)
        return request_id

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.

        Args:
            request: The incoming HTTP request.

        Returns:
            str: Client IP address.
        """
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        if request.client:
            return request.client.host

        return "unknown"


def get_request_id(request: Request) -> str:
    """
    Helper function to extract request ID from request state.

    This function should be used in route handlers to access the request ID
    that was set by the middleware.

    Args:
        request: The FastAPI Request object.

    Returns:
        str: The request ID, or 'unknown' if not found.

    Example:
        ```python
        @router.post("/endpoint")
        async def my_endpoint(request: Request):
            request_id = get_request_id(request)
            logger.info("Processing request", request_id=request_id)
        ```
    """
    return getattr(request.state, "request_id", "unknown")


def generate_request_id() -> str:
    """
    Generate a new unique request ID.

    Returns:
        str: A new request ID in the format 'req_<uuid_hex>'.
    """
    return f"req_{uuid.uuid4().hex[:16]}"


class RequestContextManager:
    """
    Context manager for request-scoped logging context.

    This class provides a convenient way to add request-specific context
    to all log messages within a scope.

    Example:
        ```python
        async with RequestContextManager(request_id="req_abc123"):
            logger.info("This log includes request context")
        ```
    """

    def __init__(self, **context_kwargs) -> None:
        """
        Initialize the context manager with logging context.

        Args:
            **context_kwargs: Key-value pairs to add to log context.
        """
        self.context_kwargs = context_kwargs
        self.context_token = None

    def __enter__(self) -> "RequestContextManager":
        """Enter the context and apply log context."""
        self.context_token = logger.contextualize(**self.context_kwargs)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context and restore previous log context."""
        if self.context_token:
            self.context_token.__exit__(exc_type, exc_val, exc_tb)

    async def __aenter__(self) -> "RequestContextManager":
        """Async enter the context and apply log context."""
        self.context_token = logger.contextualize(**self.context_kwargs)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async exit the context and restore previous log context."""
        if self.context_token:
            self.context_token.__exit__(exc_type, exc_val, exc_tb)
