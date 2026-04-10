"""
Peak memory footprint tracer for execution graph boundaries.
"""
import tracemalloc
import logging

logger = logging.getLogger(__name__)

class PeakMemoryTracer:
    """
    Context manager to trace CPU memory allocation during agent execution steps.
    """
    def __enter__(self):
        tracemalloc.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        current, peak = tracemalloc.get_traced_memory()
        logger.info(f"Peak RAM dynamically tracked: {peak / 10**6:.2f} MB")
        tracemalloc.stop()
        # TODO: Add torch.cuda.max_memory_allocated() for vLLM local profiling
