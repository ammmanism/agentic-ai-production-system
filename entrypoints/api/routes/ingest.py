"""
API route handlers for document ingestion.

This module provides the /ingest endpoint for queuing PDF and text documents
for background processing by the Celery worker system.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import APIRouter, Request, status
from loguru import logger

from entrypoints.api.schemas import IngestRequest, IngestResponse


router = APIRouter()


# Mock task queue for demonstration (in production, this would be Celery/Redis)
class MockTaskQueue:
    """
    Mock task queue simulating Celery/Redis behavior.

    This class demonstrates the interface that would be used with Celery
    in a production environment.
    """

    def __init__(self) -> None:
        """Initialize the mock task queue with an empty task store."""
        self._tasks: Dict[str, Dict[str, Any]] = {}

    def enqueue_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: str = "normal",
    ) -> str:
        """
        Enqueue a new task for background processing.

        Args:
            task_type: Type of task (e.g., 'document_ingest').
            payload: Task payload containing document data.
            priority: Task priority level (low, normal, high).

        Returns:
            str: Unique task identifier.
        """
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        self._tasks[task_id] = {
            "task_id": task_id,
            "task_type": task_type,
            "payload": payload,
            "priority": priority,
            "status": "queued",
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "error": None,
        }
        logger.info(
            "task_enqueued",
            task_id=task_id,
            task_type=task_type,
            priority=priority,
        )
        return task_id

    def get_task_status(self, task_id: str) -> Dict[str, Any] | None:
        """
        Get the current status of a task.

        Args:
            task_id: Unique task identifier.

        Returns:
            Dict containing task status or None if not found.
        """
        return self._tasks.get(task_id)


# Global mock queue instance
task_queue = MockTaskQueue()


def estimate_processing_time(
    document_type: str,
    content_length: int = 0,
    priority: str = "normal",
) -> int:
    """
    Estimate processing time in seconds based on document characteristics.

    Args:
        document_type: Type of document (pdf or txt).
        content_length: Length of document content in bytes.
        priority: Processing priority level.

    Returns:
        int: Estimated processing time in seconds.
    """
    # Base processing times by document type
    base_times = {
        "txt": 5,
        "pdf": 15,  # PDFs require OCR and parsing
    }

    base_time = base_times.get(document_type, 10)

    # Adjust for content length (rough estimate)
    if content_length > 10000:
        base_time += (content_length // 10000) * 2

    # Adjust for priority
    priority_multipliers = {
        "high": 0.5,  # High priority gets more resources
        "normal": 1.0,
        "low": 1.5,  # Low priority may take longer
    }

    multiplier = priority_multipliers.get(priority, 1.0)
    estimated_time = int(base_time * multiplier)

    return max(estimated_time, 1)  # Minimum 1 second


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    request: IngestRequest,
    req: Request,
) -> IngestResponse:
    """
    Queue a document for background ingestion and processing.

    This endpoint accepts PDF or text documents (via URL or raw content)
    and queues them for asynchronous processing. The actual ingestion
    (chunking, embedding, indexing) is performed by background workers.

    Args:
        request: Validated IngestRequest containing document information.
        req: FastAPI Request object for metadata extraction.

    Returns:
        IngestResponse: Response containing task ID and status.

    Raises:
        HTTPException: If request validation fails or queue is unavailable.
    """
    request_id = getattr(req.state, "request_id", str(uuid.uuid4()))

    logger.info(
        "ingest_request_started",
        request_id=request_id,
        document_type=request.document_type,
        has_url=request.document_url is not None,
        has_content=request.document_content is not None,
        priority=request.priority,
        metadata_keys=list(request.metadata.keys()) if request.metadata else None,
    )

    try:
        # Validate request using Pydantic
        validated_request = IngestRequest.model_validate(request.model_dump())

        # Prepare task payload
        payload = {
            "document_url": validated_request.document_url,
            "document_content": validated_request.document_content,
            "document_type": validated_request.document_type,
            "metadata": validated_request.metadata,
            "request_id": request_id,
            "submitted_at": datetime.utcnow().isoformat(),
        }

        # Calculate content length for estimation
        content_length = 0
        if validated_request.document_content:
            content_length = len(validated_request.document_content.encode("utf-8"))
        elif validated_request.document_url:
            content_length = len(validated_request.document_url)

        # Estimate processing time
        estimated_time = estimate_processing_time(
            document_type=validated_request.document_type,
            content_length=content_length,
            priority=validated_request.priority,
        )

        # Enqueue task
        task_id = task_queue.enqueue_task(
            task_type="document_ingest",
            payload=payload,
            priority=validated_request.priority,
        )

        logger.info(
            "document_queued",
            request_id=request_id,
            task_id=task_id,
            estimated_time_seconds=estimated_time,
        )

        return IngestResponse(
            task_id=task_id,
            status="queued",
            message="Document queued for processing",
            estimated_time_seconds=estimated_time,
        )

    except Exception as e:
        logger.error(
            "ingest_request_failed",
            request_id=request_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True,
        )
        raise


@router.get("/ingest/{task_id}")
async def get_ingest_status(
    task_id: str,
    req: Request,
) -> Dict[str, Any]:
    """
    Get the current status of an ingestion task.

    Args:
        task_id: Unique task identifier.
        req: FastAPI Request object for metadata.

    Returns:
        dict: Task status including progress and result information.

    Raises:
        HTTPException: If task is not found.
    """
    request_id = getattr(req.state, "request_id", str(uuid.uuid4()))

    logger.info(
        "status_check_requested",
        request_id=request_id,
        task_id=task_id,
    )

    task_info = task_queue.get_task_status(task_id)

    if not task_info:
        logger.warning(
            "task_not_found",
            request_id=request_id,
            task_id=task_id,
        )
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    # Calculate progress (mock implementation)
    status_map = {
        "queued": 0,
        "processing": 50,
        "completed": 100,
        "failed": -1,
    }

    progress = status_map.get(task_info["status"], 0)

    return {
        "task_id": task_id,
        "status": task_info["status"],
        "progress_percent": progress,
        "created_at": task_info["created_at"].isoformat() if task_info["created_at"] else None,
        "started_at": task_info["started_at"].isoformat() if task_info["started_at"] else None,
        "completed_at": task_info["completed_at"].isoformat() if task_info["completed_at"] else None,
        "error": task_info["error"],
        "request_id": request_id,
    }


@router.delete("/ingest/{task_id}")
async def cancel_ingest_task(
    task_id: str,
    req: Request,
) -> Dict[str, Any]:
    """
    Cancel a pending or running ingestion task.

    Args:
        task_id: Unique task identifier.
        req: FastAPI Request object for metadata.

    Returns:
        dict: Cancellation confirmation.

    Raises:
        HTTPException: If task is not found or cannot be cancelled.
    """
    request_id = getattr(req.state, "request_id", str(uuid.uuid4()))

    logger.info(
        "cancel_requested",
        request_id=request_id,
        task_id=task_id,
    )

    task_info = task_queue.get_task_status(task_id)

    if not task_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    if task_info["status"] == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed task",
        )

    # Update task status
    task_info["status"] = "cancelled"
    task_info["completed_at"] = datetime.utcnow()

    logger.info(
        "task_cancelled",
        request_id=request_id,
        task_id=task_id,
    )

    return {
        "task_id": task_id,
        "status": "cancelled",
        "message": "Task successfully cancelled",
        "request_id": request_id,
    }
