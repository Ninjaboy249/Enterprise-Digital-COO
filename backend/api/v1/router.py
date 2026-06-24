"""
API v1 Router - Main router for all v1 endpoints
"""
from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

# Import and include sub-routers
# from api.v1.endpoints import metrics, recommendations, simulations, agents

# api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
# api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
# api_router.include_router(simulations.router, prefix="/simulations", tags=["simulations"])
# api_router.include_router(agents.router, prefix="/agents", tags=["agents"])

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

# Made with Bob