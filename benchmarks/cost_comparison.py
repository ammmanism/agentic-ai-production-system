class CostCalculator:
    """
    Calculates cost differentials between our self-hosted LangGraph agent 
    vs OpenAI generic assistants.
    """
    
    # Prices per 1M tokens ($)
    RATES = {
        "gpt-4o": {"in": 5.00, "out": 15.00},
        "claude-3.5-sonnet": {"in": 3.00, "out": 15.00},
        "local_llama3_8b_vllm": {"in": 0.10, "out": 0.10} # Hardware amortization est
    }
    
    @classmethod
    def compare(cls, avg_in_tokens: int, avg_out_tokens: int, query_volume: int):
        results = {}
        for model, rates in cls.RATES.items():
            cost_in = (avg_in_tokens / 1_000_000) * rates["in"] * query_volume
            cost_out = (avg_out_tokens / 1_000_000) * rates["out"] * query_volume
            results[model] = cost_in + cost_out
            
        print(f"Cost basis for {query_volume} queries ({avg_in_tokens}in / {avg_out_tokens}out per query):")
        for m, cost in results.items():
            print(f"- {m}: ${cost:.2f}")
        return results

if __name__ == "__main__":
    # Estimate standard multi-tool agent run (Context heavy in, standard out)
    CostCalculator.compare(avg_in_tokens=4500, avg_out_tokens=800, query_volume=10_000)
