"""CI/CD evaluation gate — fail the build if p99 latency exceeds threshold."""
from __future__ import annotations

import sys
import time
import logging
from typing import List

logger = logging.getLogger(__name__)

P99_THRESHOLD_MS = 3000.0   # 3 seconds — adjust per SLO
SAMPLE_SIZE = 20


def measure_latencies(n: int = SAMPLE_SIZE) -> List[float]:
    """
    Run a series of dummy queries and record latencies.
    Replace the inner logic with real API calls in CI.
    """
    latencies = []
    for i in range(n):
        start = time.monotonic()
        # Stub query — replace with: requests.post("/chat/stream", ...)
        time.sleep(0.05)  # simulate 50 ms response
        elapsed_ms = (time.monotonic() - start) * 1000
        latencies.append(elapsed_ms)
    return latencies


def p99(latencies: List[float]) -> float:
    if not latencies:
        return 0.0
    sorted_lat = sorted(latencies)
    idx = int(0.99 * len(sorted_lat))
    return sorted_lat[min(idx, len(sorted_lat) - 1)]


def assert_latency(threshold_ms: float = P99_THRESHOLD_MS) -> None:
    """Measure latencies and assert that p99 is below the SLO threshold."""
    latencies = measure_latencies()
    p99_val = p99(latencies)

    print(f"p99 latency: {p99_val:.1f} ms  (threshold: {threshold_ms:.0f} ms)")
    if p99_val > threshold_ms:
        print(f"FAIL: p99 latency {p99_val:.1f} ms exceeds {threshold_ms:.0f} ms SLO!")
        sys.exit(1)
    else:
        print("PASS: latency within SLO.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    assert_latency()
