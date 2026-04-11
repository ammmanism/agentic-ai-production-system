"""
Peak memory footprint tracer for execution graph boundaries and function isolation.
"""
import tracemalloc
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class PeakMemoryTracer:
    """
    Context manager to trace CPU memory allocation during agent execution steps.
    Useful for block-level profiling.
    """
    def __enter__(self):
        tracemalloc.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        current, peak = tracemalloc.get_traced_memory()
        logger.info(f"[Context Memory Trace] Peak RAM: {peak / 10**6:.2f} MB")
        tracemalloc.stop()

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
            logger.info(f"[Memory Trace - {func.__name__}] Peak usage: {peak / 10**6:.2f} MB")
        return result
    return wrapper

