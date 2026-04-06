"""E2E API smoke test — hits the live FastAPI server."""
from __future__ import annotations

import os
import pytest

# Requires `requests` and a running server at BASE_URL
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def _get(path: str):
    import requests
    return requests.get(f"{BASE_URL}{path}", timeout=10)


def _post(path: str, json: dict):
    import requests
    return requests.post(f"{BASE_URL}{path}", json=json, timeout=10)


@pytest.mark.e2e
def test_health_check():
    resp = _get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.e2e
def test_chat_endpoint():
    resp = _post(
        "/chat/stream",
        {
            "session_id": "e2e-test-session",
            "query": "What is 2 + 2?",
            "stream": False,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert data["session_id"] == "e2e-test-session"


@pytest.mark.e2e
def test_ingest_endpoint():
    resp = _post(
        "/ingest",
        {
            "documents": [{"id": "1", "text": "Test document", "metadata": {}}],
            "collection": "e2e-test",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["ingested"] == 1
