"""
ChromaDB Memory Client
Provides vector database operations for agent memory and knowledge retrieval
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
import logging
from functools import lru_cache

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from config import settings

logger = logging.getLogger(__name__)


class ChromaDBClient:
    """
    ChromaDB client for Enterprise Digital COO memory system
    
    Features:
    - 7 specialized collections
    - Hybrid search (vector + metadata)
    - Automatic embedding generation
    - Query caching
    - Batch operations
    """
    
    # Collection names
    COLLECTIONS = {
        "agent_decisions": "agent_decisions",
        "business_incidents": "business_incidents",
        "root_cause_analyses": "root_cause_analyses",
        "executive_recommendations": "executive_recommendations",
        "simulation_outcomes": "simulation_outcomes",
        "domain_knowledge": "domain_knowledge",
        "workflow_patterns": "workflow_patterns",
    }
    
    # HNSW index configuration
    HNSW_CONFIG = {
        "hnsw:space": "cosine",
        "hnsw:construction_ef": 200,
        "hnsw:search_ef": 100,
        "hnsw:M": 16,
    }
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        persist_directory: str = None,
    ):
        """
        Initialize ChromaDB client
        
        Args:
            host: ChromaDB server host
            port: ChromaDB server port
            persist_directory: Local persistence directory
        """
        self.host = host or settings.CHROMADB_HOST
        self.port = port or settings.CHROMADB_PORT
        self.persist_directory = persist_directory or settings.CHROMADB_PERSIST_DIR
        
        # Initialize client
        self.client = None
        self.collections = {}
        
        # Use default embedding function for ChromaDB (sentence-transformers)
        # Works offline and is compatible with all AI providers
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        logger.info("ChromaDB client initialized")
    
    async def connect(self) -> None:
        """Connect to ChromaDB and initialize collections"""
        try:
            # Create client
            if self.host and self.port:
                # Remote server
                self.client = chromadb.HttpClient(
                    host=self.host,
                    port=self.port,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=False,
                    )
                )
            else:
                # Local persistent client
                self.client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=False,
                    )
                )
            
            # Initialize collections
            await self._initialize_collections()
            
            logger.info("Connected to ChromaDB successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise
    
    async def _initialize_collections(self) -> None:
        """Initialize all collections with proper configuration"""
        for name, collection_name in self.COLLECTIONS.items():
            try:
                # Get or create collection
                collection = self.client.get_or_create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function,
                    metadata=self.HNSW_CONFIG,
                )
                self.collections[name] = collection
                
                logger.info(f"Initialized collection: {collection_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize collection {collection_name}: {e}")
                raise
    
    async def disconnect(self) -> None:
        """Disconnect from ChromaDB"""
        self.client = None
        self.collections = {}
        logger.info("Disconnected from ChromaDB")
    
    def _prepare_text(self, document: Dict[str, Any]) -> str:
        """
        Prepare document text for optimal embedding
        
        Args:
            document: Document with text and metadata
            
        Returns:
            Prepared text string
        """
        text_parts = [document["text"]]
        
        metadata = document.get("metadata", {})
        
        # Add contextual metadata
        if "domain" in metadata:
            text_parts.append(f"Domain: {metadata['domain']}")
        
        if "severity" in metadata:
            text_parts.append(f"Severity: {metadata['severity']}")
        
        if "tags" in metadata and metadata["tags"]:
            text_parts.append(f"Tags: {', '.join(metadata['tags'])}")
        
        return " | ".join(text_parts)
    
    async def add(
        self,
        collection: str,
        documents: List[Dict[str, Any]],
        batch_size: int = 100,
    ) -> List[str]:
        """
        Add documents to collection
        
        Args:
            collection: Collection name
            documents: List of documents with id, text, metadata
            batch_size: Batch size for processing
            
        Returns:
            List of document IDs
        """
        if collection not in self.collections:
            raise ValueError(f"Unknown collection: {collection}")
        
        coll = self.collections[collection]
        added_ids = []
        
        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            ids = [doc["id"] for doc in batch]
            texts = [self._prepare_text(doc) for doc in batch]
            metadatas = [doc.get("metadata", {}) for doc in batch]
            
            try:
                # Add to collection (embeddings generated automatically)
                coll.add(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas,
                )
                
                added_ids.extend(ids)
                logger.debug(f"Added {len(batch)} documents to {collection}")
                
            except Exception as e:
                logger.error(f"Failed to add batch to {collection}: {e}")
                raise
        
        logger.info(f"Added {len(added_ids)} documents to {collection}")
        return added_ids
    
    async def search(
        self,
        collection: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10,
        include_distances: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Search collection with hybrid search (vector + metadata)
        
        Args:
            collection: Collection name
            query: Search query text
            filters: Metadata filters (ChromaDB where clause)
            top_k: Number of results to return
            include_distances: Include similarity distances
            
        Returns:
            List of search results with metadata and distances
        """
        if collection not in self.collections:
            raise ValueError(f"Unknown collection: {collection}")
        
        coll = self.collections[collection]
        
        try:
            # Perform search
            results = coll.query(
                query_texts=[query],
                n_results=top_k,
                where=filters,
                include=["documents", "metadatas", "distances"] if include_distances else ["documents", "metadatas"],
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                result = {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                }
                
                if include_distances:
                    result["distance"] = results["distances"][0][i]
                    result["similarity"] = 1 - results["distances"][0][i]  # Convert distance to similarity
                
                formatted_results.append(result)
            
            logger.debug(f"Search in {collection} returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed in {collection}: {e}")
            raise
    
    async def search_multi(
        self,
        collections: List[str],
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across multiple collections
        
        Args:
            collections: List of collection names
            query: Search query text
            filters: Metadata filters
            top_k: Number of results per collection
            
        Returns:
            Dictionary mapping collection names to results
        """
        results = {}
        
        # Search each collection
        tasks = []
        for collection in collections:
            if collection in self.collections:
                tasks.append(self.search(collection, query, filters, top_k))
            else:
                logger.warning(f"Skipping unknown collection: {collection}")
        
        # Execute searches in parallel
        collection_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Map results to collections
        for i, collection in enumerate(collections):
            if collection in self.collections:
                if isinstance(collection_results[i], Exception):
                    logger.error(f"Search failed for {collection}: {collection_results[i]}")
                    results[collection] = []
                else:
                    results[collection] = collection_results[i]
        
        return results
    
    async def get(
        self,
        collection: str,
        ids: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Get documents by IDs
        
        Args:
            collection: Collection name
            ids: List of document IDs
            
        Returns:
            List of documents
        """
        if collection not in self.collections:
            raise ValueError(f"Unknown collection: {collection}")
        
        coll = self.collections[collection]
        
        try:
            results = coll.get(
                ids=ids,
                include=["documents", "metadatas"],
            )
            
            # Format results
            documents = []
            for i in range(len(results["ids"])):
                documents.append({
                    "id": results["ids"][i],
                    "text": results["documents"][i],
                    "metadata": results["metadatas"][i],
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Get failed in {collection}: {e}")
            raise
    
    async def update(
        self,
        collection: str,
        id: str,
        text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Update document in collection
        
        Args:
            collection: Collection name
            id: Document ID
            text: New text (optional, will re-embed)
            metadata: New metadata (optional, merged with existing)
        """
        if collection not in self.collections:
            raise ValueError(f"Unknown collection: {collection}")
        
        coll = self.collections[collection]
        
        try:
            # Get existing document
            existing = await self.get(collection, [id])
            if not existing:
                raise ValueError(f"Document {id} not found in {collection}")
            
            # Prepare update
            update_data = {"ids": [id]}
            
            if text is not None:
                # Re-embed with new text
                update_data["documents"] = [text]
            
            if metadata is not None:
                # Merge metadata
                existing_metadata = existing[0]["metadata"]
                existing_metadata.update(metadata)
                existing_metadata["updated_at"] = datetime.utcnow().isoformat()
                update_data["metadatas"] = [existing_metadata]
            
            # Update document
            coll.update(**update_data)
            
            logger.debug(f"Updated document {id} in {collection}")
            
        except Exception as e:
            logger.error(f"Update failed in {collection}: {e}")
            raise
    
    async def delete(
        self,
        collection: str,
        ids: List[str],
    ) -> None:
        """
        Delete documents from collection
        
        Args:
            collection: Collection name
            ids: List of document IDs to delete
        """
        if collection not in self.collections:
            raise ValueError(f"Unknown collection: {collection}")
        
        coll = self.collections[collection]
        
        try:
            coll.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from {collection}")
            
        except Exception as e:
            logger.error(f"Delete failed in {collection}: {e}")
            raise
    
    async def count(self, collection: str) -> int:
        """
        Get document count in collection
        
        Args:
            collection: Collection name
            
        Returns:
            Number of documents
        """
        if collection not in self.collections:
            raise ValueError(f"Unknown collection: {collection}")
        
        coll = self.collections[collection]
        return coll.count()
    
    async def archive_old_documents(
        self,
        collection: str,
        days: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Archive documents older than specified days
        
        Args:
            collection: Collection name
            days: Age threshold in days
            filters: Additional filters
            
        Returns:
            Number of documents archived
        """
        if collection not in self.collections:
            raise ValueError(f"Unknown collection: {collection}")
        
        # Calculate cutoff date
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        # Build filter
        archive_filter = {"timestamp": {"$lt": cutoff}}
        if filters:
            archive_filter.update(filters)
        
        # Get documents to archive
        coll = self.collections[collection]
        results = coll.get(
            where=archive_filter,
            include=["metadatas"],
        )
        
        if not results["ids"]:
            return 0
        
        # Delete from active collection
        await self.delete(collection, results["ids"])
        
        logger.info(f"Archived {len(results['ids'])} documents from {collection}")
        return len(results["ids"])
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check ChromaDB health and return statistics
        
        Returns:
            Health status dictionary
        """
        try:
            health = {
                "status": "healthy",
                "collections": {},
                "total_documents": 0,
            }
            
            # Get stats for each collection
            for name, collection_name in self.COLLECTIONS.items():
                if name in self.collections:
                    count = await self.count(name)
                    health["collections"][collection_name] = {
                        "count": count,
                        "status": "active",
                    }
                    health["total_documents"] += count
            
            return health
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }
    
    async def reset_collection(self, collection: str) -> None:
        """
        Reset collection (delete all documents)
        WARNING: Only use in development
        
        Args:
            collection: Collection name
        """
        if not settings.DEBUG:
            raise RuntimeError("reset_collection() only allowed in DEBUG mode")
        
        if collection not in self.collections:
            raise ValueError(f"Unknown collection: {collection}")
        
        # Delete and recreate collection
        self.client.delete_collection(name=self.COLLECTIONS[collection])
        await self._initialize_collections()
        
        logger.warning(f"Reset collection: {collection}")


# Singleton instance
_chromadb_client: Optional[ChromaDBClient] = None


async def get_chromadb_client() -> ChromaDBClient:
    """
    Get or create ChromaDB client singleton
    
    Returns:
        ChromaDBClient instance
    """
    global _chromadb_client
    
    if _chromadb_client is None:
        _chromadb_client = ChromaDBClient()
        await _chromadb_client.connect()
    
    return _chromadb_client


async def close_chromadb_client() -> None:
    """Close ChromaDB client"""
    global _chromadb_client
    
    if _chromadb_client is not None:
        await _chromadb_client.disconnect()
        _chromadb_client = None

# Aliases for compatibility with main.py
async def init_chromadb() -> None:
    """Initialize ChromaDB client (alias for get_chromadb_client)"""
    await get_chromadb_client()


async def close_chromadb() -> None:
    """Close ChromaDB client (alias for close_chromadb_client)"""
    await close_chromadb_client()


# Export public API
__all__ = [
    "ChromaDBClient",
    "get_chromadb_client",
    "close_chromadb_client",
    "init_chromadb",
    "close_chromadb",
]

# Made with Bob
