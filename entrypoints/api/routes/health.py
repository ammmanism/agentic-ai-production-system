from fastapi import APIRouter
from datetime import datetime
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    """Check the health of the API and its environment."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("ENV", "development")
    }

@router.get("/version")
async def get_version():
    """Return the current application version."""
    return {"version": os.getenv("APP_VERSION", "1.0.0")}
