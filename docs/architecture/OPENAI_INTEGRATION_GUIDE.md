# OpenAI GPT-4/5 Integration Guide - Enterprise Digital COO

## Document Information

**Version**: 1.0  
**Date**: 2026-06-17  
**Author**: OpenAI Solutions Architect  
**Model**: GPT-4 Turbo / GPT-5 (when available)

---

## Overview

This guide provides complete OpenAI integration specifications for the Enterprise Digital COO, including system prompts, user prompts, output schemas, function calling, and structured JSON outputs.

### Integration Strategy

- **Structured Outputs**: JSON mode with Pydantic schemas
- **Function Calling**: Tool use for data retrieval and actions
- **System Prompts**: Role-based expert personas
- **Temperature Control**: 0.3 for analysis, 0.7 for recommendations
- **Token Optimization**: Efficient prompt engineering

---

## Table of Contents

1. [Root Cause Analysis](#1-root-cause-analysis)
2. [Executive Recommendations](#2-executive-recommendations)
3. [Business Simulations](#3-business-simulations)
4. [Risk Assessment](#4-risk-assessment)
5. [Function Calling Structure](#5-function-calling-structure)
6. [Best Practices](#6-best-practices)

---

## 1. Root Cause Analysis

### System Prompt

```python
ROOT_CAUSE_ANALYSIS_SYSTEM = """You are an expert Business Analyst specializing in Root Cause Analysis with 25 years of experience.

Your expertise: 5 Whys, Fishbone diagrams, Fault tree analysis, Statistical correlation.

Your task: Identify root causes of business anomalies by analyzing multi-domain data, identifying causal relationships, distinguishing symptoms from causes, and providing evidence-based conclusions.

Output: Structured JSON with root causes, evidence, confidence scores.

Be analytical, data-driven, and precise."""
```

### User Prompt Template

```python
def create_rca_prompt(anomaly: dict, analyses: dict) -> str:
    return f"""Perform root cause analysis:

ANOMALY: {anomaly['type']} - {anomaly['description']}
Severity: {anomaly['severity']} | Deviation: {anomaly['deviation']}%

DOMAIN ANALYSES:
Sales: {analyses['sales']}
Finance: {analyses['finance']}
Supply Chain: {analyses['supply_chain']}

REQUIRED:
1. Primary root cause with evidence
2. 2-3 contributing factors
3. Causal chain explanation
4. Cross-domain correlations
5. Business impact estimate
6. Confidence score (0-1)

Output in JSON format."""
```

### Output Schema (Pydantic)

```python
from pydantic import BaseModel, Field
from typing import List

class Evidence(BaseModel):
    source: str
    metric: str
    value: str
    relevance: str

class RootCause(BaseModel):
    root_cause: str
    category: str  # operational, financial, external, systemic
    confidence_score: float = Field(ge=0, le=1)
    evidence: List[Evidence]
    causal_chain: List[str]
    estimated_impact: dict

class RCAOutput(BaseModel):
    analysis_id: str
    primary_root_cause: RootCause
    alternative_hypotheses: List[RootCause]
    overall_confidence: float
    recommended_next_steps: List[str]
```

### Example JSON Output

```json
{
  "analysis_id": "rca_001",
  "primary_root_cause": {
    "root_cause": "Supplier equipment failure causing 3-week stockout",
    "category": "operational",
    "confidence_score": 0.92,
    "evidence": [
      {
        "source": "supply_chain_analysis",
        "metric": "supplier_on_time_delivery",
        "value": "45% vs 95% baseline",
        "relevance": "Confirms supplier delivery issues"
      }
    ],
    "causal_chain": [
      "Supplier equipment failure",
      "Production halted 3 weeks",
      "Inventory depleted",
      "Product unavailable",
      "Revenue drops 15%"
    ],
    "estimated_impact": {
      "revenue_loss": 1500000,
      "customer_churn_risk": "15-20%"
    }
  },
  "overall_confidence": 0.92,
  "recommended_next_steps": [
    "Source alternative suppliers",
    "Increase safety stock to 30 days"
  ]
}
```

---

## 2. Executive Recommendations

### System Prompt

```python
EXECUTIVE_RECOMMENDATIONS_SYSTEM = """You are a seasoned COO with 30 years of executive leadership in Fortune 500 companies.

Your expertise: Strategic decision-making, Operational excellence, Change management, Risk mitigation, Resource optimization.

Your task: Generate actionable executive recommendations by synthesizing complex data, prioritizing by impact/urgency, assessing feasibility, and quantifying outcomes.

Output: Structured JSON with prioritized recommendations, ROI estimates, implementation plans.

Be decisive, strategic, action-oriented."""
```

### User Prompt Template

```python
def create_recommendations_prompt(root_causes: list, simulations: dict, context: dict) -> str:
    return f"""Generate executive recommendations:

ROOT CAUSES: {root_causes}
SIMULATIONS: Best: ${simulations['best_case']}, Likely: ${simulations['most_likely']}, Worst: ${simulations['worst_case']}
CONTEXT: Revenue: ${context['revenue']}, Cash: ${context['cash']}

REQUIREMENTS:
1. 5-7 prioritized recommendations
2. For each: action, rationale, impact, effort, timeline, resources, metrics, risks
3. Prioritize by: Impact × Urgency / Effort
4. SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)

Output in JSON format."""
```

### Output Schema

```python
class Recommendation(BaseModel):
    recommendation_id: str
    priority: int = Field(ge=1, le=10)
    category: str  # immediate, short_term, medium_term, long_term
    title: str
    description: str
    rationale: str
    expected_impact: dict
    implementation_effort: str  # low, medium, high
    timeline: str
    resource_requirements: List[dict]
    success_metrics: List[dict]
    risks: List[dict]
    estimated_roi: float
    confidence_level: float

class RecommendationsOutput(BaseModel):
    analysis_id: str
    recommendations: List[Recommendation]
    implementation_sequence: List[str]
    total_investment: float
    total_return: float
    overall_roi: float
    executive_summary: str
```

### Example JSON Output

```json
{
  "analysis_id": "rec_001",
  "recommendations": [
    {
      "recommendation_id": "REC-001",
      "priority": 1,
      "category": "immediate",
      "title": "Emergency Supplier Diversification",
      "description": "Onboard 2-3 alternative suppliers for Product X",
      "rationale": "Single-source dependency caused $1.5M loss",
      "expected_impact": {
        "revenue_protection": 6000000,
        "risk_reduction": "85%"
      },
      "implementation_effort": "medium",
      "timeline": "4-6 weeks",
      "resource_requirements": [
        {"type": "budget", "amount": 150000}
      ],
      "success_metrics": [
        {"metric": "supplier_count", "target": "3+"}
      ],
      "risks": [
        {"risk": "Quality issues", "mitigation": "Rigorous testing"}
      ],
      "estimated_roi": 2900.0,
      "confidence_level": 0.9
    }
  ],
  "total_investment": 1150000,
  "total_return": 11900000,
  "overall_roi": 935.0,
  "executive_summary": "Three immediate actions address $1.5M loss: diversify suppliers, increase safety stock, launch win-back campaign. $1.15M investment yields $11.9M return (935% ROI)."
}
```

---

## 3. Business Simulations

### System Prompt

```python
BUSINESS_SIMULATION_SYSTEM = """You are an expert Business Analytics Director specializing in predictive modeling and Monte Carlo simulations.

Your expertise: Statistical modeling, Monte Carlo design, Scenario planning, Risk quantification, Sensitivity analysis.

Your task: Design and interpret business simulations by defining parameters, identifying variables, establishing distributions, and quantifying uncertainty.

Output: Structured JSON with simulation design, results, interpretations.

Be rigorous, statistically sound, transparent about assumptions."""
```

### User Prompt Template

```python
def create_simulation_prompt(scenario: str, metrics: dict, interventions: list) -> str:
    return f"""Design business simulation:

SCENARIO: {scenario}
CURRENT METRICS: {metrics}
INTERVENTIONS: {interventions}

REQUIREMENTS:
- Time Horizon: 90 days
- Iterations: 10,000 Monte Carlo
- Scenarios: Best (90th %), Most Likely (50th %), Worst (10th %)
- Variables: Revenue, costs, customer behavior, supply recovery
- Confidence Intervals: 80% and 95%

ANALYSIS:
1. Define simulation parameters
2. Identify probability distributions
3. Model intervention effects
4. Calculate scenario outcomes
5. Assess sensitivity
6. Quantify risks/opportunities

Output in JSON format."""
```

### Output Schema

```python
class ScenarioOutcome(BaseModel):
    scenario_name: str  # best_case, most_likely, worst_case
    probability: float
    revenue_forecast: float
    cost_forecast: float
    profit_forecast: float
    key_metrics: dict
    confidence_interval_80: dict
    confidence_interval_95: dict

class SimulationOutput(BaseModel):
    simulation_id: str
    time_horizon_days: int
    iterations: int
    scenarios: List[ScenarioOutcome]
    sensitivity_analysis: List[dict]
    risk_assessment: dict
    recommended_monitoring: List[str]
    confidence_in_simulation: float
```

### Example JSON Output

```json
{
  "simulation_id": "sim_001",
  "time_horizon_days": 90,
  "iterations": 10000,
  "scenarios": [
    {
      "scenario_name": "best_case",
      "probability": 0.10,
      "revenue_forecast": 9750000,
      "cost_forecast": 6200000,
      "profit_forecast": 3550000,
      "key_metrics": {
        "revenue_recovery": "97.5%",
        "customer_retention": "92%"
      },
      "confidence_interval_80": {"lower": 9500000, "upper": 10000000},
      "confidence_interval_95": {"lower": 9300000, "upper": 10200000}
    },
    {
      "scenario_name": "most_likely",
      "probability": 0.50,
      "revenue_forecast": 8850000,
      "cost_forecast": 6400000,
      "profit_forecast": 2450000,
      "key_metrics": {
        "revenue_recovery": "88.5%",
        "customer_retention": "82%"
      },
      "confidence_interval_80": {"lower": 8500000, "upper": 9200000},
      "confidence_interval_95": {"lower": 8200000, "upper": 9500000}
    }
  ],
  "sensitivity_analysis": [
    {
      "variable": "customer_retention_rate",
      "impact": "high",
      "elasticity": 1.8
    }
  ],
  "risk_assessment": {
    "probability_below_80_recovery": 0.15,
    "maximum_potential_loss": 2500000
  },
  "recommended_monitoring": [
    "Weekly revenue by product",
    "Daily supplier performance",
    "Customer retention rate"
  ],
  "confidence_in_simulation": 0.82
}
```

---

## 4. Risk Assessment

### System Prompt

```python
RISK_ASSESSMENT_SYSTEM = """You are a Chief Risk Officer with 25 years of experience in enterprise risk management and compliance.

Your expertise: COSO framework, ISO 31000, Quantitative risk analysis, Risk scoring, Compliance, Business continuity.

Your task: Assess enterprise risks by identifying/categorizing risks, evaluating likelihood/impact, calculating scores, assessing controls, and recommending mitigations.

Output: Structured JSON with risk assessments, scores, mitigation plans.

Be thorough, conservative, focused on protection."""
```

### User Prompt Template

```python
def create_risk_assessment_prompt(situation: dict, analyses: dict, controls: list) -> str:
    return f"""Perform risk assessment:

SITUATION: {situation}
ANALYSES: {analyses}
CURRENT CONTROLS: {controls}

REQUIREMENTS:
1. Identify risks: Operational, Financial, Strategic, Compliance, Reputational, Technology
2. For each: Likelihood (1-5), Impact (1-5), Risk Score, Control effectiveness, Residual risk
3. Prioritize by: Score, Velocity, Cascading effects
4. Recommend mitigations: Immediate (0-30d), Short-term (1-3m), Long-term (3-12m)
5. Quantify financial exposure

Output in JSON format."""
```

### Output Schema

```python
class Risk(BaseModel):
    risk_id: str
    risk_name: str
    category: str
    description: str
    likelihood: int = Field(ge=1, le=5)
    impact: int = Field(ge=1, le=5)
    risk_score: int = Field(ge=1, le=25)
    velocity: str  # slow, moderate, fast, immediate
    current_controls: List[dict]
    residual_risk_level: str
    financial_exposure: dict
    mitigation_actions: List[dict]

class RiskAssessmentOutput(BaseModel):
    assessment_id: str
    risks_identified: List[Risk]
    top_risks: List[str]
    total_financial_exposure: dict
    overall_risk_posture: str
    critical_actions_required: List[str]
```

### Example JSON Output

```json
{
  "assessment_id": "risk_001",
  "risks_identified": [
    {
      "risk_id": "RISK-001",
      "risk_name": "Extended Supply Chain Disruption",
      "category": "operational",
      "description": "Supplier may experience prolonged recovery",
      "likelihood": 3,
      "impact": 5,
      "risk_score": 15,
      "velocity": "moderate",
      "current_controls": [
        {
          "control": "Supplier monitoring",
          "effectiveness": "adequate",
          "gaps": ["No real-time alerts"]
        }
      ],
      "residual_risk_level": "high",
      "financial_exposure": {
        "minimum": 2000000,
        "maximum": 8000000,
        "expected": 4500000
      },
      "mitigation_actions": [
        {
          "action": "Emergency supplier diversification",
          "timeline": "immediate",
          "cost": 200000,
          "risk_reduction": "60%"
        }
      ]
    }
  ],
  "top_risks": ["RISK-001", "RISK-002"],
  "total_financial_exposure": {
    "minimum": 3500000,
    "maximum": 14000000,
    "expected": 7700000
  },
  "overall_risk_posture": "elevated",
  "critical_actions_required": [
    "Diversify suppliers immediately",
    "Increase safety stock"
  ]
}
```

---

## 5. Function Calling Structure

### Available Functions

```python
AVAILABLE_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_historical_data",
            "description": "Retrieve historical business metrics",
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "enum": ["sales", "finance", "supply_chain"]},
                    "metric": {"type": "string"},
                    "time_range": {"type": "string", "description": "e.g., '30d', '90d', '1y'"}
                },
                "required": ["domain", "metric", "time_range"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_financial_impact",
            "description": "Calculate financial impact of scenarios",
            "parameters": {
                "type": "object",
                "properties": {
                    "scenario": {"type": "string"},
                    "revenue_change": {"type": "number"},
                    "cost_change": {"type": "number"},
                    "time_horizon_days": {"type": "integer"}
                },
                "required": ["scenario", "revenue_change"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_monte_carlo_simulation",
            "description": "Run Monte Carlo simulation",
            "parameters": {
                "type": "object",
                "properties": {
                    "variables": {"type": "array", "items": {"type": "object"}},
                    "iterations": {"type": "integer", "default": 10000},
                    "time_horizon_days": {"type": "integer", "default": 90}
                },
                "required": ["variables"]
            }
        }
    }
]
```

### Function Calling Example

```python
async def call_with_functions(prompt: str) -> dict:
    response = await client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        tools=AVAILABLE_FUNCTIONS,
        tool_choice="auto"
    )
    
    # Handle function calls
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Execute function
            result = await execute_function(function_name, function_args)
            
            # Continue conversation with function result
            messages.append({
                "role": "function",
                "name": function_name,
                "content": json.dumps(result)
            })
    
    return response
```

---

## 6. Best Practices

### Temperature Settings

```python
TEMPERATURE_BY_TASK = {
    "root_cause_analysis": 0.3,      # Deterministic, analytical
    "risk_assessment": 0.3,          # Conservative, precise
    "business_simulation": 0.4,      # Balanced
    "recommendations": 0.7,          # Creative, strategic
    "executive_summary": 0.6         # Clear, engaging
}
```

### Token Optimization

```python
# Use concise prompts
# Provide only relevant context
# Use structured data formats
# Leverage function calling for data retrieval
# Cache common responses
```

### Error Handling

```python
async def call_openai_with_retry(prompt: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return await call_openai(prompt)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
```

### Cost Optimization

```python
# Use GPT-4 Turbo for cost efficiency
# Implement response caching
# Use function calling to reduce context
# Batch similar requests
# Monitor token usage
```

---

## Summary

This guide provides production-ready OpenAI integration for the Enterprise Digital COO with:

✅ **4 Complete Use Cases**: Root cause analysis, recommendations, simulations, risk assessment  
✅ **Structured Outputs**: Pydantic schemas for type safety  
✅ **Function Calling**: Tool use for data retrieval  
✅ **Example JSON**: Real-world output examples  
✅ **Best Practices**: Temperature, optimization, error handling  

**Status**: Production-ready for GPT-4 Turbo and GPT-5