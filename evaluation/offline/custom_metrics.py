"""Custom evaluation metrics beyond RAGAS (tool call accuracy, format adherence)."""
from __future__ import annotations

from typing import Any, Dict, List


def tool_call_accuracy(
    predictions: List[Dict[str, Any]],
    ground_truths: List[Dict[str, Any]],
) -> float:
    """
    Measure the fraction of responses where the agent used the correct tool(s).

    Each element should have a "tools_used" list.
    """
    if not predictions:
        return 0.0
    correct = 0
    for pred, truth in zip(predictions, ground_truths):
        pred_tools = set(pred.get("tools_used") or [])
        truth_tools = set(truth.get("tools_used") or [])
        if pred_tools == truth_tools:
            correct += 1
    return correct / len(predictions)


def format_adherence(responses: List[str], required_keys: List[str]) -> float:
    """
    Check that responses contain all required keys/sections.

    Useful for structured outputs (JSON, YAML, markdown with headers).
    """
    if not responses:
        return 0.0
    passes = 0
    for resp in responses:
        if all(key.lower() in resp.lower() for key in required_keys):
            passes += 1
    return passes / len(responses)


def latency_p99(latencies_ms: List[float]) -> float:
    """Return the 99th-percentile latency from a list of measurements."""
    if not latencies_ms:
        return 0.0
    sorted_lat = sorted(latencies_ms)
    idx = int(0.99 * len(sorted_lat))
    return sorted_lat[min(idx, len(sorted_lat) - 1)]
