"""FastAPI application with lifespan event handling."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .middleware.request_id import RequestIdMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .routes import chat, ingest, feedback

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle events."""
    logger.info("Starting Agentic AI API...")
    # Initialise connections (vector DB, Redis, etc.) here
    yield
    logger.info("Shutting down Agentic AI API...")


app = FastAPI(
    title="Agentic AI Production System",
    description="Production-ready agentic RAG API with safety, observability, and evaluation.",
    version="0.1.0",
    lifespan=lifespan,
)

# ----- Middleware -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(RateLimitMiddleware)

# ----- Routers -----
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(feedback.router, prefix="/feedback", tags=["feedback"])


@app.get("/health")
async def health_check():
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "Agentic AI Production System — visit /docs for the API reference."}
