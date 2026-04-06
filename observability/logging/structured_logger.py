"""Structured JSON logger — emit consistent, machine-parseable log records."""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, Optional


class StructuredFormatter(logging.Formatter):
    """Format log records as single-line JSON for log aggregators."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        payload: Dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        # Merge any extra fields passed via `extra=`
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord.__dict__ and not key.startswith("_"):
                payload[key] = value
        return json.dumps(payload, default=str)


def get_logger(name: str, level: str | None = None) -> logging.Logger:
    """
    Return a logger configured with the structured JSON formatter.

    Pass ``level="DEBUG"`` or set the LOG_LEVEL env var (default: INFO).
    """
    log_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)
    logger.setLevel(log_level)
    logger.propagate = False
    return logger
