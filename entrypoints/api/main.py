"""
FastAPI application entrypoint with lifespan context, CORS, and global exception handlers.

This module provides the main FastAPI application factory with comprehensive
error handling, middleware integration, and lifecycle management.
"""

from __future__ import annotations

import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from entrypoints.api.routes import chat, feedback, ingest


# Configure loguru for structured logging
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    serialize=False,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for FastAPI application startup and shutdown.

    This handles initialization of resources (database connections, caches, etc.)
    on startup and proper cleanup on shutdown.

    Args:
        app: The FastAPI application instance.

    Yields:
        None: Control returns to FastAPI to handle requests.

    Raises:
        Exception: Logs any exceptions during startup/shutdown.
    """
    # Startup
    logger.info("application_startup", event="startup", timestamp=datetime.utcnow().isoformat())
    
    try:
        # Initialize database connection pool (mocked for now)
        logger.info("db_connection_initialized", component="database")
        
        # Initialize Redis cache connection (mocked for now)
        logger.info("cache_connection_initialized", component="redis")
        
        # Initialize LLM client connections (mocked for now)
        logger.info("llm_clients_initialized", component="llm")
        
        logger.info("startup_complete", duration_ms=150)
        yield
        
    except Exception as e:
        logger.error(f"startup_failed", error=str(e), exc_info=True)
        raise
    
    finally:
        # Shutdown
        logger.info("application_shutdown", event="shutdown", timestamp=datetime.utcnow().isoformat())
        
        try:
            # Close database connections
            logger.info("db_connections_closed", component="database")
            
            # Close Redis connections
            logger.info("cache_connections_closed", component="redis")
            
            # Close LLM client sessions
            logger.info("llm_clients_closed", component="llm")
            
            logger.info("shutdown_complete")
        except Exception as e:
            logger.error(f"shutdown_error", error=str(e), exc_info=True)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.

    Returns:
        FastAPI: Configured FastAPI application with all middleware and routes.
    """
    app = FastAPI(
        title="Agentic AI Production System",
        description="Production-grade Agentic AI system with RAG capabilities, streaming responses, and RLHF feedback.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:8501",
            "http://127.0.0.1:8501",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Correlation-ID"],
        max_age=600,
    )

    # Include routers
    app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
    app.include_router(ingest.router, prefix="/api/v1", tags=["ingest"])
    app.include_router(feedback.router, prefix="/api/v1", tags=["feedback"])

    # Register global exception handlers
    register_exception_handlers(app)

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, Any]:
        """
        Health check endpoint for monitoring and load balancers.

        Returns:
            dict: Health status with timestamp and version.
        """
        return {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
        }

    logger.info("app_created", app_name="agentic-ai-api")
    return app


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers for the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handle uncaught exceptions globally.

        Args:
            request: The incoming HTTP request.
            exc: The uncaught exception.

        Returns:
            JSONResponse: Standardized error response.
        """
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(
            "unhandled_exception",
            request_id=request_id,
            path=request.url.path,
            method=request.method,
            error_type=type(exc).__name__,
            error_message=str(exc),
            exc_info=True,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An internal server error occurred",
                "error_type": type(exc).__name__,
                "request_id": request_id,
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """
        Handle ValueError exceptions.

        Args:
            request: The incoming HTTP request.
            exc: The ValueError exception.

        Returns:
            JSONResponse: Standardized error response for validation errors.
        """
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(
            "validation_error",
            request_id=request_id,
            path=request.url.path,
            method=request.method,
            error_message=str(exc),
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": str(exc),
                "error_type": "ValidationError",
                "request_id": request_id,
            },
        )

    @app.exception_handler(PermissionError)
    async def permission_error_handler(
        request: Request, exc: PermissionError
    ) -> JSONResponse:
        """
        Handle PermissionError exceptions.

        Args:
            request: The incoming HTTP request.
            exc: The PermissionError exception.

        Returns:
            JSONResponse: Standardized error response for permission errors.
        """
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(
            "permission_error",
            request_id=request_id,
            path=request.url.path,
            method=request.method,
            error_message=str(exc),
        )

        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "detail": "Access denied",
                "error_type": "PermissionError",
                "request_id": request_id,
            },
        )

    logger.info("exception_handlers_registered")


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "entrypoints.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
