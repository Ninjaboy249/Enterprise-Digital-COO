"""
ChromaDB Memory Usage Examples
Demonstrates how to use the memory system for agent learning and knowledge retrieval
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any

from backend.memory.chromadb_client import get_chromadb_client


# ============================================================================
# Example 1: Store Agent Decision
# ============================================================================

async def example_store_agent_decision():
    """Store an agent decision for future learning"""
    
    client = await get_chromadb_client()
    
    # Prepare decision document
    decision = {
        "id": "decision_001",
        "text": (
            "Sales Agent detected 15% revenue drop in Q2 2026. "
            "Root cause: 3 major deals delayed due to procurement issues. "
            "Recommended immediate escalation to procurement team and executive review. "
            "Action taken: Escalated to COO. "
            "Outcome: Procurement bottleneck resolved in 5 days, deals closed successfully."
        ),
        "metadata": {
            "agent_name": "sales_agent",
            "decision_type": "anomaly_detection",
            "domain": "sales",
            "severity": "high",
            "confidence_score": 0.87,
            "timestamp": datetime.utcnow().isoformat(),
            "workflow_id": "wf_12345",
            "anomaly_id": "anom_67890",
            "outcome": "successful",
            "effectiveness_score": 0.92,
            "tags": ["revenue_drop", "procurement_delay", "escalation", "successful"],
        }
    }
    
    # Store in memory
    await client.add(
        collection="agent_decisions",
        documents=[decision]
    )
    
    print("✅ Stored agent decision in memory")


# ============================================================================
# Example 2: Retrieve Similar Past Decisions
# ============================================================================

async def example_retrieve_similar_decisions():
    """Retrieve similar past decisions for context"""
    
    client = await get_chromadb_client()
    
    # Current situation
    query = "Revenue dropped 12% this quarter due to supply chain delays"
    
    # Search for similar past decisions
    results = await client.search(
        collection="agent_decisions",
        query=query,
        filters={
            "outcome": "successful",  # Only successful decisions
            "domain": "sales",
        },
        top_k=5
    )
    
    print(f"\n📚 Found {len(results)} similar past decisions:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Similarity: {result['similarity']:.2%}")
        print(f"   Decision: {result['text'][:100]}...")
        print(f"   Effectiveness: {result['metadata'].get('effectiveness_score', 'N/A')}")


# ============================================================================
# Example 3: Store Business Incident
# ============================================================================

async def example_store_business_incident():
    """Store a business incident for pattern recognition"""
    
    client = await get_chromadb_client()
    
    incident = {
        "id": "incident_001",
        "text": (
            "Critical inventory stockout detected for Product SKU-12345. "
            "Quantity dropped from 500 to 0 units in 48 hours. "
            "Expected restock in 14 days. High revenue impact: $250K potential loss. "
            "Similar incident occurred 6 months ago with same supplier. "
            "Root cause: Supplier production delay due to raw material shortage."
        ),
        "metadata": {
            "incident_type": "stockout",
            "domain": "supply_chain",
            "severity": "critical",
            "detected_at": datetime.utcnow().isoformat(),
            "financial_impact": 250000.0,
            "affected_products": ["SKU-12345"],
            "affected_regions": ["North America"],
            "root_cause": "supplier_delay",
            "recurrence": True,
            "previous_incident_id": "incident_abc123",
            "tags": ["stockout", "supplier_delay", "high_impact", "recurring"],
        }
    }
    
    await client.add(
        collection="business_incidents",
        documents=[incident]
    )
    
    print("✅ Stored business incident in memory")


# ============================================================================
# Example 4: Find Recurring Incidents
# ============================================================================

async def example_find_recurring_incidents():
    """Find recurring incidents to identify systemic issues"""
    
    client = await get_chromadb_client()
    
    # Search for similar incidents
    query = "inventory stockout supplier delay"
    
    results = await client.search(
        collection="business_incidents",
        query=query,
        filters={
            "recurrence": True,
            "severity": {"$in": ["high", "critical"]},
        },
        top_k=10
    )
    
    print(f"\n🔄 Found {len(results)} recurring incidents:")
    for result in results:
        print(f"\n- {result['metadata']['incident_type']}")
        print(f"  Financial Impact: ${result['metadata']['financial_impact']:,.0f}")
        print(f"  Root Cause: {result['metadata']['root_cause']}")


# ============================================================================
# Example 5: Store Root Cause Analysis
# ============================================================================

async def example_store_root_cause_analysis():
    """Store RCA for knowledge reuse"""
    
    client = await get_chromadb_client()
    
    rca = {
        "id": "rca_001",
        "text": (
            "Root Cause Analysis: Q2 Revenue Drop. "
            "Primary cause: 3 enterprise deals ($2M total) delayed due to procurement bottleneck. "
            "Contributing factors: (1) New vendor approval process added 30 days, "
            "(2) Legal review backlog, (3) Budget freeze in customer organizations. "
            "Recommended actions: Streamline vendor approval, add legal resources, "
            "improve customer budget forecasting. "
            "Actions taken: Implemented automated vendor approval system, hired 2 legal staff. "
            "Effectiveness: 85% - Approval time reduced from 30 to 5 days."
        ),
        "metadata": {
            "rca_id": "rca_12345",
            "incident_id": "incident_67890",
            "domain": "sales",
            "analysis_method": "5_whys",
            "primary_cause": "procurement_bottleneck",
            "contributing_factors": ["vendor_approval_delay", "legal_backlog", "customer_budget_freeze"],
            "confidence_score": 0.92,
            "analyzed_by": "executive_decision_agent",
            "analyzed_at": datetime.utcnow().isoformat(),
            "validation_status": "validated",
            "actions_taken": ["streamline_approval", "hire_legal_staff"],
            "effectiveness_score": 0.85,
            "tags": ["revenue_drop", "procurement", "process_improvement", "high_effectiveness"],
        }
    }
    
    await client.add(
        collection="root_cause_analyses",
        documents=[rca]
    )
    
    print("✅ Stored root cause analysis in memory")


# ============================================================================
# Example 6: Learn from Effective RCAs
# ============================================================================

async def example_learn_from_effective_rcas():
    """Learn from highly effective root cause analyses"""
    
    client = await get_chromadb_client()
    
    query = "procurement delays affecting sales"
    
    results = await client.search(
        collection="root_cause_analyses",
        query=query,
        filters={
            "effectiveness_score": {"$gte": 0.8},  # High effectiveness
            "validation_status": "validated",
        },
        top_k=5
    )
    
    print(f"\n🎯 Found {len(results)} highly effective RCAs:")
    for result in results:
        print(f"\n- Primary Cause: {result['metadata']['primary_cause']}")
        print(f"  Effectiveness: {result['metadata']['effectiveness_score']:.0%}")
        print(f"  Actions: {', '.join(result['metadata']['actions_taken'])}")


# ============================================================================
# Example 7: Store Executive Recommendation
# ============================================================================

async def example_store_executive_recommendation():
    """Store executive recommendation for learning"""
    
    client = await get_chromadb_client()
    
    recommendation = {
        "id": "rec_001",
        "text": (
            "Executive Recommendation: Implement automated vendor approval system. "
            "Expected ROI: 300% over 12 months. Reduces approval time from 30 to 5 days. "
            "Estimated cost: $150K implementation, $30K annual maintenance. "
            "Risk: Medium (integration complexity). Timeline: 90 days. "
            "Dependencies: IT infrastructure upgrade, legal process redesign. "
            "Actual outcome: Implemented in 85 days, cost $145K, achieved 320% ROI."
        ),
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
            "status": "implemented",
            "approved_by": "coo@company.com",
            "approved_at": datetime.utcnow().isoformat(),
            "implemented_at": datetime.utcnow().isoformat(),
            "actual_roi": 3.2,
            "actual_cost": 145000.0,
            "actual_timeline_days": 85,
            "success_score": 0.95,
            "tags": ["automation", "procurement", "high_roi", "successful"],
        }
    }
    
    await client.add(
        collection="executive_recommendations",
        documents=[recommendation]
    )
    
    print("✅ Stored executive recommendation in memory")


# ============================================================================
# Example 8: Find High-ROI Recommendations
# ============================================================================

async def example_find_high_roi_recommendations():
    """Find successful high-ROI recommendations"""
    
    client = await get_chromadb_client()
    
    query = "process automation to improve efficiency"
    
    results = await client.search(
        collection="executive_recommendations",
        query=query,
        filters={
            "status": "implemented",
            "success_score": {"$gte": 0.8},
            "actual_roi": {"$gte": 2.0},
        },
        top_k=5
    )
    
    print(f"\n💰 Found {len(results)} high-ROI recommendations:")
    for result in results:
        print(f"\n- Category: {result['metadata']['category']}")
        print(f"  Estimated ROI: {result['metadata']['estimated_roi']:.1f}x")
        print(f"  Actual ROI: {result['metadata']['actual_roi']:.1f}x")
        print(f"  Success Score: {result['metadata']['success_score']:.0%}")


# ============================================================================
# Example 9: Store Simulation Outcome
# ============================================================================

async def example_store_simulation_outcome():
    """Store simulation results for predictive learning"""
    
    client = await get_chromadb_client()
    
    simulation = {
        "id": "sim_001",
        "text": (
            "Monte Carlo Simulation: Revenue Recovery Scenario. "
            "Tested 3 interventions: (1) Expedite procurement, (2) Offer customer incentives, "
            "(3) Increase sales team. Best case: Revenue recovers to $10M in 60 days (90th percentile). "
            "Most likely: $8.5M in 75 days (median). Worst case: $7M in 90 days (10th percentile). "
            "Recommended: Intervention #1 + #2 for optimal outcome. "
            "Actual outcome: $8.7M in 72 days - 98% prediction accuracy."
        ),
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
            "tags": ["revenue_recovery", "monte_carlo", "high_accuracy"],
        }
    }
    
    await client.add(
        collection="simulation_outcomes",
        documents=[simulation]
    )
    
    print("✅ Stored simulation outcome in memory")


# ============================================================================
# Example 10: Cross-Collection Search
# ============================================================================

async def example_cross_collection_search():
    """Search across multiple collections for comprehensive context"""
    
    client = await get_chromadb_client()
    
    query = "procurement delays affecting revenue"
    
    results = await client.search_multi(
        collections=["agent_decisions", "business_incidents", "root_cause_analyses"],
        query=query,
        filters={"domain": {"$in": ["sales", "supply_chain", "procurement"]}},
        top_k=3
    )
    
    print("\n🔍 Cross-collection search results:")
    for collection, docs in results.items():
        print(f"\n{collection.upper()}:")
        for doc in docs:
            print(f"  - {doc['text'][:80]}...")


# ============================================================================
# Example 11: Update Document with Outcome
# ============================================================================

async def example_update_with_outcome():
    """Update a decision with actual outcome for learning"""
    
    client = await get_chromadb_client()
    
    # Update decision with outcome
    await client.update(
        collection="agent_decisions",
        id="decision_001",
        metadata={
            "outcome": "successful",
            "effectiveness_score": 0.92,
            "resolution_time_hours": 120,
            "tags": ["revenue_drop", "procurement_delay", "escalation", "successful"],
        }
    )
    
    print("✅ Updated decision with outcome")


# ============================================================================
# Example 12: Archive Old Documents
# ============================================================================

async def example_archive_old_documents():
    """Archive documents older than retention period"""
    
    client = await get_chromadb_client()
    
    # Archive decisions older than 1 year
    archived_count = await client.archive_old_documents(
        collection="agent_decisions",
        days=365,
        filters={"outcome": {"$in": ["failed", "rejected"]}},  # Only archive unsuccessful
    )
    
    print(f"📦 Archived {archived_count} old documents")


# ============================================================================
# Example 13: Memory Health Check
# ============================================================================

async def example_memory_health_check():
    """Check memory system health and statistics"""
    
    client = await get_chromadb_client()
    
    health = await client.health_check()
    
    print("\n🏥 Memory System Health:")
    print(f"Status: {health['status']}")
    print(f"Total Documents: {health['total_documents']:,}")
    print("\nCollections:")
    for name, stats in health['collections'].items():
        print(f"  - {name}: {stats['count']:,} documents")


# ============================================================================
# Example 14: Agent Learning Pattern
# ============================================================================

async def example_agent_learning_pattern():
    """Complete agent learning pattern: retrieve → decide → store"""
    
    client = await get_chromadb_client()
    
    # Step 1: Retrieve similar past experiences
    print("\n1️⃣ Retrieving similar past experiences...")
    past_decisions = await client.search(
        collection="agent_decisions",
        query="revenue drop due to delays",
        filters={"outcome": "successful"},
        top_k=3
    )
    print(f"   Found {len(past_decisions)} relevant past decisions")
    
    # Step 2: Make decision based on past learnings
    print("\n2️⃣ Making decision based on learnings...")
    decision_text = (
        "Based on 3 similar past incidents, recommended immediate escalation "
        "to procurement team. Historical success rate: 92%. Expected resolution: 5 days."
    )
    
    # Step 3: Store new decision
    print("\n3️⃣ Storing new decision for future learning...")
    new_decision = {
        "id": f"decision_{datetime.utcnow().timestamp()}",
        "text": decision_text,
        "metadata": {
            "agent_name": "sales_agent",
            "decision_type": "anomaly_response",
            "domain": "sales",
            "confidence_score": 0.89,
            "timestamp": datetime.utcnow().isoformat(),
            "learned_from": [d["id"] for d in past_decisions],
            "tags": ["revenue_drop", "learned_decision"],
        }
    }
    
    await client.add(
        collection="agent_decisions",
        documents=[new_decision]
    )
    
    print("✅ Complete learning cycle executed")


# ============================================================================
# Run All Examples
# ============================================================================

async def run_all_examples():
    """Run all examples in sequence"""
    
    print("=" * 80)
    print("ChromaDB Memory System - Usage Examples")
    print("=" * 80)
    
    examples = [
        ("Store Agent Decision", example_store_agent_decision),
        ("Retrieve Similar Decisions", example_retrieve_similar_decisions),
        ("Store Business Incident", example_store_business_incident),
        ("Find Recurring Incidents", example_find_recurring_incidents),
        ("Store Root Cause Analysis", example_store_root_cause_analysis),
        ("Learn from Effective RCAs", example_learn_from_effective_rcas),
        ("Store Executive Recommendation", example_store_executive_recommendation),
        ("Find High-ROI Recommendations", example_find_high_roi_recommendations),
        ("Store Simulation Outcome", example_store_simulation_outcome),
        ("Cross-Collection Search", example_cross_collection_search),
        ("Update with Outcome", example_update_with_outcome),
        ("Archive Old Documents", example_archive_old_documents),
        ("Memory Health Check", example_memory_health_check),
        ("Agent Learning Pattern", example_agent_learning_pattern),
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n{'=' * 80}")
        print(f"Example {i}: {name}")
        print(f"{'=' * 80}")
        try:
            await func()
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n{'=' * 80}")
    print("All examples completed!")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    asyncio.run(run_all_examples())

# Made with Bob
