# Architecture Tradeoffs

This document outlines the core architectural and library decisions made for this agentic AI system.

| Decision | Alternative | Why We Chose This | Downside |
|----------|-------------|-------------------|-----------|
| **LangGraph vs CrewAI** | CrewAI is simpler | Need explicit cyclic flows, state management & human-in-loop approval | Steeper learning curve, more boilerplate |
| **Qdrant vs Pinecone** | Pinecone is fully managed | Better cost control, open-source with self-host option | More operational overhead to maintain locally |
| **Pydantic vs TypedDict** | TypedDict native to langgraph | Strict validation and schema enforcement at boundaries | Slight performance overhead for complex models |
| **Prometheus vs Datadog** | Datadog has deeper APM out of box | Vendor agnosticism, cheaper for high cardinality metrics | Requires manual grafana dashboards |
| **Sync API vs Async** | Async everywhere for max throughput | Simplified implementation, predictable worker management | Slightly higher latency p99 under burst load |
