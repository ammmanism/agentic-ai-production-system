import logging
from typing import Dict, Any, List
from rag.ingestion.embedder import SentenceEmbedder
from rag.retrieval.hybrid import BM25, hybrid_search
from rag.retrieval.reranker import rerank

logger = logging.getLogger(__name__)

class FullRAGPipeline:
    """
    End-to-End Hybrid RAG Pipeline.
    Integrates Vector Storage, BM25 Indexing, and Cross-Encoder Reranking.
    """
    
    def __init__(self, alpha: float = 0.7, rerank_top_k: int = 5):
        self.alpha = alpha
        self.rerank_top_k = rerank_top_k
        self.embedder = SentenceEmbedder()
        self.bm25 = BM25()
        self.dense_index = []  # Mock dense vector store
        
    def ingest(self, documents: List[str]):
        logger.info(f"Ingesting {len(documents)} documents into RAG Pipeline.")
        self.bm25.index(documents)
        # Mock dense indexing
        self.dense_index = [{"id": i, "text": doc} for i, doc in enumerate(documents)]
        logger.info("Ingestion complete.")
        
    def answer(self, query: str) -> List[Dict[str, Any]]:
        logger.debug(f"Answering RAG query: {query}")
        
        # 1. Fetch Candidates (Mocking 20 documents)
        sparse_scores = [self.bm25.score(query, i) for i in range(len(self.dense_index))]
        
        # 2. Hybrid Merge
        fused_results = hybrid_search(query, self.dense_index, sparse_scores, alpha=self.alpha)
        
        # 3. Rerank Output
        final_candidates = rerank(query, fused_results, top_k=self.rerank_top_k)
        
        return final_candidates
