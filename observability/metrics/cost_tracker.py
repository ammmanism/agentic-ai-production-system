from prometheus_client import Counter

cost_counter = Counter("llm_cost_cents", "Cost in USD cents", ["model", "provider"])

def track_cost(model: str, provider: str, input_tokens: int, output_tokens: int):
    # Pricing per 1M tokens (example)
    rates = {"gpt-3.5-turbo": (0.5, 1.5), "gpt-4": (10, 30)}
    input_cost = input_tokens / 1_000_000 * rates[model][0]
    output_cost = output_tokens / 1_000_000 * rates[model][1]
    total_cents = (input_cost + output_cost) * 100
    cost_counter.labels(model=model, provider=provider).inc(total_cents)
