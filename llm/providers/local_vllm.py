"""Local vLLM provider — self-hosted model via OpenAI-compatible API."""
from __future__ import annotations

import os
from typing import Any, Dict, Iterator, List

from .base import BaseLLM


class LocalVLLM(BaseLLM):
    """
    Connector for a locally running vLLM server.

    vLLM exposes an OpenAI-compatible API endpoint, so we reuse the
    openai client library pointed at localhost.
    """

    def __init__(
        self,
        model: str = "mistralai/Mistral-7B-Instruct-v0.3",
        base_url: str | None = None,
    ):
        self._model = model
        self._base_url = base_url or os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")

    @property
    def model_name(self) -> str:
        return self._model

    def _client(self):
        import openai  # type: ignore
        return openai.OpenAI(api_key="EMPTY", base_url=self._base_url)

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
