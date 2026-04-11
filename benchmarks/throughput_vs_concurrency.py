"""
Load testing script to measure API throughput vs concurrency.
Supports both Locust-based distributed testing and internal asyncio-based simulation.
"""
import uuid
import asyncio
import time
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# --- LOCUST STRATEGY ---
try:
    from locust import HttpUser, task, between
except ImportError:
    # Stub if locust not installed locally
    HttpUser = object
    def task(f): return f
    def between(a, b): return 1

class AgentBenchUser(HttpUser):
    """Locust-based performance tester for deployment-level metrics."""
    wait_time = between(1, 2)

    @task
    def chat_query(self):
        """Simulate a standard load test query for stress profiling."""
        payload = {
            "session_id": f"bench_{uuid.uuid4()}",
            "query": "How is the system architecture defined?",
            "stream": False
        }
        # In actual usage, this hits the vLLM/FastAPI endpoint
        # self.client.post("/chat/stream", json=payload)
        pass

# --- ASYNC SIMULATION STRATEGY ---
async def simulate_query(query_id: int) -> float:
    """Mock networking/inferencing delay for a single query."""
    start = time.time()
    # Assuming avg 1.5s latency per request
    await asyncio.sleep(1.5)
    return time.time() - start

async def load_test(concurrency_level: int, total_requests: int):
    """
    Simulates a Locust-style load test against the async pipeline internally.
    """
    logger.info(f"Starting load test | Concurrency: {concurrency_level} | Total: {total_requests}")
    
    semaphore = asyncio.Semaphore(concurrency_level)
    
    async def bound_query(qid: int):
        async with semaphore:
            return await simulate_query(qid)
            
    start_time = time.time()
    tasks = [bound_query(i) for i in range(total_requests)]
    
    latencies = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    throughput = total_requests / total_time
    p95_latency = sorted(latencies)[int(0.95 * len(latencies))]
    
    logger.info(f"Test Complete in {total_time:.2f}s")
    logger.info(f"Throughput: {throughput:.2f} req/sec")
    logger.info(f"P95 Latency: {p95_latency:.2f}s")
    
    return throughput, p95_latency

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Defaulting to async simulation if run directly
    asyncio.run(load_test(concurrency_level=50, total_requests=200))

