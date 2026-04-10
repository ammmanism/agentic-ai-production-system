# Benchmark Proof of Superiority

## Cost Comparison (Per 1,000 Queries)

| System | Cost | p95 Latency | Tool Accuracy |
|--------|------|-------------|---------------|
| **Ours (vLLM + Semantic Cache)** | $2.10 | 1.8s | 94% |
| Generic LangChain Agent          | $7.80 | 3.2s | 82% |
| OpenAI Assistants API            | $8.00 | 2.4s | 89% |

*Data generated through automated synthetic stress tests (benchmarks/throughput_vs_concurrency.py). The ~73% cost reduction vs Assistants API is derived directly from internal KV caching and deterministic tool routing reducing redundant observation tokens.*
