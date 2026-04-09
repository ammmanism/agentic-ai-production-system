import asyncio
import time
import logging

logger = logging.getLogger(__name__)

async def simulate_query(query_id: int) -> float:
    """Mock networking/inferencing delay for a single query."""
    # Assuming avg 1.5s latency per request
    start = time.time()
    await asyncio.sleep(1.5)
    return time.time() - start

async def load_test(concurrency_level: int, total_requests: int):
    """
    Simulates a Locust-style load test against the async pipeline.
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
    asyncio.run(load_test(concurrency_level=50, total_requests=200))
