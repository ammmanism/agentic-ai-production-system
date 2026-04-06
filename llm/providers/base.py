"""LLM provider abstract base class."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional


class BaseLLM(ABC):
    """Abstract interface that every LLM provider must implement."""

    @abstractmethod
    def complete(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Return a completion string."""

    @abstractmethod
    def stream(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Iterator[str]:
        """Yield completion tokens one at a time."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Identifier string for the model (used in metrics)."""
