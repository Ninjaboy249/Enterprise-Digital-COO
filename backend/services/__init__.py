"""
Services package for Enterprise Digital COO
"""
from .websocket_manager import websocket_manager

try:
    from .chromadb_service import (
        ChromaDBService,
        get_chromadb_service,
        close_chromadb_service,
    )
except ImportError:
    ChromaDBService = None

    async def get_chromadb_service():
        raise RuntimeError("ChromaDB service is not available in this runtime.")

    async def close_chromadb_service():
        return None

__all__ = [
    "websocket_manager",
    "ChromaDBService",
    "get_chromadb_service",
    "close_chromadb_service"
]

# Made with Codex
