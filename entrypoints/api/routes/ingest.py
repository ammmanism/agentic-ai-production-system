"""POST /ingest — document ingestion endpoint."""
from __future__ import annotations

from fastapi import APIRouter

from ..schemas import IngestRequest, IngestResponse

router = APIRouter()


@router.post("", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest):
    """Ingest documents into the vector store."""
    # TODO: wire up rag.ingestion pipeline
    return IngestResponse(
        ingested=len(request.documents),
        collection=request.collection,
    )
