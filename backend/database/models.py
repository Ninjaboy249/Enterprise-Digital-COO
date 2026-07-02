"""
SQLAlchemy ORM Models
Defines database models matching the PostgreSQL schema
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Index,
    CheckConstraint,
    Computed,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from .session import Base


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class SalesMetrics(Base, TimestampMixin):
    """Sales performance metrics"""
    __tablename__ = "sales_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, index=True)
    total_revenue = Column(Float, nullable=False)
    pipeline_value = Column(Float, nullable=False)
    conversion_rate = Column(Float, nullable=False)
    average_deal_size = Column(Float)
    sales_cycle_days = Column(Integer)
    win_rate = Column(Float)
    revenue_by_region = Column(JSONB)
    revenue_by_product = Column(JSONB)
    top_deals = Column(JSONB)
    
    __table_args__ = (
        Index('idx_sales_metrics_timestamp', 'timestamp'),
        Index('idx_sales_metrics_revenue', 'total_revenue'),
        Index('idx_sales_metrics_jsonb_region', 'revenue_by_region', postgresql_using='gin'),
    )


class FinancialMetrics(Base, TimestampMixin):
    """Financial performance and health metrics"""
    __tablename__ = "financial_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, index=True)
    closing_cash_balance = Column(Float, nullable=False)
    burn_rate = Column(Float, nullable=False)
    runway_days = Column(Integer, nullable=False)
    accounts_receivable = Column(Float)
    accounts_payable = Column(Float)
    current_ratio = Column(Float)
    quick_ratio = Column(Float)
    debt_to_equity = Column(Float)
    gross_margin = Column(Float)
    operating_margin = Column(Float)
    cash_flow_by_category = Column(JSONB)
    
    __table_args__ = (
        Index('idx_financial_metrics_timestamp', 'timestamp'),
        Index('idx_financial_metrics_cash', 'closing_cash_balance'),
        Index('idx_financial_metrics_runway', 'runway_days', postgresql_where='runway_days < 90'),
    )


class InventoryMetrics(Base, TimestampMixin):
    """Inventory and supply chain metrics"""
    __tablename__ = "inventory_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, index=True)
    product_id = Column(String(100), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity_on_hand = Column(Integer, nullable=False)
    quantity_reserved = Column(Integer, nullable=False, default=0)
    quantity_available = Column(Integer, Computed('quantity_on_hand - quantity_reserved'))
    reorder_point = Column(Integer, nullable=False)
    lead_time_days = Column(Integer, nullable=False)
    unit_cost = Column(Float, nullable=False)
    total_value = Column(Float, Computed('quantity_on_hand * unit_cost'))
    stockout_risk_score = Column(Float)
    supplier_info = Column(JSONB)
    
    __table_args__ = (
        Index('idx_inventory_metrics_timestamp', 'timestamp'),
        Index('idx_inventory_metrics_product', 'product_id'),
        Index('idx_inventory_metrics_stockout', 'stockout_risk_score', postgresql_where='stockout_risk_score > 0.7'),
        Index('idx_inventory_metrics_available', 'quantity_available', postgresql_where='quantity_available < reorder_point'),
    )


class HRMetrics(Base, TimestampMixin):
    """Human resources and workforce metrics"""
    __tablename__ = "hr_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, index=True)
    department = Column(String(100), nullable=False)
    total_headcount = Column(Integer, nullable=False)
    new_hires = Column(Integer, default=0)
    terminations = Column(Integer, default=0)
    turnover_rate = Column(Float)
    engagement_score = Column(Float)
    average_tenure_months = Column(Float)
    time_to_fill_days = Column(Float)
    cost_per_hire = Column(Float)
    training_hours = Column(Float)
    performance_ratings = Column(JSONB)
    
    __table_args__ = (
        Index('idx_hr_metrics_timestamp', 'timestamp'),
        Index('idx_hr_metrics_department', 'department'),
        Index('idx_hr_metrics_turnover', 'turnover_rate', postgresql_where='turnover_rate > 0.15'),
        Index('idx_hr_metrics_engagement', 'engagement_score', postgresql_where='engagement_score < 70'),
    )


class RiskMetrics(Base, TimestampMixin):
    """Enterprise risk assessment metrics"""
    __tablename__ = "risk_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, index=True)
    risk_id = Column(String(100), nullable=False, unique=True)
    risk_category = Column(String(50), nullable=False)
    risk_description = Column(Text, nullable=False)
    likelihood = Column(Integer, nullable=False)
    impact = Column(Integer, nullable=False)
    risk_score = Column(Integer, Computed('likelihood * impact'))
    status = Column(String(20), nullable=False, default='active')
    owner = Column(String(100))
    mitigation_plan = Column(Text)
    financial_exposure_min = Column(Float)
    financial_exposure_max = Column(Float)
    financial_exposure_expected = Column(Float)
    control_effectiveness_score = Column(Float)
    last_review_date = Column(DateTime)
    next_review_date = Column(DateTime)
    
    __table_args__ = (
        Index('idx_risk_metrics_timestamp', 'timestamp'),
        Index('idx_risk_metrics_category', 'risk_category'),
        Index('idx_risk_metrics_score', 'risk_score'),
        Index('idx_risk_metrics_review', 'next_review_date', postgresql_where="status = 'active'"),
        CheckConstraint('likelihood >= 1 AND likelihood <= 5', name='check_likelihood_range'),
        CheckConstraint('impact >= 1 AND impact <= 5', name='check_impact_range'),
    )


class Anomaly(Base, TimestampMixin):
    """Detected business anomalies"""
    __tablename__ = "anomalies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    anomaly_id = Column(String(100), nullable=False, unique=True)
    domain = Column(String(50), nullable=False)
    metric_name = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expected_value = Column(Float)
    actual_value = Column(Float)
    deviation_percentage = Column(Float)
    confidence_score = Column(Float)
    description = Column(Text)
    context = Column(JSONB)
    status = Column(String(20), nullable=False, default='open')
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Relationships
    agent_decisions = relationship("AgentDecision", back_populates="anomaly")
    
    __table_args__ = (
        Index('idx_anomalies_domain', 'domain'),
        Index('idx_anomalies_detected', 'detected_at'),
        Index('idx_anomalies_unresolved', 'status', 'severity', postgresql_where="status NOT IN ('resolved', 'false_positive')"),
        Index('idx_anomalies_severity', 'severity', 'status'),
    )


class AgentDecision(Base, TimestampMixin):
    """AI agent decisions and analyses"""
    __tablename__ = "agent_decisions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    decision_id = Column(String(100), nullable=False, unique=True)
    agent_name = Column(String(100), nullable=False)
    workflow_id = Column(String(100), nullable=False)
    anomaly_id = Column(UUID(as_uuid=True), ForeignKey('anomalies.id'))
    decision_type = Column(String(50), nullable=False)
    confidence_score = Column(Float, nullable=False)
    reasoning = Column(Text)
    input_data = Column(JSONB)
    analysis_results = Column(JSONB)
    recommendations = Column(JSONB)
    execution_time_ms = Column(Integer)
    
    # Relationships
    anomaly = relationship("Anomaly", back_populates="agent_decisions")
    
    __table_args__ = (
        Index('idx_agent_decisions_agent', 'agent_name'),
        Index('idx_agent_decisions_workflow', 'workflow_id'),
        Index('idx_agent_decisions_created', 'created_at'),
        Index('idx_agent_decisions_jsonb_input', 'input_data', postgresql_using='gin'),
        Index('idx_agent_decisions_jsonb_results', 'analysis_results', postgresql_using='gin'),
    )


class ExecutiveRecommendation(Base, TimestampMixin):
    """Executive-level recommendations"""
    __tablename__ = "executive_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(String(100), nullable=False, unique=True)
    source_workflow_id = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Integer, nullable=False)
    category = Column(String(50), nullable=False)
    estimated_roi = Column(Float)
    implementation_effort = Column(String(20))
    timeline_days = Column(Integer)
    expected_impact = Column(JSONB)
    risks = Column(JSONB)
    dependencies = Column(JSONB)
    status = Column(String(20), nullable=False, default='pending')
    approved_by = Column(String(100))
    approved_at = Column(DateTime)
    implemented_at = Column(DateTime)
    actual_impact = Column(JSONB)
    
    __table_args__ = (
        Index('idx_exec_recommendations_priority', 'priority'),
        Index('idx_exec_recommendations_status', 'status'),
        Index('idx_exec_recommendations_roi', 'estimated_roi'),
        Index('idx_exec_recommendations_created', 'created_at'),
        Index('idx_exec_recommendations_jsonb_impact', 'expected_impact', postgresql_using='gin'),
        CheckConstraint('priority >= 1 AND priority <= 10', name='check_priority_range'),
    )


class SimulationResult(Base, TimestampMixin):
    """Business simulation results"""
    __tablename__ = "simulation_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(String(100), nullable=False, unique=True)
    workflow_id = Column(String(100), nullable=False)
    simulation_type = Column(String(50), nullable=False)
    scenario_name = Column(String(255), nullable=False)
    input_parameters = Column(JSONB, nullable=False)
    iterations = Column(Integer, nullable=False)
    best_case_outcome = Column(JSONB)
    most_likely_outcome = Column(JSONB)
    worst_case_outcome = Column(JSONB)
    confidence_interval_95 = Column(JSONB)
    key_insights = Column(JSONB)
    recommendations = Column(JSONB)
    execution_time_ms = Column(Integer)
    confidence_score = Column(Float)
    
    __table_args__ = (
        Index('idx_simulation_results_workflow', 'workflow_id'),
        Index('idx_simulation_results_type', 'simulation_type'),
        Index('idx_simulation_results_confidence', 'confidence_score'),
        Index('idx_simulation_results_created', 'created_at'),
        Index('idx_simulation_results_jsonb_outcomes', 'most_likely_outcome', postgresql_using='gin'),
    )


class Workflow(Base, TimestampMixin):
    """LangGraph workflow executions"""
    __tablename__ = "workflows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(String(100), nullable=False, unique=True)
    workflow_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default='running')
    trigger_type = Column(String(50), nullable=False)
    trigger_data = Column(JSONB)
    initial_state = Column(JSONB)
    final_state = Column(JSONB)
    execution_path = Column(JSONB)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime)
    execution_time_ms = Column(Integer)
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(String(100))
    approved_at = Column(DateTime)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    __table_args__ = (
        Index('idx_workflows_type', 'workflow_type'),
        Index('idx_workflows_status', 'status'),
        Index('idx_workflows_started', 'started_at'),
        Index('idx_workflows_approval', 'requires_approval', 'status', postgresql_where="requires_approval = true AND status = 'pending_approval'"),
        Index('idx_workflows_jsonb_state', 'final_state', postgresql_using='gin'),
    )


# Export all models
__all__ = [
    "Base",
    "SalesMetrics",
    "FinancialMetrics",
    "InventoryMetrics",
    "HRMetrics",
    "RiskMetrics",
    "Anomaly",
    "AgentDecision",
    "ExecutiveRecommendation",
    "SimulationResult",
    "Workflow",
]

# Made with Codex
