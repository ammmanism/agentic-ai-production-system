"""Prometheus metrics — latency, token usage, cost per request."""
from __future__ import annotations

from prometheus_client import Counter, Histogram, Gauge

# Request latency histogram (seconds)
request_latency = Histogram(
    "llm_request_latency_seconds",
    "End-to-end request latency in seconds",
    ["model", "endpoint"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0],
)

# Token counters
input_tokens_total = Counter(
    "llm_input_tokens_total",
    "Total input tokens consumed",
    ["model", "provider"],
)

output_tokens_total = Counter(
    "llm_output_tokens_total",
    "Total output tokens generated",
    ["model", "provider"],
)

# Request counters
requests_total = Counter(
    "api_requests_total",
    "Total API requests received",
    ["endpoint", "status"],
)

# Active connections
active_requests = Gauge(
    "api_active_requests",
    "Number of requests currently being processed",
)
