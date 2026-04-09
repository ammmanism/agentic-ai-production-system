import pytest
from rag.retrieval.hybrid import BM25, hybrid_search

def test_bm25_scoring():
    bm25 = BM25()
    bm25.index(["This is a test document", "Another document about cats"])
    
    # Exact keyword match
    score = bm25.score("test", 0)
    assert score > 0.0
    
    # Missing keyword
    score = bm25.score("dogs", 1)
    assert score == 0.0

def test_hybrid_fusion():
    dense_results = [{"id": 1, "score": 0.9}, {"id": 2, "score": 0.4}]
    sparse_scores = [0.1, 0.8]
    
    # Heavy sparse weighting
    fused = hybrid_search("query", dense_results, sparse_scores, alpha=0.1)
    assert fused[0]["id"] == 2 # Because 0.8 * 0.9 > 0.9 * 0.1
