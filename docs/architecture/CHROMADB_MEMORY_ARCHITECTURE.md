# ChromaDB Memory Architecture for Enterprise Digital COO

## Overview

ChromaDB serves as the long-term memory system for the Enterprise Digital COO, enabling agents to learn from historical decisions, incidents, and outcomes. This document defines the complete vector database architecture.

---

## Architecture Principles

### 1. **Semantic Search First**
- Store business context as embeddings
- Enable similarity-based retrieval
- Support cross-domain knowledge transfer

### 2. **Multi-Collection Strategy**
- Separate collections by data type
- Optimize for different retrieval patterns
- Enable collection-specific configurations

### 3. **Rich Metadata**
- Store structured metadata alongside embeddings
- Enable hybrid search (vector + metadata filters)
- Support temporal and categorical filtering

### 4. **Memory Lifecycle**
- Automatic archival of old memories
- Relevance-based pruning
- Continuous learning from new data

---

## Collection Structure

### Collection Hierarchy

```
chromadb_enterprise_coo/
├── agent_decisions/          # Historical agent decisions
├── business_incidents/        # Anomalies and incidents
├── root_cause_analyses/       # RCA investigations
├── executive_recommendations/ # Strategic recommendations
├── simulation_outcomes/       # Simulation results
├── domain_knowledge/          # Business domain expertise
└── workflow_patterns/         # Successful workflow patterns
```

### Collection Specifications

#### 1. **agent_decisions**
**Purpose**: Store all agent decisions for learning and consistency

**Document Structure**:
```json
{
  "id": "decision_uuid",
  "text": "Sales Agent detected 15% revenue drop in Q2 2026. Root cause: 3 major deals delayed due to procurement issues. Recommended immediate escalation to procurement team and executive review.",
  "embedding": [0.123, -0.456, ...],  // 1536-dim OpenAI embedding
  "metadata": {
    "agent_name": "sales_agent",
    "decision_type": "anomaly_detection",
    "domain": "sales",
    "severity": "high",
    "confidence_score": 0.87,
    "timestamp": "2026-06-15T10:30:00Z",
    "workflow_id": "wf_12345",
    "anomaly_id": "anom_67890",
    "outcome": "successful",
    "tags": ["revenue_drop", "procurement_delay", "escalation"]
  }
}
```

**Metadata Schema**:
- `agent_name` (string): Which agent made the decision
- `decision_type` (string): anomaly_detection, root_cause, recommendation, simulation
- `domain` (string): sales, finance, supply_chain, procurement, hr, risk
- `severity` (string): low, medium, high, critical
- `confidence_score` (float): 0.0-1.0
- `timestamp` (datetime): When decision was made
- `workflow_id` (string): Associated workflow
- `anomaly_id` (string): Related anomaly (if applicable)
- `outcome` (string): successful, failed, pending
- `tags` (array): Searchable keywords

**Retrieval Patterns**:
- Find similar past decisions
- Filter by agent, domain, severity
- Time-based retrieval (last 30/90 days)
- Outcome-based learning (successful decisions only)

---

#### 2. **business_incidents**
**Purpose**: Store anomalies and business incidents for pattern recognition

**Document Structure**:
```json
{
  "id": "incident_uuid",
  "text": "Critical inventory stockout detected for Product SKU-12345. Quantity dropped from 500 to 0 units in 48 hours. Expected restock in 14 days. High revenue impact: $250K potential loss. Similar incident occurred 6 months ago with same supplier.",
  "embedding": [0.234, -0.567, ...],
  "metadata": {
    "incident_type": "stockout",
    "domain": "supply_chain",
    "severity": "critical",
    "detected_at": "2026-06-15T08:00:00Z",
    "resolved_at": "2026-06-20T15:30:00Z",
    "resolution_time_hours": 127.5,
    "financial_impact": 250000.0,
    "affected_products": ["SKU-12345"],
    "affected_regions": ["North America"],
    "root_cause": "supplier_delay",
    "recurrence": true,
    "previous_incident_id": "incident_abc123",
    "tags": ["stockout", "supplier_delay", "high_impact"]
  }
}
```

**Metadata Schema**:
- `incident_type` (string): stockout, revenue_drop, cash_flow_issue, turnover_spike, risk_event
- `domain` (string): Business domain
- `severity` (string): low, medium, high, critical
- `detected_at` (datetime): Detection timestamp
- `resolved_at` (datetime): Resolution timestamp (null if open)
- `resolution_time_hours` (float): Time to resolve
- `financial_impact` (float): Dollar impact
- `affected_products` (array): Product SKUs
- `affected_regions` (array): Geographic regions
- `root_cause` (string): Identified root cause
- `recurrence` (boolean): Is this a recurring issue?
- `previous_incident_id` (string): Link to previous similar incident
- `tags` (array): Searchable keywords

**Retrieval Patterns**:
- Find similar historical incidents
- Identify recurring patterns
- Filter by severity, domain, financial impact
- Time-series analysis (incident frequency)

---

#### 3. **root_cause_analyses**
**Purpose**: Store RCA investigations for knowledge reuse

**Document Structure**:
```json
{
  "id": "rca_uuid",
  "text": "Root Cause Analysis: Q2 Revenue Drop. Primary cause: 3 enterprise deals ($2M total) delayed due to procurement bottleneck. Contributing factors: (1) New vendor approval process added 30 days, (2) Legal review backlog, (3) Budget freeze in customer organizations. Recommended actions: Streamline vendor approval, add legal resources, improve customer budget forecasting.",
  "embedding": [0.345, -0.678, ...],
  "metadata": {
    "rca_id": "rca_12345",
    "incident_id": "incident_67890",
    "domain": "sales",
    "analysis_method": "5_whys",
    "primary_cause": "procurement_bottleneck",
    "contributing_factors": ["vendor_approval_delay", "legal_backlog", "customer_budget_freeze"],
    "confidence_score": 0.92,
    "analyzed_by": "executive_decision_agent",
    "analyzed_at": "2026-06-16T14:00:00Z",
    "validation_status": "validated",
    "actions_taken": ["streamline_approval", "hire_legal_staff"],
    "effectiveness_score": 0.85,
    "tags": ["revenue_drop", "procurement", "process_improvement"]
  }
}
```

**Metadata Schema**:
- `rca_id` (string): Unique RCA identifier
- `incident_id` (string): Related incident
- `domain` (string): Business domain
- `analysis_method` (string): 5_whys, fishbone, fault_tree, pareto
- `primary_cause` (string): Main root cause
- `contributing_factors` (array): Secondary causes
- `confidence_score` (float): Analysis confidence
- `analyzed_by` (string): Agent that performed RCA
- `analyzed_at` (datetime): Analysis timestamp
- `validation_status` (string): validated, pending, rejected
- `actions_taken` (array): Implemented actions
- `effectiveness_score` (float): How effective were actions (0-1)
- `tags` (array): Searchable keywords

**Retrieval Patterns**:
- Find similar root causes
- Learn from effective actions
- Filter by domain, method, effectiveness
- Cross-domain pattern recognition

---

#### 4. **executive_recommendations**
**Purpose**: Store strategic recommendations for learning

**Document Structure**:
```json
{
  "id": "recommendation_uuid",
  "text": "Executive Recommendation: Implement automated vendor approval system. Expected ROI: 300% over 12 months. Reduces approval time from 30 to 5 days. Estimated cost: $150K implementation, $30K annual maintenance. Risk: Medium (integration complexity). Timeline: 90 days. Dependencies: IT infrastructure upgrade, legal process redesign.",
  "embedding": [0.456, -0.789, ...],
  "metadata": {
    "recommendation_id": "rec_12345",
    "workflow_id": "wf_67890",
    "priority": 9,
    "category": "process_automation",
    "estimated_roi": 3.0,
    "implementation_cost": 150000.0,
    "annual_cost": 30000.0,
    "timeline_days": 90,
    "risk_level": "medium",
    "status": "approved",
    "approved_by": "coo@company.com",
    "approved_at": "2026-06-17T09:00:00Z",
    "implemented_at": "2026-09-15T00:00:00Z",
    "actual_roi": 3.2,
    "actual_cost": 145000.0,
    "success_score": 0.95,
    "tags": ["automation", "procurement", "high_roi"]
  }
}
```

**Metadata Schema**:
- `recommendation_id` (string): Unique identifier
- `workflow_id` (string): Source workflow
- `priority` (int): 1-10 ranking
- `category` (string): process_automation, cost_reduction, revenue_growth, risk_mitigation
- `estimated_roi` (float): Expected return multiple
- `implementation_cost` (float): One-time cost
- `annual_cost` (float): Recurring cost
- `timeline_days` (int): Implementation timeline
- `risk_level` (string): low, medium, high
- `status` (string): pending, approved, rejected, implemented
- `approved_by` (string): Approver email
- `approved_at` (datetime): Approval timestamp
- `implemented_at` (datetime): Implementation timestamp
- `actual_roi` (float): Realized ROI
- `actual_cost` (float): Actual cost
- `success_score` (float): 0-1 success rating
- `tags` (array): Searchable keywords

**Retrieval Patterns**:
- Find similar successful recommendations
- Learn from high-ROI initiatives
- Filter by category, priority, success_score
- Compare estimated vs actual outcomes

---

#### 5. **simulation_outcomes**
**Purpose**: Store simulation results for predictive learning

**Document Structure**:
```json
{
  "id": "simulation_uuid",
  "text": "Monte Carlo Simulation: Revenue Recovery Scenario. Tested 3 interventions: (1) Expedite procurement, (2) Offer customer incentives, (3) Increase sales team. Best case: Revenue recovers to $10M in 60 days (90th percentile). Most likely: $8.5M in 75 days (median). Worst case: $7M in 90 days (10th percentile). Recommended: Intervention #1 + #2 for optimal outcome.",
  "embedding": [0.567, -0.890, ...],
  "metadata": {
    "simulation_id": "sim_12345",
    "workflow_id": "wf_67890",
    "simulation_type": "monte_carlo",
    "scenario_name": "revenue_recovery",
    "iterations": 10000,
    "interventions": ["expedite_procurement", "customer_incentives", "increase_sales_team"],
    "best_case_revenue": 10000000.0,
    "most_likely_revenue": 8500000.0,
    "worst_case_revenue": 7000000.0,
    "confidence_interval_95": [7500000.0, 9500000.0],
    "recommended_action": "intervention_1_and_2",
    "actual_outcome": 8700000.0,
    "prediction_accuracy": 0.98,
    "tags": ["revenue_recovery", "monte_carlo", "high_accuracy"]
  }
}
```

**Metadata Schema**:
- `simulation_id` (string): Unique identifier
- `workflow_id` (string): Source workflow
- `simulation_type` (string): monte_carlo, scenario_analysis, sensitivity_analysis
- `scenario_name` (string): Descriptive name
- `iterations` (int): Number of simulation runs
- `interventions` (array): Tested interventions
- `best_case_revenue` (float): 90th percentile outcome
- `most_likely_revenue` (float): Median outcome
- `worst_case_revenue` (float): 10th percentile outcome
- `confidence_interval_95` (array): [lower, upper] bounds
- `recommended_action` (string): Best intervention
- `actual_outcome` (float): Real-world result
- `prediction_accuracy` (float): 0-1 accuracy score
- `tags` (array): Searchable keywords

**Retrieval Patterns**:
- Find similar scenarios
- Learn from accurate predictions
- Filter by simulation_type, accuracy
- Compare predicted vs actual outcomes

---

#### 6. **domain_knowledge**
**Purpose**: Store business domain expertise and best practices

**Document Structure**:
```json
{
  "id": "knowledge_uuid",
  "text": "Sales Best Practice: Enterprise deals typically have 90-120 day sales cycles. Key success factors: (1) Executive sponsorship, (2) Multi-threaded engagement, (3) Clear ROI demonstration, (4) Reference customers. Common failure modes: Single-threaded relationships, unclear value proposition, competitive displacement.",
  "embedding": [0.678, -0.901, ...],
  "metadata": {
    "knowledge_type": "best_practice",
    "domain": "sales",
    "topic": "enterprise_sales",
    "source": "historical_analysis",
    "confidence_score": 0.95,
    "usage_count": 47,
    "last_used": "2026-06-15T10:00:00Z",
    "effectiveness_score": 0.88,
    "tags": ["sales", "enterprise", "best_practice"]
  }
}
```

---

#### 7. **workflow_patterns**
**Purpose**: Store successful workflow execution patterns

**Document Structure**:
```json
{
  "id": "pattern_uuid",
  "text": "Successful Workflow Pattern: Revenue Drop Response. Sequence: (1) Sales Agent detects anomaly, (2) Finance Agent validates impact, (3) Supply Chain Agent checks inventory, (4) Executive Agent synthesizes, (5) Simulation Agent models recovery, (6) Human approval, (7) Implementation. Average resolution time: 48 hours. Success rate: 92%.",
  "embedding": [0.789, -0.012, ...],
  "metadata": {
    "pattern_name": "revenue_drop_response",
    "workflow_type": "revenue_drop",
    "agent_sequence": ["sales", "finance", "supply_chain", "executive", "simulation"],
    "average_duration_hours": 48.0,
    "success_rate": 0.92,
    "usage_count": 23,
    "last_used": "2026-06-15T12:00:00Z",
    "tags": ["revenue_drop", "high_success", "fast_resolution"]
  }
}
```

---

## Embedding Strategy

### 1. **Embedding Model Selection**

**Primary Model**: OpenAI `text-embedding-3-large`
- **Dimensions**: 3072 (can be reduced to 1536 for performance)
- **Context Window**: 8,191 tokens
- **Performance**: State-of-the-art semantic understanding
- **Cost**: $0.13 per 1M tokens

**Fallback Model**: OpenAI `text-embedding-3-small`
- **Dimensions**: 1536
- **Context Window**: 8,191 tokens
- **Performance**: Good for most use cases
- **Cost**: $0.02 per 1M tokens

### 2. **Text Preparation Pipeline**

```python
def prepare_text_for_embedding(document: dict) -> str:
    """
    Prepare document text for optimal embedding
    
    Strategy:
    1. Combine key fields into coherent text
    2. Add context from metadata
    3. Optimize for semantic search
    """
    
    # Core content
    text_parts = [document["text"]]
    
    # Add contextual metadata
    if "domain" in document["metadata"]:
        text_parts.append(f"Domain: {document['metadata']['domain']}")
    
    if "severity" in document["metadata"]:
        text_parts.append(f"Severity: {document['metadata']['severity']}")
    
    if "tags" in document["metadata"]:
        text_parts.append(f"Tags: {', '.join(document['metadata']['tags'])}")
    
    # Combine with separators
    return " | ".join(text_parts)
```

### 3. **Embedding Optimization**

**Chunking Strategy**:
- **Max Chunk Size**: 8,000 tokens (leave buffer for context)
- **Overlap**: 200 tokens between chunks
- **Splitting**: Semantic boundaries (paragraphs, sentences)

**Batch Processing**:
- **Batch Size**: 100 documents per API call
- **Rate Limiting**: 3,000 requests/min (OpenAI tier 3)
- **Retry Logic**: Exponential backoff on failures

**Caching**:
- Cache embeddings in Redis (24-hour TTL)
- Avoid re-embedding unchanged documents
- Invalidate cache on document updates

---

## Retrieval Strategy

### 1. **Hybrid Search Architecture**

```python
def hybrid_search(
    query: str,
    collection: str,
    filters: dict = None,
    top_k: int = 10,
    rerank: bool = True
) -> list:
    """
    Hybrid search combining vector similarity and metadata filtering
    
    Steps:
    1. Generate query embedding
    2. Vector similarity search (top 50)
    3. Apply metadata filters
    4. Rerank by relevance
    5. Return top K results
    """
    pass
```

### 2. **Search Modes**

#### **Semantic Search** (Default)
```python
# Find similar decisions
results = memory.search(
    collection="agent_decisions",
    query="revenue drop due to procurement delays",
    top_k=5
)
```

#### **Filtered Search**
```python
# Find high-severity incidents in last 30 days
results = memory.search(
    collection="business_incidents",
    query="inventory stockout",
    filters={
        "severity": "critical",
        "detected_at": {"$gte": "2026-05-15T00:00:00Z"}
    },
    top_k=10
)
```

#### **Cross-Collection Search**
```python
# Search across multiple collections
results = memory.search_multi(
    collections=["agent_decisions", "root_cause_analyses"],
    query="procurement bottleneck solutions",
    top_k=5
)
```

#### **Temporal Search**
```python
# Find recent successful recommendations
results = memory.search(
    collection="executive_recommendations",
    query="process automation",
    filters={
        "status": "implemented",
        "success_score": {"$gte": 0.8},
        "implemented_at": {"$gte": "2026-01-01T00:00:00Z"}
    },
    top_k=5
)
```

### 3. **Reranking Strategy**

**Two-Stage Retrieval**:
1. **Stage 1**: Vector search retrieves top 50 candidates
2. **Stage 2**: Rerank by:
   - Recency (exponential decay)
   - Relevance score
   - Success/effectiveness metrics
   - Domain match

```python
def rerank_results(results: list, query_metadata: dict) -> list:
    """
    Rerank search results by multiple factors
    
    Scoring:
    - Vector similarity: 40%
    - Recency: 20%
    - Success metrics: 20%
    - Domain match: 20%
    """
    pass
```

---

## Metadata Schema Standards

### Common Fields (All Collections)

```python
COMMON_METADATA = {
    "id": str,              # Unique identifier
    "timestamp": datetime,  # Creation timestamp
    "domain": str,          # Business domain
    "tags": List[str],      # Searchable keywords
    "version": int,         # Document version
}
```

### Domain-Specific Fields

```python
DECISION_METADATA = {
    **COMMON_METADATA,
    "agent_name": str,
    "decision_type": str,
    "confidence_score": float,
    "outcome": str,
}

INCIDENT_METADATA = {
    **COMMON_METADATA,
    "severity": str,
    "financial_impact": float,
    "resolution_time_hours": float,
    "recurrence": bool,
}

RCA_METADATA = {
    **COMMON_METADATA,
    "analysis_method": str,
    "primary_cause": str,
    "effectiveness_score": float,
}
```

---

## Memory Lifecycle Management

### 1. **Ingestion Pipeline**

```
New Data → Validation → Text Preparation → Embedding Generation → 
Metadata Enrichment → ChromaDB Storage → Index Update
```

**Validation Rules**:
- Required fields present
- Metadata schema compliance
- Text length within limits
- No duplicate IDs

### 2. **Update Strategy**

**Versioning**:
- Increment version number on updates
- Keep previous versions for audit trail
- Link versions with `previous_version_id`

**Partial Updates**:
- Update metadata without re-embedding
- Re-embed only if text changes significantly
- Use edit distance threshold (> 20% change)

### 3. **Archival Policy**

**Time-Based Archival**:
```python
ARCHIVAL_RULES = {
    "agent_decisions": 365,      # 1 year
    "business_incidents": 730,   # 2 years
    "root_cause_analyses": 1095, # 3 years
    "executive_recommendations": 1825,  # 5 years
    "simulation_outcomes": 365,  # 1 year
    "domain_knowledge": None,    # Never archive
    "workflow_patterns": None,   # Never archive
}
```

**Relevance-Based Pruning**:
- Archive low-usage documents (< 5 retrievals in 6 months)
- Keep high-value documents (success_score > 0.8)
- Preserve unique patterns (low similarity to other docs)

### 4. **Backup & Recovery**

**Backup Strategy**:
- Daily snapshots to S3/GCS
- Incremental backups every 6 hours
- 30-day retention for daily backups
- 1-year retention for monthly backups

**Recovery Procedures**:
- Point-in-time recovery within 30 days
- Collection-level restore
- Document-level restore

---

## Performance Optimization

### 1. **Indexing Strategy**

**HNSW Index Configuration**:
```python
collection_config = {
    "hnsw:space": "cosine",           # Similarity metric
    "hnsw:construction_ef": 200,      # Build quality
    "hnsw:search_ef": 100,            # Search quality
    "hnsw:M": 16,                     # Connections per node
}
```

### 2. **Query Optimization**

**Caching**:
- Cache frequent queries (Redis, 1-hour TTL)
- Cache query embeddings (24-hour TTL)
- Invalidate on collection updates

**Batch Retrieval**:
- Batch similar queries
- Parallel collection searches
- Async query execution

### 3. **Scaling Strategy**

**Horizontal Scaling**:
- Shard collections by domain
- Replicate for read scaling
- Load balance across replicas

**Vertical Scaling**:
- Increase memory for larger indexes
- SSD storage for faster I/O
- GPU acceleration for embeddings

---

## Integration Patterns

### 1. **Agent Memory Integration**

```python
class BaseAgent:
    async def _retrieve_memory(self, context: dict) -> list:
        """Retrieve relevant memories for decision-making"""
        
        # Build search query from context
        query = self._build_memory_query(context)
        
        # Search relevant collections
        decisions = await self.memory.search(
            collection="agent_decisions",
            query=query,
            filters={"agent_name": self.name, "outcome": "successful"},
            top_k=5
        )
        
        incidents = await self.memory.search(
            collection="business_incidents",
            query=query,
            filters={"domain": self.domain},
            top_k=3
        )
        
        # Combine and return
        return decisions + incidents
```

### 2. **Workflow Memory Integration**

```python
class RevenueDropWorkflow:
    async def _load_workflow_patterns(self) -> dict:
        """Load successful workflow patterns"""
        
        patterns = await self.memory.search(
            collection="workflow_patterns",
            query="revenue drop response",
            filters={"success_rate": {"$gte": 0.8}},
            top_k=3
        )
        
        return patterns[0] if patterns else None
```

### 3. **Learning Loop**

```python
async def store_decision_outcome(
    decision_id: str,
    outcome: str,
    effectiveness_score: float
):
    """Update decision with outcome for learning"""
    
    await memory.update(
        collection="agent_decisions",
        id=decision_id,
        metadata={
            "outcome": outcome,
            "effectiveness_score": effectiveness_score,
            "updated_at": datetime.utcnow()
        }
    )
```

---

## Monitoring & Observability

### Key Metrics

```python
MEMORY_METRICS = {
    "collection_size": "Number of documents per collection",
    "query_latency_p95": "95th percentile query time",
    "embedding_latency_p95": "95th percentile embedding time",
    "cache_hit_rate": "Percentage of cached queries",
    "retrieval_relevance": "Average relevance score",
    "storage_size_gb": "Total storage used",
}
```

### Health Checks

```python
async def memory_health_check() -> dict:
    """Check ChromaDB health"""
    return {
        "status": "healthy",
        "collections": 7,
        "total_documents": 125000,
        "avg_query_latency_ms": 45,
        "cache_hit_rate": 0.73,
        "storage_gb": 12.5,
    }
```

---

## Security & Privacy

### 1. **Access Control**

```python
COLLECTION_PERMISSIONS = {
    "agent_decisions": ["agents", "admin"],
    "business_incidents": ["agents", "executives", "admin"],
    "executive_recommendations": ["executives", "admin"],
    "simulation_outcomes": ["agents", "executives", "admin"],
}
```

### 2. **Data Sanitization**

- Remove PII before embedding
- Anonymize sensitive business data
- Encrypt metadata at rest
- Audit log all access

### 3. **Compliance**

- GDPR: Right to deletion
- SOC 2: Audit trails
- HIPAA: PHI protection (if applicable)

---

## Summary

**Collections**: 7 specialized collections  
**Embedding Model**: OpenAI text-embedding-3-large (3072-dim)  
**Search Strategy**: Hybrid (vector + metadata)  
**Retrieval Modes**: 4 (semantic, filtered, cross-collection, temporal)  
**Lifecycle**: Automated archival and pruning  
**Performance**: < 50ms query latency (p95)  
**Scalability**: Horizontal sharding + replication  

**Status**: ✅ Architecture Complete - Ready for Implementation