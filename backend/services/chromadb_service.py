"""
ChromaDB Service for Enterprise Digital COO
Provides vector database functionality for semantic search and memory storage
"""
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import json

from config import settings

logger = logging.getLogger(__name__)


class ChromaDBService:
    """Service for managing ChromaDB vector database operations"""
    
    def __init__(self):
        """Initialize ChromaDB client and collections"""
        self.client: Optional[chromadb.Client] = None
        self.embedding_function = None
        self.collections: Dict[str, chromadb.Collection] = {}
        
    async def initialize(self):
        """Initialize ChromaDB client and create collections"""
        try:
            # Initialize ChromaDB client with persistent storage (new API)
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY
            )
            
            # Use default embedding function (sentence-transformers)
            # This avoids OpenAI API compatibility issues and works offline
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
            
            logger.info("Using default embedding function (sentence-transformers)")
            
            # Create or get collections
            await self._initialize_collections()
            
            logger.info("ChromaDB service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB service: {e}")
            raise
    
    async def _initialize_collections(self):
        """Initialize all required collections"""
        collection_configs = [
            {
                "name": "business_insights",
                "metadata": {"description": "Business insights and analysis results"}
            },
            {
                "name": "agent_decisions",
                "metadata": {"description": "Agent decision history and reasoning"}
            },
            {
                "name": "anomaly_patterns",
                "metadata": {"description": "Detected anomaly patterns and signatures"}
            },
            {
                "name": "simulation_results",
                "metadata": {"description": "Business simulation outcomes and scenarios"}
            },
            {
                "name": "executive_queries",
                "metadata": {"description": "Executive questions and responses"}
            },
            {
                "name": "knowledge_base",
                "metadata": {"description": "General business knowledge and best practices"}
            }
        ]
        
        for config in collection_configs:
            try:
                collection = self.client.get_or_create_collection(
                    name=config["name"],
                    embedding_function=self.embedding_function,
                    metadata=config["metadata"]
                )
                self.collections[config["name"]] = collection
                logger.info(f"Collection '{config['name']}' initialized")
            except Exception as e:
                logger.error(f"Failed to initialize collection '{config['name']}': {e}")
    
    async def add_document(
        self,
        collection_name: str,
        document: str,
        metadata: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> str:
        """
        Add a document to a collection
        
        Args:
            collection_name: Name of the collection
            document: Text content to store
            metadata: Metadata associated with the document
            document_id: Optional custom ID for the document
            
        Returns:
            Document ID
        """
        try:
            collection = self.collections.get(collection_name)
            if not collection:
                raise ValueError(f"Collection '{collection_name}' not found")
            
            # Generate ID if not provided
            if not document_id:
                document_id = f"{collection_name}_{datetime.utcnow().timestamp()}"
            
            # Add timestamp to metadata
            metadata["timestamp"] = datetime.utcnow().isoformat()
            
            # Add document to collection
            collection.add(
                documents=[document],
                metadatas=[metadata],
                ids=[document_id]
            )
            
            logger.info(f"Document added to '{collection_name}': {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"Failed to add document to '{collection_name}': {e}")
            raise
    
    async def add_documents_batch(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        document_ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add multiple documents to a collection in batch
        
        Args:
            collection_name: Name of the collection
            documents: List of text contents
            metadatas: List of metadata dictionaries
            document_ids: Optional list of custom IDs
            
        Returns:
            List of document IDs
        """
        try:
            collection = self.collections.get(collection_name)
            if not collection:
                raise ValueError(f"Collection '{collection_name}' not found")
            
            # Generate IDs if not provided
            if not document_ids:
                timestamp = datetime.utcnow().timestamp()
                document_ids = [f"{collection_name}_{timestamp}_{i}" for i in range(len(documents))]
            
            # Add timestamps to all metadata
            for metadata in metadatas:
                metadata["timestamp"] = datetime.utcnow().isoformat()
            
            # Add documents in batch
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=document_ids
            )
            
            logger.info(f"Added {len(documents)} documents to '{collection_name}'")
            return document_ids
            
        except Exception as e:
            logger.error(f"Failed to add documents batch to '{collection_name}': {e}")
            raise
    
    async def query(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query a collection for similar documents
        
        Args:
            collection_name: Name of the collection
            query_text: Query text for semantic search
            n_results: Number of results to return
            where: Metadata filter conditions
            where_document: Document content filter conditions
            
        Returns:
            Query results with documents, distances, and metadata
        """
        try:
            collection = self.collections.get(collection_name)
            if not collection:
                raise ValueError(f"Collection '{collection_name}' not found")
            
            # Perform query
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            
            # Format results
            formatted_results = {
                "documents": results["documents"][0] if results["documents"] else [],
                "distances": results["distances"][0] if results["distances"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "ids": results["ids"][0] if results["ids"] else []
            }
            
            logger.info(f"Query executed on '{collection_name}': {len(formatted_results['documents'])} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to query '{collection_name}': {e}")
            raise
    
    async def get_document(
        self,
        collection_name: str,
        document_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID
        
        Args:
            collection_name: Name of the collection
            document_id: Document ID
            
        Returns:
            Document data or None if not found
        """
        try:
            collection = self.collections.get(collection_name)
            if not collection:
                raise ValueError(f"Collection '{collection_name}' not found")
            
            result = collection.get(ids=[document_id])
            
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "document": result["documents"][0],
                    "metadata": result["metadatas"][0]
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document from '{collection_name}': {e}")
            raise
    
    async def update_document(
        self,
        collection_name: str,
        document_id: str,
        document: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Update a document in a collection
        
        Args:
            collection_name: Name of the collection
            document_id: Document ID to update
            document: New document content (optional)
            metadata: New metadata (optional)
        """
        try:
            collection = self.collections.get(collection_name)
            if not collection:
                raise ValueError(f"Collection '{collection_name}' not found")
            
            update_data = {"ids": [document_id]}
            
            if document:
                update_data["documents"] = [document]
            
            if metadata:
                metadata["updated_at"] = datetime.utcnow().isoformat()
                update_data["metadatas"] = [metadata]
            
            collection.update(**update_data)
            logger.info(f"Document updated in '{collection_name}': {document_id}")
            
        except Exception as e:
            logger.error(f"Failed to update document in '{collection_name}': {e}")
            raise
    
    async def delete_document(
        self,
        collection_name: str,
        document_id: str
    ):
        """
        Delete a document from a collection
        
        Args:
            collection_name: Name of the collection
            document_id: Document ID to delete
        """
        try:
            collection = self.collections.get(collection_name)
            if not collection:
                raise ValueError(f"Collection '{collection_name}' not found")
            
            collection.delete(ids=[document_id])
            logger.info(f"Document deleted from '{collection_name}': {document_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete document from '{collection_name}': {e}")
            raise
    
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics for a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection statistics
        """
        try:
            collection = self.collections.get(collection_name)
            if not collection:
                raise ValueError(f"Collection '{collection_name}' not found")
            
            count = collection.count()
            
            return {
                "name": collection_name,
                "count": count,
                "metadata": collection.metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats for '{collection_name}': {e}")
            raise
    
    async def search_similar_insights(
        self,
        query: str,
        collection_name: str = "business_insights",
        limit: int = 5,
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar business insights
        
        Args:
            query: Search query
            collection_name: Collection to search in
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold (0-1)
            
        Returns:
            List of similar insights with scores
        """
        try:
            results = await self.query(
                collection_name=collection_name,
                query_text=query,
                n_results=limit
            )
            
            # Filter by similarity threshold
            # Note: ChromaDB returns distances, lower is better
            # Convert to similarity score (1 - normalized_distance)
            filtered_results = []
            for i, distance in enumerate(results["distances"]):
                similarity = 1 - (distance / 2)  # Normalize to 0-1 range
                if similarity >= min_similarity:
                    filtered_results.append({
                        "document": results["documents"][i],
                        "metadata": results["metadatas"][i],
                        "similarity": similarity,
                        "id": results["ids"][i]
                    })
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Failed to search similar insights: {e}")
            raise
    
    async def close(self):
        """Close ChromaDB client and cleanup resources"""
        try:
            if self.client:
                # ChromaDB client doesn't need explicit closing
                # but we can clear references
                self.collections.clear()
                self.client = None
                logger.info("ChromaDB service closed")
        except Exception as e:
            logger.error(f"Error closing ChromaDB service: {e}")


# Global service instance
_chromadb_service: Optional[ChromaDBService] = None


async def get_chromadb_service() -> ChromaDBService:
    """Get or create ChromaDB service instance"""
    global _chromadb_service
    
    if _chromadb_service is None:
        _chromadb_service = ChromaDBService()
        await _chromadb_service.initialize()
    
    return _chromadb_service


async def close_chromadb_service():
    """Close ChromaDB service"""
    global _chromadb_service
    
    if _chromadb_service:
        await _chromadb_service.close()
        _chromadb_service = None


# Made with Codex