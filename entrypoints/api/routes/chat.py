"""POST /chat/stream — streaming chat endpoint."""
from __future__ import annotations

import time
import uuid

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..schemas import ChatRequest, ChatResponse
from orchestration.graph.compiler import build_agent_graph

router = APIRouter()
_graph = build_agent_graph()

@router.post("/stream", response_model=ChatResponse)
async def chat_stream(request: ChatRequest):
    """Handle a chat query, optionally streaming tokens."""
    start = time.monotonic()

    final_state = _graph.invoke({
        "query": request.query,
        "messages": [],
        "plan": None,
        "current_step": 0,
        "tool_results": [],
        "final_answer": None,
        "needs_replan": False,
        "replan_count": 0,
        "context": None,
        "metadata": {}
    })
    
    answer = final_state.get("final_answer") or "[Agent failed to generate response]"

    latency_ms = (time.monotonic() - start) * 1000

    return ChatResponse(
        session_id=request.session_id,
        answer=answer,
        sources=[],
        latency_ms=round(latency_ms, 2),
        cost_cents=0.0,
    )
