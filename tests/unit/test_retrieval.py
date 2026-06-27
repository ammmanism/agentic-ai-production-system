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

from rag.ingestion.vector_store import VectorStore

def test_vector_store_in_memory_search():
    store = VectorStore(collection="test_collection")
    # Insert some mock vectors
    ids = ["doc1", "doc2", "doc3"]
    # doc1 is [1, 0], doc2 is [0, 1], doc3 is [0.707, 0.707]
    vectors = [[1.0, 0.0], [0.0, 1.0], [0.707, 0.707]]
    payloads = [{"text": "doc1"}, {"text": "doc2"}, {"text": "doc3"}]
    store.upsert(ids, vectors, payloads)
    
    # Query vector close to doc1
    results = store.search([1.0, 0.0], top_k=2)
    assert len(results) == 2
    assert results[0]["id"] == "doc1"
    # Score should be ~1.0
    assert results[0]["score"] > 0.99
    
    # Query vector close to doc3
    results2 = store.search([0.7, 0.7], top_k=1)
    assert results2[0]["id"] == "doc3"

def test_vector_store_zero_vector():
    store = VectorStore()
    store.upsert(["doc1"], [[0.0, 0.0]])
    results = store.search([1.0, 1.0])
    # Should not crash, and yield no meaningful score (0) or skip
    assert len(results) == 0
