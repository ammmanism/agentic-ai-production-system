# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-10

### Added
- Production-ready agent graph with planner/executor/reflector mapping.
- RAGAS evaluation capability in CI environments.
- High-throughput asynchronous RAG ingestion pipeline.
- End-to-end tooling registry and executor architecture resolving stubs.
- Formal human-in-the-loop approval gate store validation.
- Profiling setup for inference compute tracking (`flops_counter.py`, `memory_tracer.py`).
- Precision mapping scaffolds for `fp8_quant` and caching parameters.
- Benchmark automation via locust and basic cost profiling charts.

### Fixed
- Prompt injection guard false positives across standard payloads.
- Resolution of testing placeholder API components to actively mapped models.

## [0.1.0] - 2026-04-06

### Added
- Initial codebase scaffolding matching architectural specs.
- Basic API entrypoints and folder conventions.
