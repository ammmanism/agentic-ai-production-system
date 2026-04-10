"""POST /ingest — document ingestion endpoint."""
from __future__ import annotations

from fastapi import APIRouter

from ..schemas import IngestRequest, IngestResponse
from rag.ingestion.pipeline import IngestionPipeline

router = APIRouter()


@router.post("", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest):
    """Ingest documents into the vector store."""
    pipeline = IngestionPipeline(collection_name=request.collection)
    ingested_count = pipeline.ingest(request.documents)
    
    return IngestResponse(
        ingested=ingested_count,
        collection=request.collection,
    )
