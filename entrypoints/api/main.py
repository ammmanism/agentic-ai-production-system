from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from entrypoints.api.routes import chat, ingest, feedback, health
from core.config import settings
from entrypoints.api.middleware.rate_limit import RateLimitMiddleware, get_rate_limiter
from entrypoints.api.middleware.request_id import RequestIdMiddleware

logger = logging.getLogger(__name__)

# Basic lifespan for starting heavy resources (vLLM, Qdrant pools, etc)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing Agentic AI System resources...")
    start_time = time.time()
    
    # Initialize Rate Limiter globally accessible via app state
    app.state.rate_limiter = get_rate_limiter()
    
    logger.info(f"System ready in {time.time() - start_time:.2f}s")
    yield
    
    # Shutdown actions
    logger.info("Shutting down cleanly, flushing telemetry...")

# Initialize FastAPI with extensive OpenAPI docs
app = FastAPI(
    title="Agentic AI Production System",
    description="High-throughput RAG agent system with streaming capabilities and extreme safety boundaries.",
    version="1.0.0",
    lifespan=lifespan
)

# Custom Middlewares
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production needs explicit origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Agent Chat"])

# Full Production Endpoints
app.include_router(ingest.router, prefix="/api/v1/ingest", tags=["Document Ingestion"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["Human Feedback"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Agentic Production System. Check /docs for interactive API reference."}
