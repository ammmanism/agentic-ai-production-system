"""
API route handlers for user feedback (RLHF) collection.

This module provides the /feedback endpoint for collecting user feedback
on chat responses, which is used for Reinforcement Learning from Human Feedback.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Request, status
from loguru import logger

from entrypoints.api.schemas import FeedbackRequest, FeedbackResponse, FeedbackType


router = APIRouter()


# Mock feedback storage (in production, this would be a database)
class MockFeedbackStore:
    """
    Mock feedback storage simulating database behavior.

    This class demonstrates the interface that would be used with a
    real database (PostgreSQL/MongoDB) in production.
    """

    def __init__(self) -> None:
        """Initialize the mock feedback store with an empty storage dict."""
        self._feedback_records: Dict[str, Dict[str, Any]] = {}

    def store_feedback(
        self,
        conversation_id: str,
        feedback_type: FeedbackType,
        rating: Optional[int] = None,
        comment: Optional[str] = None,
        message_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store a new feedback record.

        Args:
            conversation_id: ID of the conversation being rated.
            feedback_type: Type of feedback (thumbs_up, thumbs_down, comment).
            rating: Optional numeric rating (1-5).
            comment: Optional text comment.
            message_id: Optional ID of specific message being rated.
            metadata: Additional metadata about the feedback.

        Returns:
            str: Unique feedback record identifier.
        """
        feedback_id = f"fb_{uuid.uuid4().hex[:12]}"
        self._feedback_records[feedback_id] = {
            "feedback_id": feedback_id,
            "conversation_id": conversation_id,
            "feedback_type": feedback_type.value if isinstance(feedback_type, FeedbackType) else feedback_type,
            "rating": rating,
            "comment": comment,
            "message_id": message_id,
            "metadata": metadata or {},
            "created_at": datetime.utcnow(),
            "processed": False,
        }
        logger.info(
            "feedback_stored",
            feedback_id=feedback_id,
            conversation_id=conversation_id,
            feedback_type=feedback_type,
        )
        return feedback_id

    def get_feedback(self, feedback_id: str) -> Dict[str, Any] | None:
        """
        Retrieve a feedback record by ID.

        Args:
            feedback_id: Unique feedback identifier.

        Returns:
            Dict containing feedback data or None if not found.
        """
        return self._feedback_records.get(feedback_id)

    def get_conversation_feedback(
        self, conversation_id: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all feedback records for a conversation.

        Args:
            conversation_id: Conversation identifier.

        Returns:
            List of feedback records for the conversation.
        """
        return [
            record
            for record in self._feedback_records.values()
            if record["conversation_id"] == conversation_id
        ]

    def get_feedback_stats(self) -> Dict[str, Any]:
        """
        Get aggregate feedback statistics.

        Returns:
            Dict containing feedback statistics.
        """
        total = len(self._feedback_records)
        thumbs_up = sum(
            1
            for r in self._feedback_records.values()
            if r["feedback_type"] == "thumbs_up"
        )
        thumbs_down = sum(
            1
            for r in self._feedback_records.values()
            if r["feedback_type"] == "thumbs_down"
        )
        comments = sum(
            1
            for r in self._feedback_records.values()
            if r["feedback_type"] == "comment" or r["comment"]
        )

        avg_rating = 0.0
        ratings = [
            r["rating"]
            for r in self._feedback_records.values()
            if r["rating"] is not None
        ]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)

        return {
            "total_feedback": total,
            "thumbs_up": thumbs_up,
            "thumbs_down": thumbs_down,
            "comments": comments,
            "average_rating": round(avg_rating, 2),
            "satisfaction_rate": round(thumbs_up / total * 100, 2) if total > 0 else 0.0,
        }


# Global mock feedback store instance
feedback_store = MockFeedbackStore()


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    req: Request,
) -> FeedbackResponse:
    """
    Submit user feedback for RLHF (Reinforcement Learning from Human Feedback).

    This endpoint collects user feedback on chat responses, including:
    - Thumbs up/down ratings
    - Numeric ratings (1-5)
    - Text comments
    - Message-specific feedback

    The collected feedback is used to improve model performance through
    reinforcement learning techniques.

    Args:
        request: Validated FeedbackRequest containing feedback data.
        req: FastAPI Request object for metadata extraction.

    Returns:
        FeedbackResponse: Confirmation with feedback ID and timestamp.

    Raises:
        HTTPException: If request validation fails.
    """
    request_id = getattr(req.state, "request_id", str(uuid.uuid4()))

    logger.info(
        "feedback_request_started",
        request_id=request_id,
        conversation_id=request.conversation_id,
        feedback_type=request.feedback_type.value,
        has_rating=request.rating is not None,
        has_comment=request.comment is not None,
        message_id=request.message_id,
    )

    try:
        # Validate request using Pydantic
        validated_request = FeedbackRequest.model_validate(request.model_dump())

        # Prepare metadata
        metadata = {
            "request_id": request_id,
            "user_agent": req.headers.get("user-agent", "unknown"),
            "ip_address": req.client.host if req.client else "unknown",
        }

        # Store feedback
        feedback_id = feedback_store.store_feedback(
            conversation_id=validated_request.conversation_id,
            feedback_type=validated_request.feedback_type,
            rating=validated_request.rating,
            comment=validated_request.comment,
            message_id=validated_request.message_id,
            metadata=metadata,
        )

        logger.info(
            "feedback_recorded",
            request_id=request_id,
            feedback_id=feedback_id,
            conversation_id=validated_request.conversation_id,
        )

        return FeedbackResponse(
            feedback_id=feedback_id,
            status="recorded",
            message="Thank you for your feedback!",
            recorded_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(
            "feedback_submission_failed",
            request_id=request_id,
            conversation_id=request.conversation_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True,
        )
        raise


@router.get("/feedback/{feedback_id}")
async def get_feedback(
    feedback_id: str,
    req: Request,
) -> Dict[str, Any]:
    """
    Retrieve a specific feedback record.

    Args:
        feedback_id: Unique feedback identifier.
        req: FastAPI Request object for metadata.

    Returns:
        dict: Feedback record data.

    Raises:
        HTTPException: If feedback is not found.
    """
    request_id = getattr(req.state, "request_id", str(uuid.uuid4()))

    logger.info(
        "feedback_lookup",
        request_id=request_id,
        feedback_id=feedback_id,
    )

    feedback_record = feedback_store.get_feedback(feedback_id)

    if not feedback_record:
        logger.warning(
            "feedback_not_found",
            request_id=request_id,
            feedback_id=feedback_id,
        )
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback {feedback_id} not found",
        )

    # Convert datetime to ISO format for JSON serialization
    result = feedback_record.copy()
    result["created_at"] = feedback_record["created_at"].isoformat()

    return result


@router.get("/feedback/conversation/{conversation_id}")
async def get_conversation_feedback_list(
    conversation_id: str,
    req: Request,
) -> Dict[str, Any]:
    """
    Retrieve all feedback records for a specific conversation.

    Args:
        conversation_id: Conversation identifier.
        req: FastAPI Request object for metadata.

    Returns:
        dict: List of feedback records for the conversation.
    """
    request_id = getattr(req.state, "request_id", str(uuid.uuid4()))

    logger.info(
        "conversation_feedback_lookup",
        request_id=request_id,
        conversation_id=conversation_id,
    )

    feedback_records = feedback_store.get_conversation_feedback(conversation_id)

    # Convert datetimes to ISO format
    serialized_records = []
    for record in feedback_records:
        serialized = record.copy()
        serialized["created_at"] = record["created_at"].isoformat()
        serialized_records.append(serialized)

    return {
        "conversation_id": conversation_id,
        "feedback_count": len(serialized_records),
        "feedback": serialized_records,
        "request_id": request_id,
    }


@router.get("/feedback/stats")
async def get_feedback_statistics(
    req: Request,
) -> Dict[str, Any]:
    """
    Get aggregate feedback statistics for monitoring and analytics.

    Args:
        req: FastAPI Request object for metadata.

    Returns:
        dict: Aggregate feedback statistics.
    """
    request_id = getattr(req.state, "request_id", str(uuid.uuid4()))

    logger.info(
        "feedback_stats_requested",
        request_id=request_id,
    )

    stats = feedback_store.get_feedback_stats()
    stats["request_id"] = request_id
    stats["generated_at"] = datetime.utcnow().isoformat()

    return stats
