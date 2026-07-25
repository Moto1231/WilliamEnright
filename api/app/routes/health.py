"""Health check endpoints"""
from fastapi import APIRouter, Depends
from app.db.mongodb import get_mongodb

router = APIRouter(tags=["health"])


@router.get("/health", tags=["health"])
async def health_check():
    """Check API health"""
    return {"status": "ok", "service": "AI Chat API"}


@router.get("/health/db", tags=["health"])
async def health_check_db(db = Depends(get_mongodb)):
    """Check database connection"""
    try:
        db.command("ping")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}
