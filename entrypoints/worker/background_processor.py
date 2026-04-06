"""Background worker — processes ingestion and async tasks via a job queue."""
from __future__ import annotations

import logging
import time
from typing import Any, Dict

logger = logging.getLogger(__name__)


def process_ingest_job(job: Dict[str, Any]) -> None:
    """
    Process a document ingestion job from the queue.

    Expected job schema:
        {
            "collection": str,
            "documents": list[str],
            "job_id": str
        }

    Production: wire this up as a Celery task or RQ job:
        @celery_app.task
        def process_ingest_job(job): ...
    """
    job_id = job.get("job_id", "unknown")
    logger.info("Worker: starting ingest job_id=%s", job_id)

    try:
        from rag.pipelines.full_rag import FullRAGPipeline

        pipeline = FullRAGPipeline(collection=job.get("collection", "default"))
        n = pipeline.ingest(job.get("documents", []))
        logger.info("Worker: ingested %d chunks for job_id=%s", n, job_id)
    except Exception as exc:  # noqa: BLE001
        logger.error("Worker: ingest job_id=%s failed: %s", job_id, exc)
        raise


if __name__ == "__main__":
    # Simple polling loop for demonstration (use Celery/RQ in production)
    logging.basicConfig(level=logging.INFO)
    logger.info("Worker started — polling for jobs every 5 seconds …")
    while True:
        time.sleep(5)
