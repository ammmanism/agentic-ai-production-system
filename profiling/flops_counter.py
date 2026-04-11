"""
FLOPs counting utility for agent reasoning steps and model inference.
Provides theoretical estimations based on parameter count and token density.
"""
import time
import functools
import logging

logger = logging.getLogger(__name__)

def estimate_inference_flops(tokens_in: int, tokens_out: int, model_params: int = 8_000_000_000) -> int:
    """
    Theoretical FLOPs per inference step based on standard transformer sizing.
    Rough approximation: 2 FLOPs per parameter per token.
    """
    return int(model_params * (tokens_in + tokens_out) * 2)

def count_flops(model_params: int = 8_000_000_000):
    """
    Decorator to estimate floating point operations for LLM/Agent steps.
    Note: For API-based models this is an estimation based on token count.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            result = await func(*args, **kwargs)
            duration = time.time() - start
            
            # Rough heuristic: Estimate tokens based on response length if not provided
            est_tokens = len(str(result).split()) * 1.3
            est_flops = estimate_inference_flops(0, est_tokens, model_params)
            
            logger.debug(f"[FLOPs] {func.__name__} took {duration:.2f}s | Est. FLOPS: {est_flops:.2e}")
            return result
        return wrapper
    return decorator

