"""High-level document ingestion pipeline."""
import logging
import uuid
from typing import Dict, List, Any

from rag.ingestion.chunker import RecursiveTokenChunker
from rag.ingestion.embedder import SentenceEmbedder
from rag.ingestion.vector_store import VectorStore

logger = logging.getLogger(__name__)

class IngestionPipeline:
    def __init__(self, collection_name: str = "default"):
        self.chunker = RecursiveTokenChunker()
        self.embedder = SentenceEmbedder()
        self.vector_store = VectorStore(collection=collection_name)
        
    def ingest(self, documents: List[Dict[str, str]]) -> int:
        """
        Process a list of documents and store them in the vector DB.
        Documents should have 'id', 'text', and optionally 'metadata'.
        """
        logger.info(f"Ingesting {len(documents)} documents...")
        
        all_chunks = []
        for doc in documents:
            text = doc.get("text", "")
            if not text:
                continue
                
            doc_id = doc.get("id", str(uuid.uuid4()))
            metadata = doc.get("metadata", {})
            try:
                if isinstance(metadata, str):
                    import json
                    metadata = json.loads(metadata)
            except Exception:
                metadata = {}
            
            chunks = self.chunker.chunk(text)
            for i, chunk_text in enumerate(chunks):
                all_chunks.append({
                    "id": f"{doc_id}_chunk_{i}",
                    "text": chunk_text,
                    "metadata": {"doc_id": doc_id, **(metadata if isinstance(metadata, dict) else {})}
                })
        
        if not all_chunks:
            logger.warning("No valid chunks extracted from documents.")
            return 0
            
        texts = [c["text"] for c in all_chunks]
        embeddings = self.embedder.embed_batch(texts)
        
        payloads = [
            {"text": c["text"], "metadata": c["metadata"]}
            for c in all_chunks
        ]
        
        ids = [c["id"] for c in all_chunks]
        self.vector_store.upsert(ids=ids, vectors=embeddings, payloads=payloads)
        
        logger.info(f"Successfully ingested {len(all_chunks)} chunks.")
        return len(all_chunks)
