"""
Pydantic v2 schemas for the Agentic AI API.

This module defines all request/response models used across the FastAPI endpoints.
All schemas use Pydantic v2 features including Field descriptions, examples,
and model validators for data integrity.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class FeedbackType(str, Enum):
    """Enum representing the type of feedback that can be submitted."""

    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    COMMENT = "comment"


class ChatRequest(BaseModel):
    """
    Request schema for chat interactions.

    Attributes:
        message: The user's input message to the agent.
        conversation_id: Optional conversation ID for maintaining context.
        session_id: Optional session identifier for tracking user sessions.
        metadata: Optional additional metadata for the request.
    """

    message: str = Field(
        ...,
        description="The user's input message to the agent",
        min_length=1,
        max_length=10000,
        examples=["What is the weather like today?"],
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional conversation ID for maintaining context across multiple turns",
        examples=["conv_12345"],
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session identifier for tracking user sessions",
        examples=["sess_abcde"],
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional additional metadata for the request",
        examples=[{"user_agent": "Mozilla/5.0", "timezone": "UTC"}],
    )

    @field_validator("message")
    @classmethod
    def validate_message_not_empty(cls, v: str) -> str:
        """
        Validate that the message is not empty or whitespace-only.

        Args:
            v: The message string to validate.

        Returns:
            The validated message string.

        Raises:
            ValueError: If the message is empty or whitespace-only.
        """
        if not v.strip():
            raise ValueError("Message cannot be empty or whitespace-only")
        return v

    @model_validator(mode="after")
    def set_default_session_id(self) -> "ChatRequest":
        """
        Set a default session_id if not provided.

        Returns:
            The ChatRequest instance with session_id set.
        """
        if self.session_id is None:
            import uuid

            self.session_id = f"sess_{uuid.uuid4().hex[:8]}"
        return self


class ChatResponseChunk(BaseModel):
    """
    Response schema for streaming chat responses (SSE).

    Attributes:
        chunk: The text chunk being streamed.
        conversation_id: The conversation ID associated with this response.
        is_last: Whether this is the final chunk in the stream.
        metadata: Optional metadata about the chunk.
    """

    chunk: str = Field(
        ...,
        description="The text chunk being streamed",
        examples=["Hello! How can I help you today?"],
    )
    conversation_id: str = Field(
        ...,
        description="The conversation ID associated with this response",
        examples=["conv_12345"],
    )
    is_last: bool = Field(
        default=False,
        description="Whether this is the final chunk in the stream",
        examples=[False],
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata about the chunk",
        examples=[{"token_count": 5, "latency_ms": 120}],
    )


class IngestRequest(BaseModel):
    """
    Request schema for document ingestion.

    Attributes:
        document_url: URL to the document to ingest (PDF or TXT).
        document_content: Raw document content (alternative to URL).
        document_type: Type of document (pdf or txt).
        metadata: Optional metadata about the document.
        priority: Processing priority (low, normal, high).
    """

    document_url: Optional[str] = Field(
        default=None,
        description="URL to the document to ingest (PDF or TXT)",
        examples=["https://example.com/document.pdf"],
    )
    document_content: Optional[str] = Field(
        default=None,
        description="Raw document content as an alternative to providing a URL",
        examples=["This is the raw text content of the document..."],
    )
    document_type: str = Field(
        ...,
        description="Type of document being ingested",
        pattern="^(pdf|txt)$",
        examples=["pdf"],
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata about the document",
        examples=[{"author": "John Doe", "title": "Annual Report"}],
    )
    priority: str = Field(
        default="normal",
        description="Processing priority level",
        pattern="^(low|normal|high)$",
        examples=["normal"],
    )

    @model_validator(mode="after")
    def validate_document_source(self) -> "IngestRequest":
        """
        Validate that either document_url or document_content is provided.

        Returns:
            The IngestRequest instance.

        Raises:
            ValueError: If neither document_url nor document_content is provided.
        """
        if not self.document_url and not self.document_content:
            raise ValueError(
                "Either 'document_url' or 'document_content' must be provided"
            )
        return self


class IngestResponse(BaseModel):
    """
    Response schema for document ingestion requests.

    Attributes:
        task_id: Unique identifier for the ingestion task.
        status: Current status of the ingestion task.
        message: Human-readable status message.
        estimated_time_seconds: Estimated processing time in seconds.
    """

    task_id: str = Field(
        ...,
        description="Unique identifier for the ingestion task",
        examples=["task_67890"],
    )
    status: str = Field(
        ...,
        description="Current status of the ingestion task",
        examples=["queued"],
    )
    message: str = Field(
        ...,
        description="Human-readable status message",
        examples=["Document queued for processing"],
    )
    estimated_time_seconds: Optional[int] = Field(
        default=None,
        description="Estimated processing time in seconds",
        examples=[30],
    )


class FeedbackRequest(BaseModel):
    """
    Request schema for submitting user feedback (RLHF).

    Attributes:
        conversation_id: The conversation ID being rated.
        feedback_type: Type of feedback (thumbs_up, thumbs_down, comment).
        rating: Optional numeric rating (1-5).
        comment: Optional text comment from the user.
        message_id: Optional ID of the specific message being rated.
    """

    conversation_id: str = Field(
        ...,
        description="The conversation ID being rated",
        examples=["conv_12345"],
    )
    feedback_type: FeedbackType = Field(
        ...,
        description="Type of feedback being submitted",
        examples=["thumbs_up"],
    )
    rating: Optional[int] = Field(
        default=None,
        description="Optional numeric rating from 1 to 5",
        ge=1,
        le=5,
        examples=[5],
    )
    comment: Optional[str] = Field(
        default=None,
        description="Optional text comment from the user",
        max_length=2000,
        examples=["This response was very helpful!"],
    )
    message_id: Optional[str] = Field(
        default=None,
        description="Optional ID of the specific message being rated",
        examples=["msg_abc123"],
    )

    @field_validator("comment")
    @classmethod
    def validate_comment_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate that if a comment is provided, it's not empty.

        Args:
            v: The comment string to validate.

        Returns:
            The validated comment string or None.
        """
        if v is not None and not v.strip():
            raise ValueError("Comment cannot be empty or whitespace-only")
        return v


class FeedbackResponse(BaseModel):
    """
    Response schema for feedback submission.

    Attributes:
        feedback_id: Unique identifier for the feedback record.
        status: Status of the feedback submission.
        message: Human-readable confirmation message.
        recorded_at: Timestamp when the feedback was recorded.
    """

    feedback_id: str = Field(
        ...,
        description="Unique identifier for the feedback record",
        examples=["fb_xyz789"],
    )
    status: str = Field(
        ...,
        description="Status of the feedback submission",
        examples=["recorded"],
    )
    message: str = Field(
        ...,
        description="Human-readable confirmation message",
        examples=["Thank you for your feedback!"],
    )
    recorded_at: datetime = Field(
        ...,
        description="Timestamp when the feedback was recorded",
        examples=["2024-01-15T10:30:00Z"],
    )


class HealthResponse(BaseModel):
    """
    Response schema for health check endpoint.

    Attributes:
        status: Overall health status.
        version: API version string.
        timestamp: Current server timestamp.
        components: Status of individual system components.
    """

    status: str = Field(
        ...,
        description="Overall health status",
        examples=["healthy"],
    )
    version: str = Field(
        ...,
        description="API version string",
        examples=["1.0.0"],
    )
    timestamp: datetime = Field(
        ...,
        description="Current server timestamp",
        examples=["2024-01-15T10:30:00Z"],
    )
    components: Dict[str, str] = Field(
        default_factory=dict,
        description="Status of individual system components",
        examples={"database": "healthy", "cache": "healthy"},
    )
