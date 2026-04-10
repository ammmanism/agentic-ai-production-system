"""
FLOPs counting utility for agent reasoning steps (Stub).
"""

def estimate_inference_flops(tokens_in: int, tokens_out: int, model_params: int = 7_000_000_000) -> int:
    """
    Theoretical FLOPs per inference step based on standard transformer sizing.
    # TODO: Implement accurate deepspeed flops profiler hook mapped to specific agent nodes.
    """
    # Rough approximation: 2 FLOPs per parameter per token
    return model_params * (tokens_in + tokens_out) * 2
