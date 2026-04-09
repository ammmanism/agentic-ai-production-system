import tracemalloc
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def trace_memory(func):
    """
    Decorator to track peak Python memory usage during execution of a specific function.
    Highly useful for isolating memory bloat in RAG chunking pipelines.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        
        try:
            result = func(*args, **kwargs)
        finally:
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            logger.info(f"[Memory Trace - {func.__name__}] Current: {current / 10**6:.2f}MB, Peak: {peak / 10**6:.2f}MB")
            
        return result
    return wrapper
