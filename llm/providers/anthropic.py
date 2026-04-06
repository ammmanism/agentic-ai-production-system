"""Anthropic Claude LLM provider implementation."""
from __future__ import annotations

import os
from typing import Any, Dict, Iterator, List

from .base import BaseLLM


class AnthropicLLM(BaseLLM):
    """Wrapper around the Anthropic Messages API."""

    def __init__(self, model: str = "claude-3-5-haiku-latest", api_key: str | None = None):
        self._model = model
        self._api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")

    @property
    def model_name(self) -> str:
        return self._model

    def _client(self):
        import anthropic  # type: ignore
        return anthropic.Anthropic(api_key=self._api_key)

    def complete(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        # Anthropic separates system messages
        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_messages = [m for m in messages if m["role"] != "system"]

        response = self._client().messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system,
            messages=user_messages,
            **kwargs,
        )
        return response.content[0].text

    def stream(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Iterator[str]:
        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_messages = [m for m in messages if m["role"] != "system"]

        with self._client().messages.stream(
            model=self._model,
            max_tokens=max_tokens,
            system=system,
            messages=user_messages,
        ) as stream_ctx:
            for text in stream_ctx.text_stream:
                yield text
