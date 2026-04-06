"""Unit tests for RAG retrieval components."""
import pytest
from rag.retrieval.hybrid import BM25, hybrid_search
from rag.ingestion.chunker import chunk_text


# ---------------------------------------------------------------------------
# Chunker tests
# ---------------------------------------------------------------------------

def test_chunk_short_text():
    text = "Hello world."
    chunks = chunk_text(text, chunk_size=512)
    assert len(chunks) >= 1
    assert "Hello world." in chunks[0]


def test_chunk_long_text():
    text = "A" * 600 + "\n\n" + "B" * 600
    chunks = chunk_text(text, chunk_size=512, chunk_overlap=0)
    assert len(chunks) >= 2


def test_chunk_empty_text():
    chunks = chunk_text("")
    assert chunks == []


# ---------------------------------------------------------------------------
# BM25 tests
# ---------------------------------------------------------------------------

DOCS = [
    "The quick brown fox jumps over the lazy dog",
    "LangGraph is a library for building stateful agents",
    "RAG combines retrieval with generation for better answers",
]


def test_bm25_returns_ranked_indices():
    bm25 = BM25()
    bm25.index(DOCS)
    top = bm25.get_top_k("RAG retrieval generation", top_k=3)
    assert len(top) == 3
    assert top[0] == 2  # Most relevant doc is index 2


def test_bm25_empty_query():
    bm25 = BM25()
    bm25.index(DOCS)
    # Empty query should return some result without error
    top = bm25.get_top_k("", top_k=2)
    assert len(top) == 2


# ---------------------------------------------------------------------------
# Hybrid search tests
# ---------------------------------------------------------------------------

def test_hybrid_search_merges_scores():
    dense = [
        {"id": "0", "score": 0.9, "payload": {"text": "doc 0"}},
        {"id": "1", "score": 0.5, "payload": {"text": "doc 1"}},
    ]
    sparse = [0.3, 0.8]

    result = hybrid_search("query", dense, sparse, alpha=0.5)
    assert len(result) == 2
    assert "combined_score" in result[0]


def test_hybrid_search_alpha_1_pure_dense():
    dense = [
        {"id": "a", "score": 1.0, "payload": {}},
        {"id": "b", "score": 0.1, "payload": {}},
    ]
    sparse = [0.0, 1.0]
    result = hybrid_search("q", dense, sparse, alpha=1.0)
    # With alpha=1 (pure dense), "a" should rank first
    assert result[0]["id"] == "a"


def test_hybrid_search_mismatch_raises():
    with pytest.raises(ValueError):
        hybrid_search("q", [{"id": "x", "score": 0.5}], [])
