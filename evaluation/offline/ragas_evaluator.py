from typing import List, Dict, Any
from datasets import Dataset

# Lazy load ragas dependencies to keep the API server fast if imported accidentally
try:
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )
    import pandas as pd
except ImportError:
    pass

def evaluate_ragas(
    questions: List[str], 
    answers: List[str], 
    contexts: List[List[str]], 
    ground_truths: List[List[str]]
) -> Dict[str, float]:
    """
    Evaluates the RAG pipeline outputs using the RAGAS framework.
    Returns a dictionary of aggregated metrics.
    """
    
    # We must format the data exactly as the ragas evaluate() function expects
    data = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truths": ground_truths
    }
    
    dataset = Dataset.from_dict(data)
    
    # Run the rigorous evaluation
    result = evaluate(
        dataset=dataset,
        metrics=[
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy,
        ],
    )
    
    # Result object acts like a dict, extract values directly
    metrics_summary = {
        "faithfulness": result.get("faithfulness", 0.0),
        "answer_relevancy": result.get("answer_relevancy", 0.0),
        "context_precision": result.get("context_precision", 0.0),
        "context_recall": result.get("context_recall", 0.0),
    }
    
    return metrics_summary
