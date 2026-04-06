"""Short-term in-context memory — stores the current conversation turn."""
from __future__ import annotations

from typing import Dict, List


class ShortTermMemory:
    """Maintains the rolling chat history for a single session."""

    def __init__(self, max_turns: int = 20):
        self._history: List[Dict[str, str]] = []
        self._max_turns = max_turns

    def add(self, role: str, content: str) -> None:
        self._history.append({"role": role, "content": content})
        # Keep only the last N turns to stay within context window
        if len(self._history) > self._max_turns * 2:
            self._history = self._history[-(self._max_turns * 2):]

    def get_history(self) -> List[Dict[str, str]]:
        return list(self._history)

    def clear(self) -> None:
        self._history = []
