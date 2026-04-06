"""POST /feedback — user feedback collection endpoint."""
from __future__ import annotations

from fastapi import APIRouter

from ..schemas import FeedbackRequest, FeedbackResponse

router = APIRouter()


@router.post("", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """Store user 👍/👎 ratings for RLHF / active learning."""
    # TODO: persist to human_in_loop.feedback_store
    return FeedbackResponse(accepted=True)
