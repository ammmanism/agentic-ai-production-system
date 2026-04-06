"""Online evaluation — log real-world agent failures for analysis."""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_DEFAULT_LOG = Path("confusion_log.jsonl")


class ConfusionLogger:
    """
    Log cases where the agent failed, hallucinated, or gave a low-rated answer.

    Entries are written as JSONL for easy downstream analysis
    (spark, pandas, BigQuery external tables, etc.).
    """

    def __init__(self, log_path: Optional[Path] = None):
        self._path = log_path or _DEFAULT_LOG

    def log_failure(
        self,
        session_id: str,
        query: str,
        predicted_answer: str,
        expected_answer: Optional[str] = None,
        failure_type: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append a failure record to the JSONL log."""
        record = {
            "event": "agent_failure",
            "timestamp": time.time(),
            "session_id": session_id,
            "query": query,
            "predicted_answer": predicted_answer,
            "expected_answer": expected_answer,
            "failure_type": failure_type,
            "metadata": metadata or {},
        }
        with open(self._path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
        logger.warning("Failure logged: session=%s type=%s", session_id, failure_type)

    def load_failures(self) -> List[Dict[str, Any]]:
        if not self._path.exists():
            return []
        with open(self._path, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]
