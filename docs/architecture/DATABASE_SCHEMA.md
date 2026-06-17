# Database Schema Design

## 1. PostgreSQL Schema (Relational Data)

### 1.1 Core Business Entities

```sql
-- ============================================================================
-- SALES DOMAIN
-- ============================================================================

CREATE TABLE sales_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    region VARCHAR(100) NOT NULL,
    product_category VARCHAR(100),
    revenue DECIMAL(15, 2) NOT NULL,
    units_sold INTEGER NOT NULL,
    conversion_rate DECIMAL(5, 4),
    customer_acquisition_cost DECIMAL(10, 2),
    average_deal_size DECIMAL(10, 2),
    pipeline_value DECIMAL(15, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_sales_timestamp (timestamp),
    INDEX idx_sales_region (region)
);

CREATE TABLE sales_pipeline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id VARCHAR(100) UNIQUE NOT NULL,
    stage VARCHAR(50) NOT NULL,
    value DECIMAL(15, 2) NOT NULL,
    probability DECIMAL(3, 2),
    expected_close_date DATE,
    age_days INTEGER,
    sales_rep_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_pipeline_stage (stage),
    INDEX idx_pipeline_close_date (expected_close_date)
);

-- ============================================================================
-- FINANCE DOMAIN
-- ============================================================================

CREATE TABLE finance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- revenue, expense, cash_flow, etc.
    category VARCHAR(100),
    amount DECIMAL(15, 2) NOT NULL,
    budget_amount DECIMAL(15, 2),
    variance_percentage DECIMAL(5, 2),
    department VARCHAR(100),
    cost_center VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_finance_timestamp (timestamp),
    INDEX idx_finance_type (metric_type)
);

CREATE TABLE cash_flow (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    opening_balance DECIMAL(15, 2) NOT NULL,
    inflows DECIMAL(15, 2) NOT NULL,
    outflows DECIMAL(15, 2) NOT NULL,
    closing_balance DECIMAL(15, 2) NOT NULL,
    forecast_balance DECIMAL(15, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_cashflow_date (date)
);

-- ============================================================================
-- SUPPLY CHAIN DOMAIN
-- ============================================================================

CREATE TABLE inventory_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    product_id VARCHAR(100) NOT NULL,
    product_name VARCHAR(255),
    warehouse_location VARCHAR(100),
    quantity_on_hand INTEGER NOT NULL,
    reorder_point INTEGER,
    lead_time_days INTEGER,
    turnover_rate DECIMAL(5, 2),
    stockout_risk DECIMAL(3, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_inventory_timestamp (timestamp),
    INDEX idx_inventory_product (product_id)
);

CREATE TABLE supplier_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id VARCHAR(100) NOT NULL,
    supplier_name VARCHAR(255),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    on_time_delivery_rate DECIMAL(5, 2),
    quality_score DECIMAL(3, 2),
    average_lead_time_days INTEGER,
    defect_rate DECIMAL(5, 4),
    total_orders INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_supplier_id (supplier_id),
    INDEX idx_supplier_period (period_start, period_end)
);

-- ============================================================================
-- PROCUREMENT DOMAIN
-- ============================================================================

CREATE TABLE procurement_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    purchase_order_id VARCHAR(100) NOT NULL,
    vendor_id VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    amount DECIMAL(15, 2) NOT NULL,
    status VARCHAR(50), -- pending, approved, completed, cancelled
    approval_time_hours INTEGER,
    delivery_time_days INTEGER,
    cost_savings DECIMAL(10, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_procurement_timestamp (timestamp),
    INDEX idx_procurement_vendor (vendor_id)
);

CREATE TABLE vendor_contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id VARCHAR(100) NOT NULL,
    vendor_name VARCHAR(255),
    contract_start_date DATE NOT NULL,
    contract_end_date DATE NOT NULL,
    contract_value DECIMAL(15, 2),
    payment_terms VARCHAR(100),
    compliance_status VARCHAR(50),
    renewal_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_vendor_contract (vendor_id),
    INDEX idx_contract_dates (contract_start_date, contract_end_date)
);

-- ============================================================================
-- HR DOMAIN
-- ============================================================================

CREATE TABLE hr_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    department VARCHAR(100),
    headcount INTEGER,
    turnover_rate DECIMAL(5, 2),
    average_tenure_months INTEGER,
    engagement_score DECIMAL(3, 2),
    performance_score DECIMAL(3, 2),
    recruitment_time_days INTEGER,
    training_hours DECIMAL(8, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_hr_timestamp (timestamp),
    INDEX idx_hr_department (department)
);

CREATE TABLE employee_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL, -- hire, termination, promotion, transfer
    event_date DATE NOT NULL,
    department VARCHAR(100),
    position VARCHAR(100),
    reason VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_employee_id (employee_id),
    INDEX idx_event_date (event_date)
);

-- ============================================================================
-- ENTERPRISE RISK DOMAIN
-- ============================================================================

CREATE TABLE risk_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    risk_category VARCHAR(100) NOT NULL, -- operational, financial, compliance, security
    risk_level VARCHAR(20), -- low, medium, high, critical
    risk_score DECIMAL(5, 2),
    impact_score DECIMAL(5, 2),
    likelihood_score DECIMAL(5, 2),
    mitigation_status VARCHAR(50),
    owner VARCHAR(100),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_risk_timestamp (timestamp),
    INDEX idx_risk_category (risk_category),
    INDEX idx_risk_level (risk_level)
);

CREATE TABLE compliance_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_date DATE NOT NULL,
    regulation VARCHAR(100) NOT NULL,
    compliance_status VARCHAR(50), -- compliant, non_compliant, pending
    severity VARCHAR(20),
    department VARCHAR(100),
    description TEXT,
    remediation_plan TEXT,
    due_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_compliance_date (event_date),
    INDEX idx_compliance_status (compliance_status)
);

-- ============================================================================
-- ANOMALY DETECTION & ANALYSIS
-- ============================================================================

CREATE TABLE anomalies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    domain VARCHAR(50) NOT NULL, -- sales, finance, supply_chain, etc.
    anomaly_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL, -- low, medium, high, critical
    confidence_score DECIMAL(3, 2),
    metric_name VARCHAR(100),
    expected_value DECIMAL(15, 2),
    actual_value DECIMAL(15, 2),
    deviation_percentage DECIMAL(5, 2),
    description TEXT,
    status VARCHAR(50) DEFAULT 'open', -- open, investigating, resolved, false_positive
    assigned_to VARCHAR(100),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_anomaly_detected (detected_at),
    INDEX idx_anomaly_domain (domain),
    INDEX idx_anomaly_severity (severity),
    INDEX idx_anomaly_status (status)
);

CREATE TABLE root_cause_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    anomaly_id UUID REFERENCES anomalies(id),
    analysis_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    root_cause TEXT NOT NULL,
    contributing_factors JSONB,
    confidence_score DECIMAL(3, 2),
    evidence JSONB,
    impact_assessment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_rca_anomaly (anomaly_id),
    INDEX idx_rca_timestamp (analysis_timestamp)
);

-- ============================================================================
-- SIMULATIONS & PREDICTIONS
-- ============================================================================

CREATE TABLE simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_type VARCHAR(100) NOT NULL, -- monte_carlo, scenario, forecast
    domain VARCHAR(50) NOT NULL,
    parameters JSONB NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed
    results JSONB,
    confidence_interval JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    INDEX idx_simulation_type (simulation_type),
    INDEX idx_simulation_domain (domain),
    INDEX idx_simulation_status (status)
);

CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_id UUID REFERENCES simulations(id),
    prediction_date DATE NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    predicted_value DECIMAL(15, 2) NOT NULL,
    lower_bound DECIMAL(15, 2),
    upper_bound DECIMAL(15, 2),
    confidence_level DECIMAL(3, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_prediction_simulation (simulation_id),
    INDEX idx_prediction_date (prediction_date)
);

-- ============================================================================
-- RECOMMENDATIONS
-- ============================================================================

CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    anomaly_id UUID REFERENCES anomalies(id),
    priority VARCHAR(20) NOT NULL, -- low, medium, high, critical
    category VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    rationale TEXT,
    expected_impact TEXT,
    implementation_effort VARCHAR(50), -- low, medium, high
    estimated_cost DECIMAL(15, 2),
    estimated_benefit DECIMAL(15, 2),
    roi_estimate DECIMAL(5, 2),
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected, implemented
    approved_by VARCHAR(100),
    approved_at TIMESTAMPTZ,
    implemented_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_recommendation_generated (generated_at),
    INDEX idx_recommendation_priority (priority),
    INDEX idx_recommendation_status (status)
);

-- ============================================================================
-- AGENT ACTIVITY & AUDIT
-- ============================================================================

CREATE TABLE agent_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name VARCHAR(100) NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration_ms INTEGER,
    status VARCHAR(50), -- success, failure, timeout
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_agent_activity_timestamp (timestamp),
    INDEX idx_agent_activity_name (agent_name)
);

CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id VARCHAR(100),
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_audit_timestamp (timestamp),
    INDEX idx_audit_user (user_id),
    INDEX idx_audit_action (action)
);

-- ============================================================================
-- SYSTEM CONFIGURATION
-- ============================================================================

CREATE TABLE system_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    updated_by VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_config_key (config_key)
);

-- ============================================================================
-- VIEWS FOR ANALYTICS
-- ============================================================================

-- Consolidated metrics view
CREATE VIEW consolidated_metrics AS
SELECT 
    'sales' as domain,
    timestamp,
    revenue as value,
    'revenue' as metric_type
FROM sales_metrics
UNION ALL
SELECT 
    'finance' as domain,
    timestamp,
    amount as value,
    metric_type
FROM finance_metrics
UNION ALL
SELECT 
    'inventory' as domain,
    timestamp,
    quantity_on_hand as value,
    'inventory_level' as metric_type
FROM inventory_metrics;

-- Active anomalies summary
CREATE VIEW active_anomalies_summary AS
SELECT 
    domain,
    severity,
    COUNT(*) as count,
    AVG(confidence_score) as avg_confidence
FROM anomalies
WHERE status = 'open'
GROUP BY domain, severity;

-- Recommendation pipeline
CREATE VIEW recommendation_pipeline AS
SELECT 
    r.id,
    r.title,
    r.priority,
    r.status,
    r.estimated_benefit,
    r.estimated_cost,
    r.roi_estimate,
    a.domain,
    a.severity as anomaly_severity
FROM recommendations r
LEFT JOIN anomalies a ON r.anomaly_id = a.id
WHERE r.status IN ('pending', 'approved')
ORDER BY r.priority DESC, r.roi_estimate DESC;
```

## 2. ChromaDB Schema (Vector Memory)

### 2.1 Collections Structure

```python
# Collection: agent_memory
# Purpose: Store agent experiences and learnings
{
    "collection_name": "agent_memory",
    "metadata": {
        "description": "Long-term memory for all agents",
        "embedding_model": "text-embedding-ada-002"
    },
    "documents": [
        {
            "id": "uuid",
            "content": "Agent observation or insight",
            "metadata": {
                "agent_name": "sales_agent",
                "timestamp": "2026-06-17T10:00:00Z",
                "domain": "sales",
                "context_type": "anomaly_detection",
                "relevance_score": 0.95,
                "tags": ["revenue_drop", "q2_2026"]
            }
        }
    ]
}

# Collection: anomaly_context
# Purpose: Store anomaly patterns and historical context
{
    "collection_name": "anomaly_context",
    "metadata": {
        "description": "Historical anomaly patterns and resolutions",
        "embedding_model": "text-embedding-ada-002"
    },
    "documents": [
        {
            "id": "uuid",
            "content": "Anomaly description and resolution",
            "metadata": {
                "anomaly_type": "revenue_drop",
                "domain": "sales",
                "severity": "high",
                "resolution_status": "resolved",
                "root_cause": "seasonal_trend",
                "timestamp": "2026-06-17T10:00:00Z"
            }
        }
    ]
}

# Collection: business_knowledge
# Purpose: Store business rules, policies, and domain knowledge
{
    "collection_name": "business_knowledge",
    "metadata": {
        "description": "Business rules and domain expertise",
        "embedding_model": "text-embedding-ada-002"
    },
    "documents": [
        {
            "id": "uuid",
            "content": "Business rule or policy description",
            "metadata": {
                "domain": "finance",
                "category": "policy",
                "effective_date": "2026-01-01",
                "source": "CFO_directive",
                "priority": "high"
            }
        }
    ]
}

# Collection: recommendation_history
# Purpose: Store past recommendations and their outcomes
{
    "collection_name": "recommendation_history",
    "metadata": {
        "description": "Historical recommendations and effectiveness",
        "embedding_model": "text-embedding-ada-002"
    },
    "documents": [
        {
            "id": "uuid",
            "content": "Recommendation and outcome description",
            "metadata": {
                "recommendation_id": "uuid",
                "domain": "supply_chain",
                "implemented": true,
                "effectiveness_score": 0.85,
                "actual_impact": "15% cost reduction",
                "timestamp": "2026-06-17T10:00:00Z"
            }
        }
    ]
}

# Collection: cross_domain_insights
# Purpose: Store insights that span multiple domains
{
    "collection_name": "cross_domain_insights",
    "metadata": {
        "description": "Multi-domain correlations and insights",
        "embedding_model": "text-embedding-ada-002"
    },
    "documents": [
        {
            "id": "uuid",
            "content": "Cross-domain insight description",
            "metadata": {
                "domains": ["sales", "finance", "supply_chain"],
                "insight_type": "correlation",
                "confidence": 0.92,
                "timestamp": "2026-06-17T10:00:00Z"
            }
        }
    ]
}
```

## 3. Redis Schema (Cache & State)

### 3.1 Key Patterns

```python
# Agent State
"agent:state:{agent_name}" -> JSON
{
    "status": "active",
    "last_execution": "2026-06-17T10:00:00Z",
    "current_task": "anomaly_detection",
    "metrics_processed": 1500
}

# Real-time Metrics Cache
"metrics:latest:{domain}:{metric_type}" -> JSON
{
    "value": 125000.50,
    "timestamp": "2026-06-17T10:00:00Z",
    "change_percentage": 5.2
}

# Active Anomalies
"anomalies:active:{domain}" -> SET of anomaly_ids
"anomaly:details:{anomaly_id}" -> JSON

# Session Management
"session:{session_id}" -> JSON
{
    "user_id": "user123",
    "created_at": "2026-06-17T10:00:00Z",
    "expires_at": "2026-06-17T18:00:00Z",
    "permissions": ["read", "write"]
}

# Rate Limiting
"ratelimit:{user_id}:{endpoint}" -> Counter with TTL

# WebSocket Connections
"ws:connections" -> SET of connection_ids
"ws:subscriptions:{connection_id}" -> SET of topics

# Task Queue
"queue:tasks:{priority}" -> LIST of task_ids
"task:{task_id}" -> JSON

# Cache for expensive queries
"cache:query:{query_hash}" -> JSON with TTL
```

## 4. Data Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                    RELATIONSHIP DIAGRAM                      │
└─────────────────────────────────────────────────────────────┘

Anomalies (1) ──────────── (1) Root Cause Analysis
    │
    │ (1:N)
    │
    └──────────────────────── (N) Recommendations
                                    │
                                    │ (N:1)
                                    │
                                    └──── Simulations

Agent Activity (N) ────────── (1) Anomalies
                                    │
                                    │
                                    └──── (N:1) Domain Metrics
                                          (sales, finance, etc.)

ChromaDB Collections ←──────────→ PostgreSQL Tables
(Semantic Search)                  (Structured Queries)
        │                                  │
        └──────────── Redis Cache ─────────┘
                    (Fast Access)
```

## 5. Indexing Strategy

### 5.1 PostgreSQL Indexes
- Time-series indexes on all timestamp columns
- Composite indexes for common query patterns
- Partial indexes for active records
- GiST indexes for JSONB columns

### 5.2 ChromaDB Indexes
- HNSW (Hierarchical Navigable Small World) for vector similarity
- Automatic indexing on metadata fields

### 5.3 Redis Indexes
- Hash indexes for key-value lookups
- Sorted sets for time-based queries

## 6. Data Retention Policy

```python
RETENTION_POLICIES = {
    "real_time_metrics": "7 days",      # Redis
    "detailed_metrics": "90 days",      # PostgreSQL
    "aggregated_metrics": "2 years",    # PostgreSQL
    "anomalies": "1 year",              # PostgreSQL
    "agent_memory": "indefinite",       # ChromaDB
    "audit_logs": "7 years",            # PostgreSQL (compliance)
    "cache": "1 hour - 24 hours"        # Redis (TTL-based)
}
```

## 7. Backup & Recovery

- **PostgreSQL**: Daily full backups, hourly incremental
- **ChromaDB**: Weekly full backups, daily incremental
- **Redis**: RDB snapshots every 6 hours, AOF for durability
- **Recovery Time Objective (RTO)**: < 1 hour
- **Recovery Point Objective (RPO)**: < 15 minutes