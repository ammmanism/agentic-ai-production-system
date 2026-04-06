"""POST /chat/stream — streaming chat endpoint."""
from __future__ import annotations

import time
import uuid

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/stream", response_model=ChatResponse)
async def chat_stream(request: ChatRequest):
    """Handle a chat query, optionally streaming tokens."""
    start = time.monotonic()

    # TODO: wire up orchestration.graph.compiler.build_agent_graph()
    answer = f"[Agent response to: {request.query}]"

    latency_ms = (time.monotonic() - start) * 1000

    return ChatResponse(
        session_id=request.session_id,
        answer=answer,
        sources=[],
        latency_ms=round(latency_ms, 2),
        cost_cents=0.0,
    )
