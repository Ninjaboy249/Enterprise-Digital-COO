"""
API v1 Router - Main router for all v1 endpoints
"""
from fastapi import APIRouter
from api.v1.endpoints import metrics
from api.v1.endpoints import reports

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

# Made with Bob