"""Langfuse integration for LLM observability and tracing."""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class LangfuseTracer:
    """
    Thin wrapper around the Langfuse Python SDK for tracing LLM calls.

    Requires:
        LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST env vars.
    Falls back gracefully when the package or credentials are absent.
    """

    def __init__(self):
        self._client = None
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

        if not public_key or not secret_key:
            logger.warning("Langfuse credentials not set — tracing disabled")
            return

        try:
            from langfuse import Langfuse  # type: ignore

            self._client = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=host,
            )
            logger.info("Langfuse tracer initialised (host=%s)", host)
        except ImportError:
            logger.warning("langfuse package not installed — tracing disabled")

    def trace(
        self,
        name: str,
        input_data: Any,
        output_data: Any,
        metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """Record a single LLM interaction trace."""
        if self._client is None:
            return
        try:
            self._client.trace(
                name=name,
                input=input_data,
                output=output_data,
                metadata=metadata or {},
                session_id=session_id,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Langfuse trace failed: %s", exc)

    def flush(self) -> None:
        """Flush pending traces before shutdown."""
        if self._client:
            self._client.flush()
