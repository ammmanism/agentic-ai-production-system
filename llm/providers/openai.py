"""OpenAI LLM provider implementation."""
from __future__ import annotations

import os
from typing import Any, Dict, Iterator, List

from .base import BaseLLM


class OpenAILLM(BaseLLM):
    """Wrapper around the OpenAI Chat Completions API."""

    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None):
        self._model = model
        self._api_key = api_key or os.getenv("OPENAI_API_KEY", "")

    @property
    def model_name(self) -> str:
        return self._model

    def _client(self):
        import openai  # type: ignore
        return openai.OpenAI(api_key=self._api_key)

    def complete(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        response = self._client().chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )
        return response.choices[0].message.content or ""

    def stream(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Iterator[str]:
        stream = self._client().chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
            **kwargs,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
