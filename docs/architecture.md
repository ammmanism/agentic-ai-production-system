# Architecture

## System Overview

The Agentic AI Production System uses a **LangGraph-based orchestration loop** that implements Plan → Execute → Reflect cycles with human-in-the-loop gates.

```
User Query
    │
    ▼
┌─────────────┐       ┌──────────────┐       ┌──────────────┐
│   Planner   │──────▶│   Executor   │──────▶│  Reflector   │
│ (LLM + RAG) │       │ (Tool calls) │       │(Self-critique)│
└─────────────┘       └──────────────┘       └──────┬───────┘
        ▲                     │                      │
        │              Final Answer            Needs replan?
        └──────────────────────────────────────────┘
```

## Key Components

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Orchestration | LangGraph | Stateful cyclic agent graph |
| Retrieval | Qdrant + BM25 | Hybrid dense + sparse search |
| LLM Gateway | OpenAI/Anthropic/vLLM | Swappable provider interface |
| Safety | Regex + Detoxify | Injection, PII, toxicity |
| Observability | Prometheus + Langfuse | Metrics, cost, tracing |
| Deployment | Docker + K8s + Terraform | Container-first delivery |

## Data Flow

1. **Ingest**: Documents → Chunker → Embedder → Qdrant
2. **Query**: User → Safety guards → Planner → RAG → Executor → Reflector → Answer
3. **Feedback**: Answer → Human rating → FeedbackStore → ActiveLearner → Fine-tune

## Design Decisions

See [tradeoffs.md](tradeoffs.md) for a detailed table of every key decision.
