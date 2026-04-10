"""POST /feedback — user feedback collection endpoint."""
from __future__ import annotations

from fastapi import APIRouter

from ..schemas import FeedbackRequest, FeedbackResponse
from human_in_loop.feedback_store import FeedbackStore

router = APIRouter()
_feedback_store = FeedbackStore()


@router.post("", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """Store user 👍/👎 ratings for RLHF / active learning."""
    _feedback_store.record(
        session_id=request.session_id,
        message_id=request.message_id,
        rating=request.rating,
        comment=request.comment or "",
    )
    return FeedbackResponse(accepted=True)
