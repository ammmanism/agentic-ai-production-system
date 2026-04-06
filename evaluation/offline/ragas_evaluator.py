from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall

def run_ragas_eval(dataset_path: str) -> dict:
    # Load your testset (questions, answers, contexts)
    # dataset = ... (mocked out for compilation)
    dataset = [] 
    result = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_recall])
    print(f"Faithfulness: {result['faithfulness']:.2f}")
    # Fail CI if below threshold
    assert result['faithfulness'] > 0.85
    return result
