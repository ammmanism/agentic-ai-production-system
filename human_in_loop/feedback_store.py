"""Feedback store — collect and persist user thumbs-up / thumbs-down ratings."""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_DEFAULT_STORE = Path("feedback_data.jsonl")


class FeedbackStore:
    """
    Append-only JSONL store for user feedback signals.

    Each line is a JSON record with session_id, rating (1-5), message,
    and ISO timestamp.  In production: write to PostgreSQL / BigQuery.
    """

    def __init__(self, store_path: Optional[Path] = None):
        self._path = store_path or _DEFAULT_STORE
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        session_id: str,
        message_id: str,
        rating: int,
        comment: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append a feedback entry to the JSONL file."""
        entry = {
            "timestamp": time.time(),
            "session_id": session_id,
            "message_id": message_id,
            "rating": rating,
            "comment": comment,
            "metadata": metadata or {},
        }
        with open(self._path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
        logger.info("Feedback recorded: session=%s rating=%d", session_id, rating)

    def load_all(self) -> List[Dict[str, Any]]:
        """Load all feedback records from the JSONL file."""
        if not self._path.exists():
            return []
        records = []
        with open(self._path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records
