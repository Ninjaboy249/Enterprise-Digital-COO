"""
Main FastAPI application entry point
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator
from pathlib import Path

from config import settings
from api.v1.router import api_router
from database.session import init_db, close_db
from memory.chromadb_client import init_chromadb, close_chromadb
from services.websocket_manager import websocket_manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Enterprise Digital COO...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize ChromaDB
    try:
        await init_chromadb()
        logger.info("ChromaDB initialized")
    except Exception as e:
        logger.warning(f"ChromaDB initialization failed: {e}. Continuing without ChromaDB.")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Enterprise Digital COO...")
    
    # Close database connections
    await close_db()
    logger.info("Database connections closed")
    
    # Close ChromaDB
    await close_chromadb()
    logger.info("ChromaDB closed")
    
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Enterprise Digital COO for Business Transformation",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Serve index.html at root
@app.get("/")
async def read_root():
    """Serve the main dashboard"""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Welcome to Enterprise Digital COO API", "docs": "/docs"}

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            
            # Echo back for now (can be extended for bidirectional communication)
            await websocket_manager.send_personal_message(
                f"Message received: {data}",
                client_id
            )
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

# Made with Bob
