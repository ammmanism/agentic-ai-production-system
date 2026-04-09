# ⚖️ Architecture Tradeoffs

This document maintains a living record of critical design decisions. Any major refactor or integration constraint MUST be justified here to avoid revisiting debated topics without new evidence.

| Decision | Alternatives Considered | Why Chosen | Tradeoff |
|----------|-------------------------|------------|----------|
| **Orchestration**: LangGraph | AutoGen, CrewAI, Custom Loop | LangGraph provides explicit, typed state machines. This prevents models from going into endless loops and makes conditional routing extremely deterministic. | We sacrifice the "free-form" multi-agent chat vibe for strict graph-level verbosity and state boilerplate. |
| **Vector Store**: Qdrant | Pinecone, Milvus, Chroma | Rust-based, highly efficient, supports both dense + sparse (BM25) out of the box natively with zero-dependency binaries. | Self-hosting Qdrant on K8s shifts operational burden vs a managed service like Pinecone, but saves $10k+ at scale. |
| **Caching Layer**: Redis Exact + Semantic | Only Redis, or LLMLingua | High query volume often hits exact matches. Semantic caching intercepts paraphrased queries. | Semantic cache requires a lightweight embedding call upfront, adding a minimal ~50ms latency penalty but saving ~10% compute cost overall. |
| **Tool Execution**: Sandboxed Python via Docker | Native `exec()`, E2B hosted | Local Docker provides complete isolation from the host filesystem without incurring a 3rd party API network latency for code execution. | Maintaining and building isolated execution containers adds friction to the CI/CD pipeline and local developer setup. |
