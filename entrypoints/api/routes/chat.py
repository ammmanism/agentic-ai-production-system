from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import json
import logging
from typing import AsyncGenerator

from entrypoints.api.schemas import ChatRequest
from orchestration.graph.compiler import get_agent_graph

router = APIRouter()
logger = logging.getLogger(__name__)

async def stream_agent_events(query: str, session_id: str) -> AsyncGenerator[str, None]:
    """Streams Server-Sent Events (SSE) from the LangGraph execution."""
    graph = get_agent_graph()
    
    # Initial state configuration for LangGraph
    state = {
        "messages": [("user", query)],
        "session_id": session_id,
        "tools_called": []
    }
    
    try:
        # Asynchronous stream over the langgraph state machine
        async for event in graph.astream(state, {"configurable": {"thread_id": session_id}}):
            # The event dict represents the state output of the last executed node
            # Format as SSE
            yield f"data: {json.dumps(event)}\n\n"
            
        yield "event: close\ndata: [DONE]\n\n"
        
    except Exception as e:
        logger.error(f"Error executing agent graph: {e}")
        yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

@router.post("/stream")
async def chat_stream(request: ChatRequest, fast_req: Request):
    """
    Agent chat endpoint that streams reasoning steps and the final answer.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    return StreamingResponse(
        stream_agent_events(request.query, request.session_id),
        media_type="text/event-stream"
    )
