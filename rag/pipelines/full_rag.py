"""End-to-end RAG pipeline — ingest → retrieve → rerank → compress → answer."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from rag.ingestion.chunker import chunk_text
from rag.ingestion.embedder import embed_texts
from rag.ingestion.vector_store import VectorStore
from rag.retrieval.hybrid import hybrid_search, BM25
from rag.retrieval.reranker import rerank
from rag.retrieval.context_compressor import compress_context

logger = logging.getLogger(__name__)


class FullRAGPipeline:
    """
    Orchestrates the full RAG pipeline:
    Ingest → Embed → Store → Retrieve → Rerank → Compress → Return context.
    """

    def __init__(self, collection: str = "default"):
        self._store = VectorStore(collection=collection)
        self._bm25 = BM25()
        self._raw_docs: List[str] = []

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest(self, documents: List[str]) -> int:
        """Chunk, embed and store documents. Returns number of chunks stored."""
        chunks: List[str] = []
        for doc in documents:
            chunks.extend(chunk_text(doc))

        if not chunks:
            return 0

        embeddings = embed_texts(chunks)
        ids = [str(i) for i in range(len(chunks))]
        payloads = [{"text": c} for c in chunks]
        self._store.upsert(ids=ids, vectors=embeddings, payloads=payloads)

        # Update BM25 index
        self._raw_docs.extend(chunks)
        self._bm25.index(self._raw_docs)

        logger.info("Ingested %d chunks into collection", len(chunks))
        return len(chunks)

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Run the full RAG pipeline for a query.

        Returns a dict with ``context`` (compressed string) and ``sources``.
        """
        # 1. Dense retrieval
        query_vec = embed_texts([query])[0]
        dense_hits = self._store.search(query_vector=query_vec, top_k=top_k * 2)

        # 2. Sparse scores for the same candidates
        sparse_scores = [self._bm25.score(query, i) for i in range(min(len(self._raw_docs), len(dense_hits)))]
        if len(sparse_scores) < len(dense_hits):
            sparse_scores += [0.0] * (len(dense_hits) - len(sparse_scores))

        # 3. Hybrid fusion
        fused = hybrid_search(query, dense_hits, sparse_scores)

        # 4. Rerank
        reranked = rerank(query, fused, top_k=top_k)

        # 5. Compress context
        context = compress_context(query, reranked)

        return {"context": context, "sources": reranked}
