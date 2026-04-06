"""Seed the vector store with initial documents for demo / testing."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

# Make sure project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.pipelines.full_rag import FullRAGPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEED_DOCUMENTS = [
    """LangGraph is a library for building stateful, multi-actor applications with LLMs,
    used to create agent and multi-agent workflows. It extends LangChain with the ability
    to define graph-based workflows with cycles, state, and human-in-the-loop control.""",

    """RAG (Retrieval-Augmented Generation) is an AI framework that combines information
    retrieval with text generation. It retrieves relevant context from a knowledge base
    before generating an answer, reducing hallucinations significantly.""",

    """Qdrant is a vector similarity search engine and vector database written in Rust.
    It provides a production-ready service with a convenient API to store, search, and
    manage points (vectors) with an additional payload.""",

    """Prometheus is an open-source systems monitoring and alerting toolkit. It collects
    metrics from configured targets at specified intervals, evaluates rule expressions,
    and displays the results. It supports a multi-dimensional data model with time-series.""",

    """Token bucket is a rate limiting algorithm where each user has a bucket filled with
    tokens at a fixed rate. Each request consumes one token. When the bucket is empty,
    additional requests are rejected until tokens are refilled.""",
]


def main():
    logger.info("Seeding vector store with %d documents …", len(SEED_DOCUMENTS))
    pipeline = FullRAGPipeline(collection="seed")
    n = pipeline.ingest(SEED_DOCUMENTS)
    logger.info("Seeded %d chunks successfully.", n)


if __name__ == "__main__":
    main()
