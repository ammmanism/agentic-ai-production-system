"""Long-term memory — stores session summaries in a vector DB."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class LongTermMemory:
    """
    Stores and retrieves past session summaries via vector search.

    In production: connect to Qdrant / LanceDB with a real embedding model.
    This stub keeps data in memory for testing without external deps.
    """

    def __init__(self):
        self._store: List[Dict[str, Any]] = []

    def upsert(self, session_id: str, summary: str, metadata: Optional[Dict] = None) -> None:
        """Store a session summary (overwrites if session_id already exists)."""
        logger.info("LongTermMemory.upsert: session_id=%s", session_id)
        self._store = [e for e in self._store if e["session_id"] != session_id]
        self._store.append(
            {"session_id": session_id, "summary": summary, "metadata": metadata or {}}
        )

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Return the top-k most relevant past sessions (keyword match stub)."""
        results = [e for e in self._store if query.lower() in e["summary"].lower()]
        return results[:top_k]

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        for entry in self._store:
            if entry["session_id"] == session_id:
                return entry
        return None
