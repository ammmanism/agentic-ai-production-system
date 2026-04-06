# Contributing to Agentic AI Production System

We welcome contributions! Please follow these guidelines:

## Pull Requests
1. **Tradeoffs Document Required:** For any architectural or library change, you MUST update `docs/tradeoffs.md` explaining why the change was made, the alternatives considered, and any downsides. PRs without a tradeoffs update will be rejected.
2. **Evaluation:** If you touch the prompt manager or retrieval pipeline, you must run the offline RAGAS evaluation suite and paste the before/after scores in the PR description.
3. **Tests:** All new tools or nodes must have unit tests.

## Development Setup
Use the provided DevContainer for a one-click environment, or manually install `pip install -e .`.
Run `make test` before submitting.
