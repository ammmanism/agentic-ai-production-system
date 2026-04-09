# Contributing to Agentic AI Production System

We welcome contributions! To maintain our "goat-level" engineering standards, we enforce strict processes.

## Pull Request Process

1. **Branch Naming**: Ensure your branch follows our naming convention (see below).
2. **Tradeoff Documentation**: You MUST fill out the Pull Request template and document any architectural or library decisions in `docs/tradeoffs.md`. Every architectural PR must answer: "What are the alternatives, and why did we choose this?"
3. **Pass Quality Gates**: Your PR must pass `make lint`, `make test`, and our offline RAGAS evaluation limits (`make eval`).
4. **Codeowners**: All PRs require review from the team (`@yourname`), enforced by `.github/CODEOWNERS`.

## Branch Strategy

Adopt a Git Flow-inspired naming convention with descriptive prefixes.

| Prefix | Purpose | Example |
|---|---|---|
| `feat/` | New feature | `feat/add-semantic-cache` |
| `fix/` | Bug fix | `fix/prompt-injection-bypass` |
| `exp/` | Experimental (not for merge yet) | `exp/dspy-optimizer-v2` |
| `docs/` | Documentation only | `docs/update-architecture-diagram` |
| `perf/` | Performance improvement | `perf/reduce-kv-cache-memory` |
| `refactor/` | Code refactor (no behavior change) | `refactor/abstract-llm-provider` |
| `eval/` | Evaluation or benchmark changes | `eval/add-new-ragas-metrics` |

`main` is production-ready. Never commit directly.
