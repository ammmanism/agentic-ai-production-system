"""RAG ingestion — vector store interface (Qdrant backed)."""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Thin wrapper around Qdrant for upsert and similarity search.

    Falls back to an in-memory list when QDRANT_URL is not configured
    so tests can run without a running Qdrant instance.
    """

    def __init__(self, collection: str = "default"):
        self._collection = collection
        qdrant_url = os.getenv("QDRANT_URL")

        if qdrant_url:
            try:
                from qdrant_client import QdrantClient  # type: ignore
                from qdrant_client.models import Distance, VectorParams  # type: ignore

                self._client = QdrantClient(
                    url=qdrant_url,
                    api_key=os.getenv("QDRANT_API_KEY"),
                )
                self._client.recreate_collection(
                    collection_name=collection,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                )
                logger.info("VectorStore connected to Qdrant at %s", qdrant_url)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Qdrant connection failed: %s — using in-memory store", exc)
                self._client = None
        else:
            logger.warning("QDRANT_URL not set — using in-memory stub store")
            self._client = None

        self._stub_store: List[Dict[str, Any]] = []

    def upsert(
        self,
        ids: List[str],
        vectors: List[List[float]],
        payloads: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Insert or update vectors in the store."""
        if self._client is None:
            for i, (vid, vec) in enumerate(zip(ids, vectors)):
                self._stub_store.append(
                    {"id": vid, "vector": vec, "payload": (payloads or [{}])[i]}
                )
            return

        from qdrant_client.models import PointStruct  # type: ignore

        points = [
            PointStruct(
                id=vid,
                vector=vec,
                payload=(payloads or [{}])[i],
            )
            for i, (vid, vec) in enumerate(zip(ids, vectors))
        ]
        self._client.upsert(collection_name=self._collection, points=points)

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Return the top-k nearest neighbours."""
        if self._client is None:
            # Stub: return first top_k items
            return self._stub_store[:top_k]

        results = self._client.search(
            collection_name=self._collection,
            query_vector=query_vector,
            limit=top_k,
        )
        return [{"id": r.id, "score": r.score, "payload": r.payload} for r in results]
