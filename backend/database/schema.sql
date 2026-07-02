-- ============================================================================
-- Enterprise Digital COO - PostgreSQL Database Schema
-- Version: 1.0
-- Author: Senior Database Architect
-- Date: 2026-06-17
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

-- ============================================================================
-- SALES DOMAIN
-- ============================================================================

CREATE TABLE sales_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL,
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('daily', 'weekly', 'monthly', 'quarterly')),
    
    -- Revenue Metrics
    total_revenue DECIMAL(15, 2) NOT NULL,
    revenue_by_region JSONB,
    revenue_by_product JSONB,
    revenue_growth_rate DECIMAL(5, 2),
    
    -- Pipeline Metrics
    pipeline_value DECIMAL(15, 2),
    weighted_pipeline_value DECIMAL(15, 2),
    average_deal_size DECIMAL(10, 2),
    pipeline_velocity DECIMAL(8, 2),
    
    -- Conversion Metrics
    leads_count INTEGER,
    opportunities_count INTEGER,
    closed_won_count INTEGER,
    conversion_rate DECIMAL(5, 4),
    
    -- Customer Metrics
    new_customers INTEGER,
    churned_customers INTEGER,
    customer_acquisition_cost DECIMAL(10, 2),
    customer_lifetime_value DECIMAL(10, 2),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT sales_metrics_timestamp_period_key UNIQUE (timestamp, period_type)
);

CREATE INDEX idx_sales_metrics_timestamp ON sales_metrics(timestamp DESC);
CREATE INDEX idx_sales_metrics_period ON sales_metrics(period_type, timestamp DESC);
CREATE INDEX idx_sales_metrics_revenue ON sales_metrics(total_revenue DESC);
CREATE INDEX idx_sales_metrics_jsonb_region ON sales_metrics USING GIN (revenue_by_region);

-- ============================================================================
-- FINANCIAL DOMAIN
-- ============================================================================

CREATE TABLE financial_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL,
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('daily', 'weekly', 'monthly', 'quarterly', 'annual')),
    
    -- P&L Metrics
    revenue DECIMAL(15, 2) NOT NULL,
    cost_of_goods_sold DECIMAL(15, 2),
    gross_profit DECIMAL(15, 2),
    operating_expenses DECIMAL(15, 2),
    ebitda DECIMAL(15, 2),
    net_income DECIMAL(15, 2),
    
    -- Cash Flow Metrics
    opening_cash_balance DECIMAL(15, 2),
    cash_inflows DECIMAL(15, 2),
    cash_outflows DECIMAL(15, 2),
    closing_cash_balance DECIMAL(15, 2),
    burn_rate DECIMAL(12, 2),
    runway_days INTEGER,
    
    -- Balance Sheet Metrics
    total_assets DECIMAL(15, 2),
    total_liabilities DECIMAL(15, 2),
    shareholders_equity DECIMAL(15, 2),
    
    -- Financial Ratios
    current_ratio DECIMAL(5, 2),
    quick_ratio DECIMAL(5, 2),
    debt_to_equity DECIMAL(5, 2),
    return_on_equity DECIMAL(5, 4),
    return_on_assets DECIMAL(5, 4),
    
    -- Budget Metrics
    budget_variance DECIMAL(15, 2),
    budget_variance_percentage DECIMAL(5, 2),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT financial_metrics_timestamp_period_key UNIQUE (timestamp, period_type)
);

CREATE INDEX idx_financial_metrics_timestamp ON financial_metrics(timestamp DESC);
CREATE INDEX idx_financial_metrics_period ON financial_metrics(period_type, timestamp DESC);
CREATE INDEX idx_financial_metrics_cash ON financial_metrics(closing_cash_balance DESC);
CREATE INDEX idx_financial_metrics_runway ON financial_metrics(runway_days) WHERE runway_days < 90;

-- ============================================================================
-- INVENTORY & SUPPLY CHAIN DOMAIN
-- ============================================================================

CREATE TABLE inventory_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL,
    product_id VARCHAR(100) NOT NULL,
    product_name VARCHAR(255),
    product_category VARCHAR(100),
    
    -- Inventory Levels
    quantity_on_hand INTEGER NOT NULL,
    quantity_reserved INTEGER DEFAULT 0,
    quantity_available INTEGER GENERATED ALWAYS AS (quantity_on_hand - quantity_reserved) STORED,
    reorder_point INTEGER,
    safety_stock INTEGER,
    
    -- Warehouse Info
    warehouse_location VARCHAR(100),
    warehouse_zone VARCHAR(50),
    
    -- Performance Metrics
    inventory_turnover DECIMAL(5, 2),
    days_of_inventory DECIMAL(5, 1),
    stockout_risk_score DECIMAL(3, 2),
    
    -- Supplier Info
    primary_supplier_id VARCHAR(100),
    lead_time_days INTEGER,
    
    -- Financial
    unit_cost DECIMAL(10, 2),
    total_value DECIMAL(15, 2) GENERATED ALWAYS AS (quantity_on_hand * unit_cost) STORED,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT inventory_metrics_timestamp_product_key UNIQUE (timestamp, product_id)
);

CREATE INDEX idx_inventory_metrics_timestamp ON inventory_metrics(timestamp DESC);
CREATE INDEX idx_inventory_metrics_product ON inventory_metrics(product_id, timestamp DESC);
CREATE INDEX idx_inventory_metrics_stockout ON inventory_metrics(stockout_risk_score DESC) WHERE stockout_risk_score > 0.7;
CREATE INDEX idx_inventory_metrics_category ON inventory_metrics(product_category, timestamp DESC);
CREATE INDEX idx_inventory_metrics_available ON inventory_metrics(quantity_available) WHERE quantity_available < reorder_point;

-- ============================================================================
-- HR DOMAIN
-- ============================================================================

CREATE TABLE hr_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL,
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('weekly', 'monthly', 'quarterly')),
    department VARCHAR(100),
    
    -- Headcount Metrics
    total_headcount INTEGER NOT NULL,
    new_hires INTEGER DEFAULT 0,
    terminations INTEGER DEFAULT 0,
    voluntary_terminations INTEGER DEFAULT 0,
    involuntary_terminations INTEGER DEFAULT 0,
    
    -- Turnover Metrics
    turnover_rate DECIMAL(5, 2),
    voluntary_turnover_rate DECIMAL(5, 2),
    average_tenure_months DECIMAL(5, 1),
    
    -- Engagement Metrics
    engagement_score DECIMAL(3, 2),
    engagement_survey_response_rate DECIMAL(5, 2),
    
    -- Performance Metrics
    average_performance_score DECIMAL(3, 2),
    high_performers_count INTEGER,
    low_performers_count INTEGER,
    
    -- Recruitment Metrics
    open_positions INTEGER,
    time_to_fill_days DECIMAL(5, 1),
    cost_per_hire DECIMAL(10, 2),
    quality_of_hire_score DECIMAL(3, 2),
    
    -- Compensation Metrics
    average_salary DECIMAL(10, 2),
    salary_vs_market_percentage DECIMAL(5, 2),
    total_compensation_cost DECIMAL(15, 2),
    
    -- Training Metrics
    training_hours_per_employee DECIMAL(5, 1),
    training_completion_rate DECIMAL(5, 2),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT hr_metrics_timestamp_period_dept_key UNIQUE (timestamp, period_type, department)
);

CREATE INDEX idx_hr_metrics_timestamp ON hr_metrics(timestamp DESC);
CREATE INDEX idx_hr_metrics_department ON hr_metrics(department, timestamp DESC);
CREATE INDEX idx_hr_metrics_turnover ON hr_metrics(turnover_rate DESC) WHERE turnover_rate > 15.0;
CREATE INDEX idx_hr_metrics_engagement ON hr_metrics(engagement_score) WHERE engagement_score < 70.0;

-- ============================================================================
-- RISK DOMAIN
-- ============================================================================

CREATE TABLE risk_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL,
    risk_category VARCHAR(100) NOT NULL CHECK (risk_category IN 
        ('operational', 'financial', 'strategic', 'compliance', 'reputational', 'technology', 'market')),
    risk_subcategory VARCHAR(100),
    
    -- Risk Assessment
    risk_name VARCHAR(255) NOT NULL,
    risk_description TEXT,
    likelihood INTEGER CHECK (likelihood BETWEEN 1 AND 5),
    impact INTEGER CHECK (impact BETWEEN 1 AND 5),
    risk_score INTEGER GENERATED ALWAYS AS (likelihood * impact) STORED,
    velocity VARCHAR(20) CHECK (velocity IN ('slow', 'moderate', 'fast', 'immediate')),
    
    -- Risk Status
    risk_level VARCHAR(20) CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    status VARCHAR(50) CHECK (status IN ('identified', 'assessing', 'mitigating', 'monitoring', 'closed')),
    
    -- Financial Impact
    financial_exposure_min DECIMAL(15, 2),
    financial_exposure_max DECIMAL(15, 2),
    financial_exposure_expected DECIMAL(15, 2),
    
    -- Control Assessment
    control_effectiveness_score DECIMAL(3, 2),
    residual_risk_score INTEGER,
    
    -- Ownership
    risk_owner VARCHAR(100),
    department VARCHAR(100),
    
    -- Compliance
    regulatory_requirement VARCHAR(255),
    compliance_status VARCHAR(50),
    
    -- Metadata
    identified_date DATE,
    last_review_date DATE,
    next_review_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_risk_metrics_timestamp ON risk_metrics(timestamp DESC);
CREATE INDEX idx_risk_metrics_category ON risk_metrics(risk_category, timestamp DESC);
CREATE INDEX idx_risk_metrics_score ON risk_metrics(risk_score DESC);
CREATE INDEX idx_risk_metrics_level ON risk_metrics(risk_level, status);
CREATE INDEX idx_risk_metrics_owner ON risk_metrics(risk_owner);
CREATE INDEX idx_risk_metrics_review ON risk_metrics(next_review_date) WHERE status != 'closed';

-- ============================================================================
-- AGENT DECISIONS
-- ============================================================================

CREATE TABLE agent_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    decision_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Agent Info
    agent_name VARCHAR(100) NOT NULL,
    agent_type VARCHAR(50) CHECK (agent_type IN 
        ('sales', 'finance', 'supply_chain', 'procurement', 'hr', 'risk', 'executive', 'simulation')),
    
    -- Decision Context
    trigger_event VARCHAR(255),
    anomaly_id UUID,
    workflow_id VARCHAR(100),
    
    -- Decision Details
    decision_type VARCHAR(100) NOT NULL,
    decision_description TEXT NOT NULL,
    decision_rationale TEXT,
    
    -- Analysis Data
    input_data JSONB,
    analysis_results JSONB,
    confidence_score DECIMAL(3, 2),
    
    -- Decision Outcome
    recommended_action TEXT,
    expected_impact JSONB,
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    
    -- Execution
    status VARCHAR(50) CHECK (status IN ('pending', 'approved', 'rejected', 'executed', 'completed')) DEFAULT 'pending',
    approved_by VARCHAR(100),
    approved_at TIMESTAMPTZ,
    executed_at TIMESTAMPTZ,
    
    -- Results
    actual_outcome JSONB,
    effectiveness_score DECIMAL(3, 2),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_decisions_timestamp ON agent_decisions(decision_timestamp DESC);
CREATE INDEX idx_agent_decisions_agent ON agent_decisions(agent_name, decision_timestamp DESC);
CREATE INDEX idx_agent_decisions_type ON agent_decisions(agent_type, decision_timestamp DESC);
CREATE INDEX idx_agent_decisions_status ON agent_decisions(status, priority);
CREATE INDEX idx_agent_decisions_workflow ON agent_decisions(workflow_id);
CREATE INDEX idx_agent_decisions_anomaly ON agent_decisions(anomaly_id) WHERE anomaly_id IS NOT NULL;
CREATE INDEX idx_agent_decisions_jsonb_input ON agent_decisions USING GIN (input_data);
CREATE INDEX idx_agent_decisions_jsonb_results ON agent_decisions USING GIN (analysis_results);

-- ============================================================================
-- EXECUTIVE RECOMMENDATIONS
-- ============================================================================

CREATE TABLE executive_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recommendation_id VARCHAR(50) UNIQUE NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Source
    source_analysis_id UUID,
    source_workflow_id VARCHAR(100),
    generated_by_agent VARCHAR(100),
    
    -- Recommendation Details
    priority INTEGER CHECK (priority BETWEEN 1 AND 10),
    category VARCHAR(50) CHECK (category IN ('immediate', 'short_term', 'medium_term', 'long_term')),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    rationale TEXT NOT NULL,
    
    -- Impact Assessment
    expected_impact JSONB NOT NULL,
    financial_impact DECIMAL(15, 2),
    estimated_roi DECIMAL(8, 2),
    confidence_level DECIMAL(3, 2),
    
    -- Implementation
    implementation_effort VARCHAR(20) CHECK (implementation_effort IN ('low', 'medium', 'high')),
    timeline VARCHAR(100),
    resource_requirements JSONB,
    dependencies TEXT[],
    
    -- Success Metrics
    success_metrics JSONB,
    kpis TEXT[],
    
    -- Risk Assessment
    risks JSONB,
    mitigation_strategies JSONB,
    
    -- Ownership
    recommended_owner VARCHAR(100),
    assigned_to VARCHAR(100),
    
    -- Status Tracking
    status VARCHAR(50) CHECK (status IN 
        ('pending', 'under_review', 'approved', 'rejected', 'in_progress', 'completed', 'cancelled')) DEFAULT 'pending',
    approved_by VARCHAR(100),
    approved_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Outcome Tracking
    actual_impact JSONB,
    actual_roi DECIMAL(8, 2),
    lessons_learned TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_exec_recommendations_generated ON executive_recommendations(generated_at DESC);
CREATE INDEX idx_exec_recommendations_priority ON executive_recommendations(priority, status);
CREATE INDEX idx_exec_recommendations_category ON executive_recommendations(category, status);
CREATE INDEX idx_exec_recommendations_status ON executive_recommendations(status, priority);
CREATE INDEX idx_exec_recommendations_owner ON executive_recommendations(assigned_to) WHERE status IN ('approved', 'in_progress');
CREATE INDEX idx_exec_recommendations_roi ON executive_recommendations(estimated_roi DESC) WHERE status = 'pending';
CREATE INDEX idx_exec_recommendations_workflow ON executive_recommendations(source_workflow_id);
CREATE INDEX idx_exec_recommendations_jsonb_impact ON executive_recommendations USING GIN (expected_impact);

-- ============================================================================
-- SIMULATION RESULTS
-- ============================================================================

CREATE TABLE simulation_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_id VARCHAR(100) UNIQUE NOT NULL,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Simulation Configuration
    simulation_type VARCHAR(50) CHECK (simulation_type IN ('monte_carlo', 'scenario', 'forecast', 'sensitivity')),
    scenario_name VARCHAR(255) NOT NULL,
    time_horizon_days INTEGER NOT NULL,
    iterations INTEGER,
    
    -- Input Parameters
    input_parameters JSONB NOT NULL,
    assumptions JSONB,
    variables JSONB,
    
    -- Scenario Outcomes
    best_case_outcome JSONB,
    most_likely_outcome JSONB,
    worst_case_outcome JSONB,
    
    -- Statistical Results
    mean_outcome DECIMAL(15, 2),
    median_outcome DECIMAL(15, 2),
    std_deviation DECIMAL(15, 2),
    confidence_interval_80 JSONB,
    confidence_interval_95 JSONB,
    
    -- Forecasts
    revenue_forecast DECIMAL(15, 2),
    cost_forecast DECIMAL(15, 2),
    profit_forecast DECIMAL(15, 2),
    
    -- Risk Assessment
    probability_of_success DECIMAL(5, 4),
    probability_of_failure DECIMAL(5, 4),
    value_at_risk_95 DECIMAL(15, 2),
    maximum_potential_loss DECIMAL(15, 2),
    maximum_potential_gain DECIMAL(15, 2),
    
    -- Sensitivity Analysis
    sensitivity_analysis JSONB,
    key_drivers TEXT[],
    critical_thresholds JSONB,
    
    -- Recommendations
    recommended_actions TEXT[],
    monitoring_metrics TEXT[],
    early_warning_indicators TEXT[],
    
    -- Quality Metrics
    confidence_in_simulation DECIMAL(3, 2),
    data_quality_score DECIMAL(3, 2),
    model_accuracy_score DECIMAL(3, 2),
    
    -- Execution Info
    execution_time_seconds DECIMAL(8, 2),
    status VARCHAR(50) CHECK (status IN ('pending', 'running', 'completed', 'failed')) DEFAULT 'completed',
    error_message TEXT,
    
    -- Metadata
    created_by VARCHAR(100),
    workflow_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_simulation_results_executed ON simulation_results(executed_at DESC);
CREATE INDEX idx_simulation_results_type ON simulation_results(simulation_type, executed_at DESC);
CREATE INDEX idx_simulation_results_status ON simulation_results(status);
CREATE INDEX idx_simulation_results_workflow ON simulation_results(workflow_id);
CREATE INDEX idx_simulation_results_confidence ON simulation_results(confidence_in_simulation DESC);
CREATE INDEX idx_simulation_results_jsonb_params ON simulation_results USING GIN (input_parameters);
CREATE INDEX idx_simulation_results_jsonb_outcomes ON simulation_results USING GIN (best_case_outcome, most_likely_outcome, worst_case_outcome);

-- ============================================================================
-- ANOMALIES (Cross-Domain)
-- ============================================================================

CREATE TABLE anomalies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Anomaly Classification
    domain VARCHAR(50) NOT NULL CHECK (domain IN 
        ('sales', 'finance', 'supply_chain', 'procurement', 'hr', 'risk', 'cross_domain')),
    anomaly_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    
    -- Anomaly Details
    description TEXT NOT NULL,
    metric_name VARCHAR(100),
    expected_value DECIMAL(15, 2),
    actual_value DECIMAL(15, 2),
    deviation_percentage DECIMAL(5, 2),
    
    -- Detection Info
    detection_method VARCHAR(100),
    confidence_score DECIMAL(3, 2),
    false_positive_probability DECIMAL(3, 2),
    
    -- Impact Assessment
    business_impact TEXT,
    financial_impact DECIMAL(15, 2),
    affected_entities TEXT[],
    
    -- Status Tracking
    status VARCHAR(50) CHECK (status IN 
        ('open', 'investigating', 'root_cause_identified', 'mitigating', 'resolved', 'false_positive')) DEFAULT 'open',
    assigned_to VARCHAR(100),
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    
    -- Resolution
    root_cause_id UUID,
    resolution_description TEXT,
    resolved_at TIMESTAMPTZ,
    resolution_time_hours DECIMAL(8, 2),
    
    -- Related Data
    related_anomalies UUID[],
    related_decisions UUID[],
    related_recommendations UUID[],
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_anomalies_detected ON anomalies(detected_at DESC);
CREATE INDEX idx_anomalies_domain ON anomalies(domain, detected_at DESC);
CREATE INDEX idx_anomalies_severity ON anomalies(severity, status);
CREATE INDEX idx_anomalies_status ON anomalies(status, priority);
CREATE INDEX idx_anomalies_assigned ON anomalies(assigned_to) WHERE status IN ('open', 'investigating');
CREATE INDEX idx_anomalies_unresolved ON anomalies(detected_at DESC) WHERE status NOT IN ('resolved', 'false_positive');

-- ============================================================================
-- WORKFLOWS (Orchestration Tracking)
-- ============================================================================

CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id VARCHAR(100) UNIQUE NOT NULL,
    workflow_type VARCHAR(100) NOT NULL,
    
    -- Trigger Info
    trigger_event VARCHAR(255),
    trigger_data JSONB,
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Execution Info
    status VARCHAR(50) CHECK (status IN 
        ('pending', 'running', 'awaiting_approval', 'approved', 'completed', 'failed', 'cancelled')) DEFAULT 'pending',
    current_step VARCHAR(100),
    steps_completed TEXT[],
    
    -- Timing
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    total_execution_time_seconds DECIMAL(8, 2),
    
    -- Results
    final_state JSONB,
    executive_summary TEXT,
    confidence_score DECIMAL(3, 2),
    
    -- Approval
    requires_approval BOOLEAN DEFAULT FALSE,
    approved_by VARCHAR(100),
    approved_at TIMESTAMPTZ,
    approval_notes TEXT,
    
    -- Error Handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_workflows_triggered ON workflows(triggered_at DESC);
CREATE INDEX idx_workflows_type ON workflows(workflow_type, triggered_at DESC);
CREATE INDEX idx_workflows_status ON workflows(status, triggered_at DESC);
CREATE INDEX idx_workflows_approval ON workflows(requires_approval, status) WHERE requires_approval = TRUE;
CREATE INDEX idx_workflows_jsonb_state ON workflows USING GIN (final_state);

-- ============================================================================
-- FOREIGN KEY RELATIONSHIPS
-- ============================================================================

ALTER TABLE agent_decisions
    ADD CONSTRAINT fk_agent_decisions_anomaly 
    FOREIGN KEY (anomaly_id) REFERENCES anomalies(id) ON DELETE SET NULL;

ALTER TABLE executive_recommendations
    ADD CONSTRAINT fk_exec_recommendations_workflow 
    FOREIGN KEY (source_workflow_id) REFERENCES workflows(workflow_id) ON DELETE SET NULL;

ALTER TABLE simulation_results
    ADD CONSTRAINT fk_simulation_results_workflow 
    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON DELETE SET NULL;

-- ============================================================================
-- VIEWS FOR ANALYTICS
-- ============================================================================

CREATE VIEW v_active_anomalies AS
SELECT 
    a.id,
    a.domain,
    a.anomaly_type,
    a.severity,
    a.description,
    a.detected_at,
    a.status,
    a.assigned_to,
    a.financial_impact,
    EXTRACT(EPOCH FROM (NOW() - a.detected_at))/3600 AS hours_open
FROM anomalies a
WHERE a.status NOT IN ('resolved', 'false_positive')
ORDER BY a.severity DESC, a.detected_at DESC;

CREATE VIEW v_pending_recommendations AS
SELECT 
    r.id,
    r.recommendation_id,
    r.priority,
    r.title,
    r.category,
    r.estimated_roi,
    r.financial_impact,
    r.status,
    r.generated_at,
    EXTRACT(EPOCH FROM (NOW() - r.generated_at))/86400 AS days_pending
FROM executive_recommendations r
WHERE r.status IN ('pending', 'under_review')
ORDER BY r.priority ASC, r.estimated_roi DESC;

CREATE VIEW v_workflow_summary AS
SELECT 
    w.workflow_type,
    w.status,
    COUNT(*) AS count,
    AVG(w.total_execution_time_seconds) AS avg_execution_time,
    AVG(w.confidence_score) AS avg_confidence
FROM workflows w
WHERE w.triggered_at > NOW() - INTERVAL '30 days'
GROUP BY w.workflow_type, w.status;

-- ============================================================================
-- FUNCTIONS FOR COMMON OPERATIONS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to all tables
CREATE TRIGGER update_sales_metrics_updated_at BEFORE UPDATE ON sales_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_financial_metrics_updated_at BEFORE UPDATE ON financial_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inventory_metrics_updated_at BEFORE UPDATE ON inventory_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hr_metrics_updated_at BEFORE UPDATE ON hr_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_risk_metrics_updated_at BEFORE UPDATE ON risk_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_decisions_updated_at BEFORE UPDATE ON agent_decisions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exec_recommendations_updated_at BEFORE UPDATE ON executive_recommendations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_simulation_results_updated_at BEFORE UPDATE ON simulation_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_anomalies_updated_at BEFORE UPDATE ON anomalies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- PARTITIONING STRATEGY (for large tables)
-- ============================================================================

-- Example: Partition sales_metrics by month
-- CREATE TABLE sales_metrics_2026_06 PARTITION OF sales_metrics
--     FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');

-- ============================================================================
-- GRANTS (adjust based on your security model)
-- ============================================================================

-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO coo_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO coo_app_user;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

-- Made with Codex
