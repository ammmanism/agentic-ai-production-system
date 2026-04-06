"""Run RAGAS evaluation on the golden test set."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from evaluation.offline.ragas_evaluator import run_ragas_eval

logger = logging.getLogger(__name__)

DATASETS_DIR = Path(__file__).parent.parent / "datasets"


def main():
    test_queries_path = DATASETS_DIR / "test_queries.json"
    golden_path = DATASETS_DIR / "golden_responses.json"

    if not test_queries_path.exists() or not golden_path.exists():
        logger.warning(
            "Dataset files not found at %s. Run scripts/generate_testset.py first.",
            DATASETS_DIR,
        )
        return

    with open(test_queries_path) as f:
        queries = json.load(f)

    with open(golden_path) as f:
        golden = json.load(f)

    logger.info("Running RAGAS evaluation on %d examples ...", len(queries))
    results = run_ragas_eval(dataset_path=str(DATASETS_DIR))
    print("\n=== RAGAS Evaluation Results ===")
    for metric, score in results.items():
        print(f"  {metric}: {score:.4f}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
