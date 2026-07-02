"""
Test script for ChromaDB Service
"""
import asyncio
import os
import sys
from pathlib import Path

# Set environment variable
os.environ['DEBUG'] = 'True'

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.chromadb_service import ChromaDBService
from config import settings


async def test_chromadb_service():
    """Test ChromaDB service functionality"""
    print("=" * 60)
    print("ChromaDB Service Test")
    print("=" * 60)
    
    service = ChromaDBService()
    
    try:
        # Test 1: Initialize service
        print("\n1. Initializing ChromaDB Service...")
        await service.initialize()
        print("[OK] Service initialized successfully")
        print(f"    Persist directory: {settings.CHROMA_PERSIST_DIRECTORY}")
        print(f"    Collections created: {len(service.collections)}")
        
        # Test 2: List collections
        print("\n2. Listing Collections...")
        for name, collection in service.collections.items():
            stats = await service.get_collection_stats(name)
            print(f"[OK] {name}: {stats['count']} documents")
        
        # Test 3: Add a document
        print("\n3. Adding Test Document...")
        doc_id = await service.add_document(
            collection_name="business_insights",
            document="Revenue declined by 15% in Q4 due to increased competition and market saturation.",
            metadata={
                "type": "insight",
                "category": "revenue",
                "severity": "high",
                "quarter": "Q4"
            }
        )
        print(f"[OK] Document added with ID: {doc_id}")
        
        # Test 4: Add multiple documents
        print("\n4. Adding Multiple Documents...")
        doc_ids = await service.add_documents_batch(
            collection_name="business_insights",
            documents=[
                "Customer churn rate increased to 8% from 5% in the previous quarter.",
                "New product launch exceeded expectations with 120% of target sales.",
                "Operating costs reduced by 10% through process optimization."
            ],
            metadatas=[
                {"type": "insight", "category": "customer", "severity": "medium"},
                {"type": "insight", "category": "product", "severity": "low"},
                {"type": "insight", "category": "operations", "severity": "low"}
            ]
        )
        print(f"[OK] Added {len(doc_ids)} documents")
        
        # Test 5: Query for similar documents
        print("\n5. Querying Similar Documents...")
        results = await service.query(
            collection_name="business_insights",
            query_text="Why is revenue decreasing?",
            n_results=3
        )
        print(f"[OK] Found {len(results['documents'])} similar documents:")
        for i, doc in enumerate(results['documents'][:3]):
            print(f"    {i+1}. {doc[:80]}...")
            print(f"       Distance: {results['distances'][i]:.4f}")
        
        # Test 6: Search with similarity threshold
        print("\n6. Searching with Similarity Threshold...")
        similar = await service.search_similar_insights(
            query="customer retention problems",
            limit=5,
            min_similarity=0.5
        )
        print(f"[OK] Found {len(similar)} relevant insights:")
        for item in similar:
            print(f"    - Similarity: {item['similarity']:.2f}")
            print(f"      {item['document'][:80]}...")
        
        # Test 7: Get specific document
        print("\n7. Retrieving Specific Document...")
        doc = await service.get_document(
            collection_name="business_insights",
            document_id=doc_id
        )
        if doc:
            print(f"[OK] Document retrieved:")
            print(f"    ID: {doc['id']}")
            print(f"    Content: {doc['document'][:80]}...")
        
        # Test 8: Update document
        print("\n8. Updating Document...")
        await service.update_document(
            collection_name="business_insights",
            document_id=doc_id,
            metadata={
                "type": "insight",
                "category": "revenue",
                "severity": "critical",
                "quarter": "Q4",
                "reviewed": True
            }
        )
        print(f"[OK] Document updated")
        
        # Test 9: Collection statistics
        print("\n9. Getting Collection Statistics...")
        stats = await service.get_collection_stats("business_insights")
        print(f"[OK] Collection: {stats['name']}")
        print(f"    Total documents: {stats['count']}")
        print(f"    Metadata: {stats['metadata']}")
        
        # Test 10: Test all collections
        print("\n10. Testing All Collections...")
        test_data = {
            "agent_decisions": {
                "document": "Executive agent decided to investigate revenue decline in detail.",
                "metadata": {"agent": "executive", "action": "investigate"}
            },
            "anomaly_patterns": {
                "document": "Unusual spike in customer complaints detected on weekends.",
                "metadata": {"type": "pattern", "severity": "medium"}
            },
            "simulation_results": {
                "document": "Monte Carlo simulation shows 70% probability of recovery in 6 months.",
                "metadata": {"simulation_type": "monte_carlo", "confidence": 0.7}
            }
        }
        
        for collection_name, data in test_data.items():
            doc_id = await service.add_document(
                collection_name=collection_name,
                document=data["document"],
                metadata=data["metadata"]
            )
            print(f"[OK] Added to {collection_name}: {doc_id}")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All ChromaDB Service tests passed!")
        print("=" * 60)
        
        # Summary
        print("\nSummary:")
        for name in service.collections.keys():
            stats = await service.get_collection_stats(name)
            print(f"  - {name}: {stats['count']} documents")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        print("\nClosing service...")
        await service.close()
        print("[OK] Service closed")


async def test_chromadb_without_openai():
    """Test ChromaDB with default embedding function (no OpenAI required)"""
    print("\n" + "=" * 60)
    print("ChromaDB Service Test (Without OpenAI)")
    print("=" * 60)
    
    try:
        import chromadb
        from chromadb.config import Settings
        
        print("\n1. Testing ChromaDB with default embeddings...")
        
        # Create client with default embedding (new API)
        client = chromadb.PersistentClient(
            path="./test_chroma_data"
        )
        
        # Create collection with default embedding
        collection = client.get_or_create_collection(
            name="test_collection",
            metadata={"description": "Test collection"}
        )
        
        print("[OK] ChromaDB client created with default embeddings")
        
        # Add test documents
        collection.add(
            documents=[
                "This is a test document about revenue.",
                "This document discusses customer satisfaction.",
                "This is about operational efficiency."
            ],
            metadatas=[
                {"type": "test", "category": "revenue"},
                {"type": "test", "category": "customer"},
                {"type": "test", "category": "operations"}
            ],
            ids=["doc1", "doc2", "doc3"]
        )
        
        print("[OK] Added 3 test documents")
        
        # Query
        results = collection.query(
            query_texts=["revenue problems"],
            n_results=2
        )
        
        print(f"[OK] Query successful, found {len(results['documents'][0])} results")
        for i, doc in enumerate(results['documents'][0]):
            print(f"    {i+1}. {doc}")
        
        print("\n[SUCCESS] ChromaDB works without OpenAI!")
        print("Note: Using default sentence-transformers embeddings")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("ChromaDB Service Testing Suite")
    print("=" * 60)
    
    # Check if OpenAI API key is available
    from config import settings
    has_openai = settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key"
    
    if has_openai:
        print("\nOpenAI API key detected - running full test suite")
        success = asyncio.run(test_chromadb_service())
    else:
        print("\nNo OpenAI API key - running basic ChromaDB test")
        success = asyncio.run(test_chromadb_without_openai())
    
    sys.exit(0 if success else 1)

# Made with Codex
