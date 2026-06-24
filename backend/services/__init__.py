"""
Services package for Enterprise Digital COO
"""
from .websocket_manager import websocket_manager
from .chromadb_service import (
    ChromaDBService,
    get_chromadb_service,
    close_chromadb_service
)

__all__ = [
    "websocket_manager",
    "ChromaDBService",
    "get_chromadb_service",
    "close_chromadb_service"
]

# Made with Bob