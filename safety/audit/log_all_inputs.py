"""Audit logger — writes all LLM inputs/outputs to structured JSON logs."""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, Optional

logger = logging.getLogger("audit")


def log_request(
    session_id: str,
    user_input: str,
    model_output: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Emit a structured audit record for every LLM interaction.

    In production: ship to S3 / BigQuery via a log aggregator (Fluentd, Logstash).
    Locally: writes JSON to stdout so Docker log drivers pick it up.
    """
    record = {
        "event": "llm_interaction",
        "timestamp": time.time(),
        "session_id": session_id,
        "input_length": len(user_input),
        "output_length": len(model_output),
        "input_snippet": user_input[:200],
        "output_snippet": model_output[:200],
        "metadata": metadata or {},
    }
    logger.info(json.dumps(record))
