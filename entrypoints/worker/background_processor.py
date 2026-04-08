"""
Background worker for asynchronous document ingestion processing.

This module implements an asyncio-based worker that processes document
ingestion tasks from a queue, handling chunking, embedding, and indexing.
"""

from __future__ import annotations

import asyncio
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from loguru import logger


class TaskStatus(str, Enum):
    """Enum representing the status of a background task."""

    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class IngestionTask:
    """
    Represents a document ingestion task to be processed.

    Attributes:
        task_id: Unique identifier for the task.
        document_url: URL to the document (optional).
        document_content: Raw document content (optional).
        document_type: Type of document (pdf or txt).
        priority: Processing priority level.
        metadata: Additional task metadata.
        status: Current task status.
        created_at: Timestamp when task was created.
        started_at: Timestamp when processing started.
        completed_at: Timestamp when processing completed.
        error: Error message if task failed.
        result: Processing result if successful.
    """

    task_id: str
    document_url: Optional[str] = None
    document_content: Optional[str] = None
    document_type: str = "txt"
    priority: str = "normal"
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


class TaskQueue:
    """
    Priority queue for managing ingestion tasks.

    Tasks are ordered by priority (high > normal > low) and then by
    creation time (FIFO within same priority).
    """

    def __init__(self, max_size: int = 1000) -> None:
        """
        Initialize the task queue.

        Args:
            max_size: Maximum number of tasks the queue can hold.
        """
        self._queue: deque[IngestionTask] = deque()
        self._tasks: Dict[str, IngestionTask] = {}
        self._max_size = max_size
        self._lock = asyncio.Lock()
        logger.info(
            "task_queue_initialized",
            max_size=max_size,
        )

    async def enqueue(self, task: IngestionTask) -> bool:
        """
        Add a task to the queue.

        Args:
            task: The ingestion task to enqueue.

        Returns:
            bool: True if task was enqueued, False if queue is full.
        """
        async with self._lock:
            if len(self._queue) >= self._max_size:
                logger.warning(
                    "queue_full",
                    task_id=task.task_id,
                    queue_size=len(self._queue),
                )
                return False

            # Insert based on priority
            if task.priority == "high":
                self._queue.appendleft(task)
            else:
                self._queue.append(task)

            self._tasks[task.task_id] = task
            task.status = TaskStatus.QUEUED

            logger.info(
                "task_enqueued",
                task_id=task.task_id,
                priority=task.priority,
                queue_size=len(self._queue),
            )
            return True

    async def dequeue(self) -> Optional[IngestionTask]:
        """
        Remove and return the next task from the queue.

        Returns:
            Optional[IngestionTask]: Next task or None if queue is empty.
        """
        async with self._lock:
            if not self._queue:
                return None

            task = self._queue.popleft()
            logger.debug(
                "task_dequeued",
                task_id=task.task_id,
                queue_size=len(self._queue),
            )
            return task

    async def get_task(self, task_id: str) -> Optional[IngestionTask]:
        """
        Get a task by ID without removing it from the queue.

        Args:
            task_id: The task identifier.

        Returns:
            Optional[IngestionTask]: Task if found, None otherwise.
        """
        return self._tasks.get(task_id)

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending or queued task.

        Args:
            task_id: The task identifier.

        Returns:
            bool: True if task was cancelled, False otherwise.
        """
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False

            if task.status in [TaskStatus.PROCESSING, TaskStatus.COMPLETED]:
                logger.warning(
                    "cannot_cancel_task",
                    task_id=task_id,
                    status=task.status.value,
                )
                return False

            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.utcnow()

            # Remove from queue if present
            try:
                self._queue.remove(task)
            except ValueError:
                pass

            logger.info(
                "task_cancelled",
                task_id=task_id,
            )
            return True

    @property
    def size(self) -> int:
        """Get current queue size."""
        return len(self._queue)


class BackgroundProcessor:
    """
    Async background processor for document ingestion tasks.

    This class manages the worker loop that processes tasks from the queue,
    handling document parsing, chunking, embedding, and indexing.
    """

    def __init__(
        self,
        queue: Optional[TaskQueue] = None,
        max_concurrent_tasks: int = 5,
        polling_interval: float = 1.0,
    ) -> None:
        """
        Initialize the background processor.

        Args:
            queue: Task queue instance (creates new one if None).
            max_concurrent_tasks: Maximum number of concurrent task processors.
            polling_interval: Seconds to wait between queue polls.
        """
        self.queue = queue or TaskQueue()
        self.max_concurrent_tasks = max_concurrent_tasks
        self.polling_interval = polling_interval
        self._running = False
        self._workers: List[asyncio.Task] = []
        self._semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self._task_handlers: Dict[str, Callable] = {}

        logger.info(
            "background_processor_initialized",
            max_concurrent_tasks=max_concurrent_tasks,
            polling_interval=polling_interval,
        )

    def register_handler(
        self, task_type: str, handler: Callable[[IngestionTask], Any]
    ) -> None:
        """
        Register a handler function for a specific task type.

        Args:
            task_type: The type of task to handle.
            handler: Async function to process the task.
        """
        self._task_handlers[task_type] = handler
        logger.info(
            "handler_registered",
            task_type=task_type,
        )

    async def _process_task(self, task: IngestionTask) -> None:
        """
        Process a single ingestion task.

        Args:
            task: The ingestion task to process.
        """
        async with self._semaphore:
            task.started_at = datetime.utcnow()
            task.status = TaskStatus.PROCESSING

            logger.info(
                "task_processing_started",
                task_id=task.task_id,
                document_type=task.document_type,
            )

            try:
                # Mock processing - in production, this would:
                # 1. Download/fetch document
                # 2. Parse and extract text
                # 3. Chunk the text
                # 4. Generate embeddings
                # 5. Store in vector database

                # Simulate processing steps
                await self._simulate_step("Downloading document", 0.5)
                await self._simulate_step("Parsing content", 0.3)
                await self._simulate_step("Chunking text", 0.4)
                await self._simulate_step("Generating embeddings", 0.6)
                await self._simulate_step("Indexing vectors", 0.3)

                # Mock result
                task.result = {
                    "chunks_created": 10,
                    "embedding_dimension": 768,
                    "index_name": f"idx_{task.task_id}",
                    "processing_time_ms": int(
                        (datetime.utcnow() - task.started_at).total_seconds() * 1000
                    ),
                }

                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()

                logger.info(
                    "task_completed",
                    task_id=task.task_id,
                    chunks=task.result["chunks_created"],
                    processing_time_ms=task.result["processing_time_ms"],
                )

            except asyncio.CancelledError:
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.utcnow()
                logger.warning(
                    "task_cancelled",
                    task_id=task.task_id,
                )
                raise

            except Exception as e:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()
                task.error = str(e)

                logger.error(
                    "task_failed",
                    task_id=task.task_id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    exc_info=True,
                )

    async def _simulate_step(self, step_name: str, duration: float) -> None:
        """
        Simulate a processing step with logging.

        Args:
            step_name: Name of the processing step.
            duration: Duration to simulate in seconds.
        """
        logger.debug("processing_step", step=step_name)
        await asyncio.sleep(duration)

    async def _worker_loop(self, worker_id: int) -> None:
        """
        Main worker loop that continuously processes tasks.

        Args:
            worker_id: Unique identifier for this worker.
        """
        logger.info(
            "worker_started",
            worker_id=worker_id,
        )

        while self._running:
            try:
                task = await self.queue.dequeue()

                if task:
                    await self._process_task(task)
                else:
                    # No task available, wait before polling again
                    await asyncio.sleep(self.polling_interval)

            except asyncio.CancelledError:
                logger.info(
                    "worker_stopped",
                    worker_id=worker_id,
                )
                break

            except Exception as e:
                logger.error(
                    "worker_error",
                    worker_id=worker_id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    exc_info=True,
                )
                await asyncio.sleep(self.polling_interval)

    async def start(self, num_workers: int = 3) -> None:
        """
        Start the background processor with multiple workers.

        Args:
            num_workers: Number of worker coroutines to spawn.
        """
        if self._running:
            logger.warning("processor_already_running")
            return

        self._running = True
        logger.info(
            "processor_starting",
            num_workers=num_workers,
        )

        # Create worker tasks
        for i in range(num_workers):
            worker = asyncio.create_task(self._worker_loop(i))
            self._workers.append(worker)

        logger.info(
            "processor_started",
            active_workers=len(self._workers),
        )

    async def stop(self, timeout: float = 5.0) -> None:
        """
        Stop the background processor gracefully.

        Args:
            timeout: Maximum time to wait for workers to finish.
        """
        if not self._running:
            return

        logger.info("processor_stopping")
        self._running = False

        # Wait for workers to finish with timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*self._workers, return_exceptions=True),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.warning(
                "worker_shutdown_timeout",
                timeout=timeout,
            )
            # Cancel remaining workers
            for worker in self._workers:
                worker.cancel()

        self._workers.clear()
        logger.info("processor_stopped")

    async def submit_task(
        self,
        document_url: Optional[str] = None,
        document_content: Optional[str] = None,
        document_type: str = "txt",
        priority: str = "normal",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Submit a new ingestion task.

        Args:
            document_url: URL to the document.
            document_content: Raw document content.
            document_type: Type of document (pdf or txt).
            priority: Processing priority.
            metadata: Additional metadata.

        Returns:
            str: Task ID.

        Raises:
            ValueError: If neither URL nor content is provided.
        """
        if not document_url and not document_content:
            raise ValueError("Either document_url or document_content must be provided")

        task_id = f"task_{uuid.uuid4().hex[:12]}"
        task = IngestionTask(
            task_id=task_id,
            document_url=document_url,
            document_content=document_content,
            document_type=document_type,
            priority=priority,
            metadata=metadata or {},
        )

        success = await self.queue.enqueue(task)
        if not success:
            raise RuntimeError("Failed to enqueue task - queue is full")

        return task_id

    def get_stats(self) -> Dict[str, Any]:
        """
        Get processor statistics.

        Returns:
            dict: Processor stats including queue size and worker count.
        """
        return {
            "queue_size": self.queue.size,
            "active_workers": len([w for w in self._workers if not w.done()]),
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "is_running": self._running,
        }


# Global processor instance (for demonstration)
processor: Optional[BackgroundProcessor] = None


async def get_or_create_processor() -> BackgroundProcessor:
    """
    Get or create the global processor instance.

    Returns:
        BackgroundProcessor: The processor instance.
    """
    global processor
    if processor is None:
        processor = BackgroundProcessor()
    return processor


if __name__ == "__main__":
    # Example usage and testing
    async def main() -> None:
        """Run example worker processing."""
        proc = BackgroundProcessor(max_concurrent_tasks=3)

        # Start processor
        await proc.start(num_workers=2)

        # Submit some test tasks
        for i in range(5):
            task_id = await proc.submit_task(
                document_content=f"Test document {i}",
                document_type="txt",
                priority="high" if i % 2 == 0 else "normal",
            )
            logger.info("submitted_task", task_id=task_id)

        # Let processing run for a bit
        await asyncio.sleep(10)

        # Get stats
        stats = proc.get_stats()
        logger.info("processor_stats", **stats)

        # Stop processor
        await proc.stop()

    asyncio.run(main())
