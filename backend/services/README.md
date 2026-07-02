# Services Module

This module contains service layer implementations for the Enterprise Digital COO system.

## Services

### 1. ChromaDB Service (`chromadb_service.py`)

Vector database service for semantic search and memory storage.

**Features:**
- Persistent vector storage
- Semantic search capabilities
- Multiple organized collections
- Batch operations support
- Default embeddings (no API key required)

**Collections:**
- `business_insights`: Business analysis and insights
- `agent_decisions`: Agent decision history
- `anomaly_patterns`: Detected anomaly patterns
- `simulation_results`: Simulation outcomes
- `executive_queries`: Executive Q&A
- `knowledge_base`: General business knowledge

**Usage:**
```python
from services.chromadb_service import get_chromadb_service

# Get service instance
service = await get_chromadb_service()

# Add document
doc_id = await service.add_document(
    collection_name="business_insights",
    document="Revenue analysis for Q4...",
    metadata={"category": "revenue", "quarter": "Q4"}
)

# Search
results = await service.query(
    collection_name="business_insights",
    query_text="revenue trends",
    n_results=5
)
```

See [CHROMADB_SERVICE_GUIDE.md](../docs/CHROMADB_SERVICE_GUIDE.md) for detailed documentation.

### 2. WebSocket Manager (`websocket_manager.py`)

Real-time communication service for client updates.

**Features:**
- Client connection management
- Personal and broadcast messaging
- Connection tracking

**Usage:**
```python
from services.websocket_manager import websocket_manager

# Send to specific client
await websocket_manager.send_personal_message(
    message="Update available",
    client_id="client_123"
)

# Broadcast to all
await websocket_manager.broadcast(
    message="System notification"
)
```

## Testing

Each service has a dedicated test file:

```bash
# Test ChromaDB Service
python test_chromadb_service.py

# Test WebSocket Manager
# (Requires running FastAPI server)
```

## Architecture

```
services/
├── __init__.py              # Service exports
├── chromadb_service.py      # Vector database service
├── websocket_manager.py     # WebSocket service
└── README.md               # This file
```

## Adding New Services

1. Create service file in `services/` directory
2. Implement service class with async methods
3. Add singleton pattern if needed
4. Export from `__init__.py`
5. Create test file
6. Update this README

Example template:

```python
"""
New Service Description
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class NewService:
    """Service description"""
    
    def __init__(self):
        """Initialize service"""
        pass
    
    async def initialize(self):
        """Setup service"""
        logger.info("Service initialized")
    
    async def close(self):
        """Cleanup resources"""
        logger.info("Service closed")


# Singleton pattern
_service_instance: Optional[NewService] = None


async def get_new_service() -> NewService:
    """Get or create service instance"""
    global _service_instance
    
    if _service_instance is None:
        _service_instance = NewService()
        await _service_instance.initialize()
    
    return _service_instance


async def close_new_service():
    """Close service"""
    global _service_instance
    
    if _service_instance:
        await _service_instance.close()
        _service_instance = None
```

## Best Practices

1. **Async/Await**: Use async methods for I/O operations
2. **Error Handling**: Catch and log exceptions appropriately
3. **Logging**: Use structured logging for debugging
4. **Singleton Pattern**: Use for stateful services
5. **Resource Cleanup**: Implement proper cleanup in `close()` methods
6. **Type Hints**: Use type annotations for better IDE support
7. **Documentation**: Add docstrings to all public methods

## Dependencies

- `chromadb`: Vector database
- `fastapi`: WebSocket support
- `pydantic`: Configuration management
- `logging`: Structured logging

## Configuration

Services use settings from `config.py`:

```python
from config import settings

# ChromaDB
CHROMA_PERSIST_DIRECTORY = settings.CHROMA_PERSIST_DIRECTORY

# WebSocket
# (No specific config needed)
```

## Monitoring

Services should implement health checks:

```python
async def health_check(self) -> dict:
    """Check service health"""
    return {
        "status": "healthy",
        "service": self.__class__.__name__,
        "details": {}
    }
```

## Future Services

Planned services for future implementation:

1. **Cache Service**: Redis-based caching
2. **Email Service**: Notification emails
3. **Analytics Service**: Usage analytics
4. **Backup Service**: Data backup/restore
5. **Monitoring Service**: Performance metrics
6. **Queue Service**: Task queue management

---

**Made with Codex**