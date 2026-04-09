import time
import functools
import logging

logger = logging.getLogger(__name__)

def count_flops(func):
    """
    Decorator to estimate floating point operations for LLM/Agent steps.
    Note: For API-based models this is an estimation based on token count.
    For local vLLM, you would plug into the CUDA profiler.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        
        # Extremely rough heuristic: 2 * Parameters * Tokens
        # Assuming 8B param model, 16 billion flops per token roughly
        est_tokens = len(str(result).split()) * 1.3
        est_flops = 2 * 8_000_000_000 * est_tokens
        
        logger.debug(f"[FLOPs] {func.__name__} took {duration:.2f}s | Est. FLOPS: {est_flops:.2e}")
        return result
    return wrapper
