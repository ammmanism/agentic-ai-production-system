"""Generate a test set of question-answer pairs for RAGAS evaluation."""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent / "evaluation" / "datasets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEST_QUERIES = [
    {"id": "q1", "question": "What is LangGraph used for?"},
    {"id": "q2", "question": "How does RAG reduce hallucinations?"},
    {"id": "q3", "question": "What is Qdrant and what language is it written in?"},
    {"id": "q4", "question": "How does Prometheus collect metrics?"},
    {"id": "q5", "question": "Explain the token bucket rate limiting algorithm."},
]

GOLDEN_RESPONSES = [
    {"id": "q1", "answer": "LangGraph is used for building stateful, multi-actor agent workflows with LLMs, extending LangChain with cyclic graph support."},
    {"id": "q2", "answer": "RAG reduces hallucinations by grounding responses in retrieved context from a knowledge base before generating the final answer."},
    {"id": "q3", "answer": "Qdrant is a vector similarity search engine and database written in Rust."},
    {"id": "q4", "answer": "Prometheus collects metrics by scraping configured targets at specified intervals through an HTTP pull model."},
    {"id": "q5", "answer": "Token bucket allows requests at a steady rate; each request consumes a token, and tokens refill at a fixed rate. When empty, requests are rejected."},
]


def main():
    queries_path = OUTPUT_DIR / "test_queries.json"
    golden_path = OUTPUT_DIR / "golden_responses.json"

    with open(queries_path, "w") as f:
        json.dump(TEST_QUERIES, f, indent=2)

    with open(golden_path, "w") as f:
        json.dump(GOLDEN_RESPONSES, f, indent=2)

    logger.info("Generated %d test queries → %s", len(TEST_QUERIES), queries_path)
    logger.info("Generated %d golden responses → %s", len(GOLDEN_RESPONSES), golden_path)


if __name__ == "__main__":
    main()
