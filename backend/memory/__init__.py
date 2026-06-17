"""
Memory Module
Provides vector database operations for agent memory and knowledge retrieval
"""

from backend.memory.chromadb_client import (
    ChromaDBClient,
    get_chromadb_client,
    close_chromadb_client,
)

__all__ = [
    "ChromaDBClient",
    "get_chromadb_client",
    "close_chromadb_client",
]

# Made with Bob
