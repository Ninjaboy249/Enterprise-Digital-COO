# ChromaDB Service Guide

## Overview

The ChromaDB Service provides vector database functionality for the Enterprise Digital COO system, enabling semantic search, memory storage, and retrieval of business insights, agent decisions, and knowledge.

## Features

- **Persistent Storage**: All data is stored persistently in the `./chroma_data` directory
- **Multiple Collections**: Organized storage for different types of data
- **Semantic Search**: Find similar documents using vector embeddings
- **Metadata Filtering**: Query documents based on metadata attributes
- **Batch Operations**: Efficiently add multiple documents at once
- **Default Embeddings**: Uses sentence-transformers (no OpenAI API required)

## Collections

The service automatically creates the following collections:

### 1. business_insights
- **Purpose**: Store business insights and analysis results
- **Use Cases**: Revenue analysis, market trends, performance metrics
- **Metadata**: type, category, severity, quarter, etc.

### 2. agent_decisions
- **Purpose**: Track agent decision history and reasoning
- **Use Cases**: Audit trail, decision analysis, learning from past decisions
- **Metadata**: agent, action, timestamp, confidence, etc.

### 3. anomaly_patterns
- **Purpose**: Store detected anomaly patterns and signatures
- **Use Cases**: Pattern recognition, anomaly detection, trend analysis
- **Metadata**: type, severity, frequency, impact, etc.

### 4. simulation_results
- **Purpose**: Store business simulation outcomes and scenarios
- **Use Cases**: Monte Carlo results, scenario planning, forecasting
- **Metadata**: simulation_type, confidence, parameters, etc.

### 5. executive_queries
- **Purpose**: Store executive questions and responses
- **Use Cases**: Knowledge base, FAQ, decision support
- **Metadata**: query_type, response_quality, timestamp, etc.

### 6. knowledge_base
- **Purpose**: General business knowledge and best practices
- **Use Cases**: Reference material, guidelines, procedures
- **Metadata**: topic, category, source, relevance, etc.

## Usage Examples

### Initialize Service

```python
from services.chromadb_service import get_chromadb_service

# Get service instance
service = await get_chromadb_service()
```

### Add a Document

```python
doc_id = await service.add_document(
    collection_name="business_insights",
    document="Revenue declined by 15% in Q4 due to increased competition.",
    metadata={
        "type": "insight",
        "category": "revenue",
        "severity": "high",
        "quarter": "Q4"
    }
)
```

### Add Multiple Documents

```python
doc_ids = await service.add_documents_batch(
    collection_name="business_insights",
    documents=[
        "Customer churn rate increased to 8%.",
        "New product launch exceeded expectations.",
        "Operating costs reduced by 10%."
    ],
    metadatas=[
        {"type": "insight", "category": "customer"},
        {"type": "insight", "category": "product"},
        {"type": "insight", "category": "operations"}
    ]
)
```

### Query for Similar Documents

```python
results = await service.query(
    collection_name="business_insights",
    query_text="Why is revenue decreasing?",
    n_results=5
)

for doc, distance in zip(results['documents'], results['distances']):
    print(f"Document: {doc}")
    print(f"Similarity: {1 - distance/2:.2f}")
```

### Search with Similarity Threshold

```python
similar = await service.search_similar_insights(
    query="customer retention problems",
    collection_name="business_insights",
    limit=5,
    min_similarity=0.7
)

for item in similar:
    print(f"Similarity: {item['similarity']:.2f}")
    print(f"Document: {item['document']}")
```

### Get Specific Document

```python
doc = await service.get_document(
    collection_name="business_insights",
    document_id="doc_123"
)

if doc:
    print(f"Content: {doc['document']}")
    print(f"Metadata: {doc['metadata']}")
```

### Update Document

```python
await service.update_document(
    collection_name="business_insights",
    document_id="doc_123",
    metadata={
        "type": "insight",
        "category": "revenue",
        "severity": "critical",
        "reviewed": True
    }
)
```

### Delete Document

```python
await service.delete_document(
    collection_name="business_insights",
    document_id="doc_123"
)
```

### Get Collection Statistics

```python
stats = await service.get_collection_stats("business_insights")
print(f"Collection: {stats['name']}")
print(f"Total documents: {stats['count']}")
```

## Integration with Agents

### Executive Decision Agent

```python
# Store agent decision
await service.add_document(
    collection_name="agent_decisions",
    document="Decided to investigate revenue decline in detail.",
    metadata={
        "agent": "executive",
        "action": "investigate",
        "confidence": 0.95,
        "timestamp": datetime.utcnow().isoformat()
    }
)

# Retrieve similar past decisions
past_decisions = await service.search_similar_insights(
    query="revenue decline investigation",
    collection_name="agent_decisions",
    limit=3
)
```

### Business Simulation Agent

```python
# Store simulation results
await service.add_document(
    collection_name="simulation_results",
    document="Monte Carlo simulation shows 70% probability of recovery in 6 months.",
    metadata={
        "simulation_type": "monte_carlo",
        "confidence": 0.7,
        "iterations": 10000,
        "scenario": "recovery"
    }
)
```

### Anomaly Detection

```python
# Store detected anomaly
await service.add_document(
    collection_name="anomaly_patterns",
    document="Unusual spike in customer complaints detected on weekends.",
    metadata={
        "type": "pattern",
        "severity": "medium",
        "frequency": "weekly",
        "impact": "customer_satisfaction"
    }
)
```

## Configuration

### Environment Variables

```env
# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_data
```

### Settings (config.py)

```python
CHROMA_PERSIST_DIRECTORY: str = "./chroma_data"
```

## Best Practices

### 1. Document Structure
- Keep documents concise and focused
- Include relevant context in the text
- Use consistent formatting

### 2. Metadata Design
- Use consistent metadata keys across documents
- Include timestamps for temporal queries
- Add severity/priority levels for filtering
- Use categorical values for easy filtering

### 3. Query Optimization
- Use specific queries for better results
- Set appropriate similarity thresholds
- Limit results to avoid information overload
- Use metadata filters to narrow results

### 4. Collection Organization
- Use appropriate collections for different data types
- Don't mix unrelated content in one collection
- Consider creating custom collections for specific use cases

### 5. Performance
- Use batch operations for multiple documents
- Cache frequently accessed documents
- Monitor collection sizes
- Clean up old/irrelevant documents periodically

## Troubleshooting

### Issue: Slow First Query
**Cause**: Sentence-transformers model needs to be downloaded
**Solution**: Wait for initial model download (happens once)

### Issue: Out of Memory
**Cause**: Too many documents or large embeddings
**Solution**: 
- Reduce batch sizes
- Clean up old documents
- Use metadata filtering to reduce search space

### Issue: Poor Search Results
**Cause**: Query doesn't match document content
**Solution**:
- Rephrase query to be more specific
- Lower similarity threshold
- Check if documents exist in collection

## API Reference

### ChromaDBService Class

#### Methods

- `initialize()`: Initialize client and collections
- `add_document()`: Add single document
- `add_documents_batch()`: Add multiple documents
- `query()`: Search for similar documents
- `get_document()`: Retrieve specific document
- `update_document()`: Update document content/metadata
- `delete_document()`: Remove document
- `get_collection_stats()`: Get collection information
- `search_similar_insights()`: Semantic search with threshold
- `close()`: Cleanup resources

### Helper Functions

- `get_chromadb_service()`: Get singleton service instance
- `close_chromadb_service()`: Close service and cleanup

## Testing

Run the test suite:

```bash
cd backend
python test_chromadb_service.py
```

The test suite covers:
- Service initialization
- Collection creation
- Document operations (add, query, update, delete)
- Batch operations
- Similarity search
- Collection statistics

## Future Enhancements

1. **Custom Embedding Functions**: Support for different embedding models
2. **Advanced Filtering**: Complex metadata queries
3. **Hybrid Search**: Combine semantic and keyword search
4. **Caching Layer**: Redis cache for frequent queries
5. **Analytics**: Usage statistics and performance metrics
6. **Backup/Restore**: Data backup and recovery tools
7. **Multi-tenancy**: Support for multiple organizations

## References

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Vector Databases Guide](https://www.pinecone.io/learn/vector-database/)

---

**Made with Bob**