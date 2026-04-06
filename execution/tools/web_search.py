"""Web search tool — wraps Tavily / Serper API."""
from __future__ import annotations

import os
from typing import Any, Dict, List

from .registry import register


@register("web_search")
def web_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web and return a list of result dicts with keys:
    title, url, snippet.

    Requires TAVILY_API_KEY env var in production.
    Falls back to a stub when the key is absent (e.g., CI).
    """
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        # Stub response for local dev / CI without API key
        return [
            {
                "title": f"[Stub] Result for: {query}",
                "url": "https://example.com",
                "snippet": f"Simulated web search result for query: {query}",
            }
        ]

    try:
        from tavily import TavilyClient  # type: ignore

        client = TavilyClient(api_key=api_key)
        response = client.search(query, max_results=max_results)
        return response.get("results", [])
    except Exception as exc:  # noqa: BLE001
        return [{"title": "Error", "url": "", "snippet": str(exc)}]
