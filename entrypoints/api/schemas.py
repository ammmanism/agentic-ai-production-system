"""Pydantic schemas for all API endpoints."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session / conversation id")
    query: str = Field(..., min_length=1, max_length=4096)
    stream: bool = Field(default=False)


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: List[Dict[str, Any]] = []
    latency_ms: float
    cost_cents: float


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------

class IngestRequest(BaseModel):
    documents: List[Dict[str, str]] = Field(
        ..., description="List of {id, text, metadata} dicts"
    )
    collection: str = Field(default="default")


class IngestResponse(BaseModel):
    ingested: int
    collection: str


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------

class FeedbackRequest(BaseModel):
    session_id: str
    message_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    accepted: bool
