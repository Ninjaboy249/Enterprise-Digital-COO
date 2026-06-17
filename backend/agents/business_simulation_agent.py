"""
Business Simulation Agent
Enterprise Strategy Consultant that simulates business scenarios
and predicts outcomes using Monte Carlo methods and predictive modeling
"""

import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from enum import Enum
import logging

from backend.agents.base_agent import BaseAgent
from backend.memory.chromadb_client import get_chromadb_client

logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Constants
# ============================================================================

class ScenarioType(str, Enum):
    """Types of business scenarios"""
    BUDGET_CHANGE = "budget_change"
    SUPPLIER_CHANGE = "supplier_change"
    HIRING_CHANGE = "hiring_change"
    CUSTOMER_BEHAVIOR = "customer_behavior"
    PRODUCT_LAUNCH = "product_launch"
    MARKET_CONDITION = "market_condition"
    OPERATIONAL_CHANGE = "operational_change"
    STRATEGIC_INITIATIVE = "strategic_initiative"


class ImpactCategory(str, Enum):
    """Categories of business impact"""
    REVENUE = "revenue"
    COST = "cost"
    RISK = "risk"
    CUSTOMER = "customer"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"


# ============================================================================
# Pydantic Models for Structured Output
# ============================================================================

class ScenarioInput(BaseModel):
    """Input parameters for a business scenario"""
    scenario_type: ScenarioType
    description: str = Field(description="Scenario description")
    parameters: Dict[str, Any] = Field(description="Scenario-specific parameters")
    baseline_metrics: Dict[str, float] = Field(description="Current baseline metrics")
    time_horizon_days: int = Field(default=90, description="Simulation time horizon")


class DistributionParams(BaseModel):
    """Statistical distribution parameters"""
    mean: float = Field(description="Mean value")
    std_dev: float = Field(description="Standard deviation")
    min_value: Optional[float] = Field(None, description="Minimum bound")
    max_value: Optional[float] = Field(None, description="Maximum bound")
    percentile_10: float = Field(description="10th percentile")
    percentile_50: float = Field(description="50th percentile (median)")
    percentile_90: float = Field(description="90th percentile")


class ImpactPrediction(BaseModel):
    """Predicted impact for a specific category"""
    category: ImpactCategory
    metric_name: str = Field(description="Name of the metric")
    baseline_value: float = Field(description="Current baseline value")
    
    # Predicted outcomes
    best_case: float = Field(description="90th percentile outcome")
    most_likely: float = Field(description="Median outcome")
    worst_case: float = Field(description="10th percentile outcome")
    
    # Statistical measures
    expected_value: float = Field(description="Mean expected value")
    confidence_interval_95: Tuple[float, float] = Field(description="95% confidence interval")
    
    # Change metrics
    absolute_change: float = Field(description="Expected absolute change")
    percentage_change: float = Field(description="Expected percentage change")
    
    # Probability assessments
    probability_positive: float = Field(ge=0.0, le=1.0, description="Probability of positive outcome")
    probability_negative: float = Field(ge=0.0, le=1.0, description="Probability of negative outcome")


class RevenueImpact(ImpactPrediction):
    """Revenue-specific impact prediction"""
    category: ImpactCategory = ImpactCategory.REVENUE
    revenue_streams_affected: List[str] = Field(description="Affected revenue streams")
    customer_segments_affected: List[str] = Field(description="Affected customer segments")


class CostImpact(ImpactPrediction):
    """Cost-specific impact prediction"""
    category: ImpactCategory = ImpactCategory.COST
    cost_categories_affected: List[str] = Field(description="Affected cost categories")
    one_time_costs: float = Field(description="One-time implementation costs")
    recurring_costs: float = Field(description="Ongoing recurring costs")


class RiskImpact(ImpactPrediction):
    """Risk-specific impact prediction"""
    category: ImpactCategory = ImpactCategory.RISK
    risk_factors: List[str] = Field(description="Key risk factors")
    risk_score_change: int = Field(description="Change in risk score")
    mitigation_strategies: List[str] = Field(description="Recommended mitigations")


class CustomerImpact(ImpactPrediction):
    """Customer-specific impact prediction"""
    category: ImpactCategory = ImpactCategory.CUSTOMER
    churn_rate_change: float = Field(description="Change in churn rate")
    satisfaction_score_change: float = Field(description="Change in satisfaction score")
    acquisition_rate_change: float = Field(description="Change in acquisition rate")
    lifetime_value_change: float = Field(description="Change in customer LTV")


class RecommendedAction(BaseModel):
    """Recommended action based on simulation"""
    action_id: str
    title: str
    description: str
    priority: int = Field(ge=1, le=10)
    rationale: str = Field(description="Why this action is recommended")
    expected_benefit: float = Field(description="Expected benefit in USD")
    implementation_cost: float = Field(description="Cost to implement")
    timeline_days: int = Field(description="Implementation timeline")
    success_probability: float = Field(ge=0.0, le=1.0)


class SimulationResult(BaseModel):
    """Complete simulation result"""
    simulation_id: str
    timestamp: str
    scenario: ScenarioInput
    
    # Simulation metadata
    iterations: int = Field(description="Number of Monte Carlo iterations")
    confidence_level: float = Field(description="Statistical confidence level")
    
    # Impact predictions
    revenue_impact: RevenueImpact
    cost_impact: CostImpact
    risk_impact: RiskImpact
    customer_impact: CustomerImpact
    
    # Overall assessment
    net_financial_impact: float = Field(description="Net financial impact (revenue - cost)")
    overall_recommendation: str = Field(description="Go/No-Go recommendation")
    confidence_score: float = Field(ge=0.0, le=1.0)
    
    # Recommended actions
    recommended_actions: List[RecommendedAction]
    
    # Key insights
    key_insights: List[str] = Field(description="Top 3-5 insights")
    assumptions: List[str] = Field(description="Key assumptions made")
    limitations: List[str] = Field(description="Simulation limitations")
    
    # Execution metadata
    execution_time_seconds: float


# ============================================================================
# Business Simulation Agent
# ============================================================================

class BusinessSimulationAgent(BaseAgent):
    """
    Business Simulation Agent - Enterprise Strategy Consultant
    
    Capabilities:
    1. Monte Carlo simulations (10,000+ iterations)
    2. Multi-dimensional impact analysis
    3. Probabilistic forecasting
    4. Scenario comparison
    5. Risk-adjusted recommendations
    
    Answers "What happens if..." questions with quantified predictions
    """
    
    def __init__(self, default_iterations: int = 10000):
        super().__init__(
            agent_name="business_simulation_agent",
            domain="strategy"
        )
        self.default_iterations = default_iterations
        
        # Simulation parameters
        self.confidence_level = 0.95
        np.random.seed(42)  # For reproducibility in testing
    
    async def simulate_scenario(
        self,
        scenario: ScenarioInput,
        iterations: Optional[int] = None
    ) -> SimulationResult:
        """
        Simulate a business scenario and predict outcomes
        
        Args:
            scenario: Scenario input parameters
            iterations: Number of Monte Carlo iterations
            
        Returns:
            Complete simulation result with predictions
        """
        start_time = datetime.utcnow()
        iterations = iterations or self.default_iterations
        
        logger.info(f"Simulating scenario: {scenario.scenario_type} with {iterations} iterations")
        
        # Step 1: Retrieve historical data for calibration
        historical_data = await self._retrieve_historical_data(scenario)
        
        # Step 2: Run Monte Carlo simulation
        simulation_data = await self._run_monte_carlo_simulation(
            scenario, iterations, historical_data
        )
        
        # Step 3: Predict revenue impact
        revenue_impact = await self._predict_revenue_impact(scenario, simulation_data)
        
        # Step 4: Predict cost impact
        cost_impact = await self._predict_cost_impact(scenario, simulation_data)
        
        # Step 5: Predict risk impact
        risk_impact = await self._predict_risk_impact(scenario, simulation_data)
        
        # Step 6: Predict customer impact
        customer_impact = await self._predict_customer_impact(scenario, simulation_data)
        
        # Step 7: Calculate net financial impact
        net_impact = revenue_impact.expected_value - cost_impact.expected_value
        
        # Step 8: Generate recommendations
        recommendations = await self._generate_recommendations(
            scenario, revenue_impact, cost_impact, risk_impact, customer_impact
        )
        
        # Step 9: Determine overall recommendation
        overall_rec = self._determine_overall_recommendation(
            net_impact, risk_impact, recommendations
        )
        
        # Step 10: Extract key insights
        insights = await self._extract_key_insights(
            scenario, revenue_impact, cost_impact, risk_impact, customer_impact
        )
        
        # Step 11: Document assumptions and limitations
        assumptions = self._document_assumptions(scenario)
        limitations = self._document_limitations(scenario, iterations)
        
        # Calculate confidence score
        confidence = self._calculate_confidence_score(
            simulation_data, historical_data, iterations
        )
        
        # Calculate execution time
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Create result
        result = SimulationResult(
            simulation_id=f"sim_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow().isoformat(),
            scenario=scenario,
            iterations=iterations,
            confidence_level=self.confidence_level,
            revenue_impact=revenue_impact,
            cost_impact=cost_impact,
            risk_impact=risk_impact,
            customer_impact=customer_impact,
            net_financial_impact=net_impact,
            overall_recommendation=overall_rec,
            confidence_score=confidence,
            recommended_actions=recommendations,
            key_insights=insights,
            assumptions=assumptions,
            limitations=limitations,
            execution_time_seconds=duration
        )
        
        # Store in memory for learning
        await self._store_simulation_in_memory(result)
        
        logger.info(
            f"Simulation complete: Net impact ${net_impact:,.0f}, "
            f"Confidence {confidence:.0%}"
        )
        
        return result
    
    async def _retrieve_historical_data(
        self,
        scenario: ScenarioInput
    ) -> List[Dict[str, Any]]:
        """Retrieve historical simulation data for calibration"""
        memory = await get_chromadb_client()
        
        # Search for similar scenarios
        query = f"{scenario.scenario_type} {scenario.description}"
        
        results = await memory.search(
            collection="simulation_outcomes",
            query=query,
            filters={"prediction_accuracy": {"$gte": 0.7}},  # High accuracy only
            top_k=5
        )
        
        return results
    
    async def _run_monte_carlo_simulation(
        self,
        scenario: ScenarioInput,
        iterations: int,
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, np.ndarray]:
        """
        Run Monte Carlo simulation
        
        Returns:
            Dictionary of simulated metric arrays
        """
        logger.info(f"Running Monte Carlo simulation with {iterations} iterations")
        
        # Initialize result arrays
        simulation_data = {
            "revenue": np.zeros(iterations),
            "cost": np.zeros(iterations),
            "risk_score": np.zeros(iterations),
            "customer_churn": np.zeros(iterations),
            "customer_satisfaction": np.zeros(iterations),
        }
        
        # Get baseline metrics
        baseline_revenue = scenario.baseline_metrics.get("revenue", 1000000)
        baseline_cost = scenario.baseline_metrics.get("cost", 500000)
        baseline_risk = scenario.baseline_metrics.get("risk_score", 10)
        baseline_churn = scenario.baseline_metrics.get("churn_rate", 0.05)
        baseline_satisfaction = scenario.baseline_metrics.get("satisfaction_score", 80)
        
        # Scenario-specific impact factors (calibrated from historical data)
        impact_factors = self._calibrate_impact_factors(scenario, historical_data)
        
        # Run iterations
        for i in range(iterations):
            # Simulate revenue impact
            revenue_factor = np.random.normal(
                impact_factors["revenue_mean"],
                impact_factors["revenue_std"]
            )
            simulation_data["revenue"][i] = baseline_revenue * (1 + revenue_factor)
            
            # Simulate cost impact
            cost_factor = np.random.normal(
                impact_factors["cost_mean"],
                impact_factors["cost_std"]
            )
            simulation_data["cost"][i] = baseline_cost * (1 + cost_factor)
            
            # Simulate risk impact
            risk_change = np.random.normal(
                impact_factors["risk_mean"],
                impact_factors["risk_std"]
            )
            simulation_data["risk_score"][i] = max(0, baseline_risk + risk_change)
            
            # Simulate customer churn
            churn_change = np.random.normal(
                impact_factors["churn_mean"],
                impact_factors["churn_std"]
            )
            simulation_data["customer_churn"][i] = np.clip(
                baseline_churn + churn_change, 0, 1
            )
            
            # Simulate customer satisfaction
            satisfaction_change = np.random.normal(
                impact_factors["satisfaction_mean"],
                impact_factors["satisfaction_std"]
            )
            simulation_data["customer_satisfaction"][i] = np.clip(
                baseline_satisfaction + satisfaction_change, 0, 100
            )
        
        return simulation_data
    
    def _calibrate_impact_factors(
        self,
        scenario: ScenarioInput,
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calibrate impact factors based on scenario type and historical data"""
        
        # Default impact factors by scenario type
        default_factors = {
            ScenarioType.BUDGET_CHANGE: {
                "revenue_mean": -0.05, "revenue_std": 0.02,
                "cost_mean": -0.10, "cost_std": 0.03,
                "risk_mean": 2, "risk_std": 1,
                "churn_mean": 0.01, "churn_std": 0.005,
                "satisfaction_mean": -3, "satisfaction_std": 2,
            },
            ScenarioType.SUPPLIER_CHANGE: {
                "revenue_mean": 0.02, "revenue_std": 0.03,
                "cost_mean": -0.08, "cost_std": 0.04,
                "risk_mean": 3, "risk_std": 2,
                "churn_mean": 0.005, "churn_std": 0.003,
                "satisfaction_mean": 1, "satisfaction_std": 3,
            },
            ScenarioType.HIRING_CHANGE: {
                "revenue_mean": -0.03, "revenue_std": 0.02,
                "cost_mean": -0.15, "cost_std": 0.02,
                "risk_mean": 4, "risk_std": 2,
                "churn_mean": 0.02, "churn_std": 0.01,
                "satisfaction_mean": -5, "satisfaction_std": 3,
            },
            ScenarioType.CUSTOMER_BEHAVIOR: {
                "revenue_mean": -0.10, "revenue_std": 0.05,
                "cost_mean": 0.02, "cost_std": 0.02,
                "risk_mean": 5, "risk_std": 2,
                "churn_mean": 0.05, "churn_std": 0.02,
                "satisfaction_mean": -8, "satisfaction_std": 4,
            },
            ScenarioType.PRODUCT_LAUNCH: {
                "revenue_mean": -0.08, "revenue_std": 0.04,
                "cost_mean": 0.05, "cost_std": 0.03,
                "risk_mean": 6, "risk_std": 3,
                "churn_mean": 0.03, "churn_std": 0.015,
                "satisfaction_mean": -6, "satisfaction_std": 4,
            },
        }
        
        # Get default factors for scenario type
        factors = default_factors.get(
            scenario.scenario_type,
            default_factors[ScenarioType.BUDGET_CHANGE]  # Fallback
        )
        
        # Adjust based on scenario parameters
        if "magnitude" in scenario.parameters:
            magnitude = scenario.parameters["magnitude"]
            # Scale factors by magnitude
            for key in factors:
                if "mean" in key:
                    factors[key] *= magnitude
        
        # Calibrate from historical data if available
        if historical_data:
            # Average historical outcomes
            avg_accuracy = np.mean([
                d.get("metadata", {}).get("prediction_accuracy", 0.7)
                for d in historical_data
            ])
            
            # Adjust std dev based on historical accuracy
            accuracy_factor = 1.0 / avg_accuracy if avg_accuracy > 0 else 1.0
            for key in factors:
                if "std" in key:
                    factors[key] *= accuracy_factor
        
        return factors
    
    async def _predict_revenue_impact(
        self,
        scenario: ScenarioInput,
        simulation_data: Dict[str, np.ndarray]
    ) -> RevenueImpact:
        """Predict revenue impact from simulation data"""
        
        revenue_array = simulation_data["revenue"]
        baseline = scenario.baseline_metrics.get("revenue", 1000000)
        
        # Calculate statistics
        best_case = np.percentile(revenue_array, 90)
        most_likely = np.median(revenue_array)
        worst_case = np.percentile(revenue_array, 10)
        expected = np.mean(revenue_array)
        ci_lower = np.percentile(revenue_array, 2.5)
        ci_upper = np.percentile(revenue_array, 97.5)
        
        # Calculate changes
        absolute_change = expected - baseline
        percentage_change = (absolute_change / baseline) * 100 if baseline > 0 else 0
        
        # Calculate probabilities
        prob_positive = np.sum(revenue_array > baseline) / len(revenue_array)
        prob_negative = 1 - prob_positive
        
        # Use LLM to identify affected streams and segments
        affected_analysis = await self._analyze_affected_areas(scenario, "revenue")
        
        return RevenueImpact(
            metric_name="Total Revenue",
            baseline_value=baseline,
            best_case=best_case,
            most_likely=most_likely,
            worst_case=worst_case,
            expected_value=expected,
            confidence_interval_95=(ci_lower, ci_upper),
            absolute_change=absolute_change,
            percentage_change=percentage_change,
            probability_positive=prob_positive,
            probability_negative=prob_negative,
            revenue_streams_affected=affected_analysis.get("streams", ["All streams"]),
            customer_segments_affected=affected_analysis.get("segments", ["All segments"]),
        )
    
    async def _predict_cost_impact(
        self,
        scenario: ScenarioInput,
        simulation_data: Dict[str, np.ndarray]
    ) -> CostImpact:
        """Predict cost impact from simulation data"""
        
        cost_array = simulation_data["cost"]
        baseline = scenario.baseline_metrics.get("cost", 500000)
        
        # Calculate statistics
        best_case = np.percentile(cost_array, 10)  # Lower is better for costs
        most_likely = np.median(cost_array)
        worst_case = np.percentile(cost_array, 90)
        expected = np.mean(cost_array)
        ci_lower = np.percentile(cost_array, 2.5)
        ci_upper = np.percentile(cost_array, 97.5)
        
        # Calculate changes
        absolute_change = expected - baseline
        percentage_change = (absolute_change / baseline) * 100 if baseline > 0 else 0
        
        # Calculate probabilities (for costs, negative change is positive outcome)
        prob_positive = np.sum(cost_array < baseline) / len(cost_array)
        prob_negative = 1 - prob_positive
        
        # Estimate one-time vs recurring costs
        one_time = scenario.parameters.get("one_time_cost", 0)
        recurring = absolute_change if absolute_change > 0 else 0
        
        # Analyze affected cost categories
        affected_analysis = await self._analyze_affected_areas(scenario, "cost")
        
        return CostImpact(
            metric_name="Total Cost",
            baseline_value=baseline,
            best_case=best_case,
            most_likely=most_likely,
            worst_case=worst_case,
            expected_value=expected,
            confidence_interval_95=(ci_lower, ci_upper),
            absolute_change=absolute_change,
            percentage_change=percentage_change,
            probability_positive=prob_positive,
            probability_negative=prob_negative,
            cost_categories_affected=affected_analysis.get("categories", ["Operating costs"]),
            one_time_costs=one_time,
            recurring_costs=recurring,
        )
    
    async def _predict_risk_impact(
        self,
        scenario: ScenarioInput,
        simulation_data: Dict[str, np.ndarray]
    ) -> RiskImpact:
        """Predict risk impact from simulation data"""
        
        risk_array = simulation_data["risk_score"]
        baseline = scenario.baseline_metrics.get("risk_score", 10)
        
        # Calculate statistics
        best_case = np.percentile(risk_array, 10)
        most_likely = np.median(risk_array)
        worst_case = np.percentile(risk_array, 90)
        expected = np.mean(risk_array)
        ci_lower = np.percentile(risk_array, 2.5)
        ci_upper = np.percentile(risk_array, 97.5)
        
        # Calculate changes
        absolute_change = expected - baseline
        percentage_change = (absolute_change / baseline) * 100 if baseline > 0 else 0
        risk_score_change = int(round(absolute_change))
        
        # Calculate probabilities
        prob_positive = np.sum(risk_array < baseline) / len(risk_array)
        prob_negative = 1 - prob_positive
        
        # Identify risk factors and mitigations using LLM
        risk_analysis = await self._analyze_risk_factors(scenario, risk_score_change)
        
        return RiskImpact(
            metric_name="Enterprise Risk Score",
            baseline_value=baseline,
            best_case=best_case,
            most_likely=most_likely,
            worst_case=worst_case,
            expected_value=expected,
            confidence_interval_95=(ci_lower, ci_upper),
            absolute_change=absolute_change,
            percentage_change=percentage_change,
            probability_positive=prob_positive,
            probability_negative=prob_negative,
            risk_factors=risk_analysis.get("factors", ["Operational risk"]),
            risk_score_change=risk_score_change,
            mitigation_strategies=risk_analysis.get("mitigations", ["Monitor closely"]),
        )
    
    async def _predict_customer_impact(
        self,
        scenario: ScenarioInput,
        simulation_data: Dict[str, np.ndarray]
    ) -> CustomerImpact:
        """Predict customer impact from simulation data"""
        
        churn_array = simulation_data["customer_churn"]
        satisfaction_array = simulation_data["customer_satisfaction"]
        
        baseline_churn = scenario.baseline_metrics.get("churn_rate", 0.05)
        baseline_satisfaction = scenario.baseline_metrics.get("satisfaction_score", 80)
        
        # Calculate churn statistics
        expected_churn = np.mean(churn_array)
        churn_change = expected_churn - baseline_churn
        
        # Calculate satisfaction statistics
        expected_satisfaction = np.mean(satisfaction_array)
        satisfaction_change = expected_satisfaction - baseline_satisfaction
        
        # Estimate acquisition and LTV changes
        acquisition_change = -churn_change * 0.5  # Inverse correlation
        ltv_change = satisfaction_change * 100  # $100 per satisfaction point
        
        # Use average for customer impact metric
        avg_baseline = (baseline_churn * 100 + baseline_satisfaction) / 2
        avg_expected = (expected_churn * 100 + expected_satisfaction) / 2
        
        return CustomerImpact(
            metric_name="Customer Health Score",
            baseline_value=avg_baseline,
            best_case=np.percentile(satisfaction_array, 90),
            most_likely=expected_satisfaction,
            worst_case=np.percentile(satisfaction_array, 10),
            expected_value=avg_expected,
            confidence_interval_95=(
                np.percentile(satisfaction_array, 2.5),
                np.percentile(satisfaction_array, 97.5)
            ),
            absolute_change=avg_expected - avg_baseline,
            percentage_change=((avg_expected - avg_baseline) / avg_baseline * 100) if avg_baseline > 0 else 0,
            probability_positive=np.sum(satisfaction_array > baseline_satisfaction) / len(satisfaction_array),
            probability_negative=np.sum(churn_array > baseline_churn) / len(churn_array),
            churn_rate_change=churn_change,
            satisfaction_score_change=satisfaction_change,
            acquisition_rate_change=acquisition_change,
            lifetime_value_change=ltv_change,
        )
    
    async def _generate_recommendations(
        self,
        scenario: ScenarioInput,
        revenue_impact: RevenueImpact,
        cost_impact: CostImpact,
        risk_impact: RiskImpact,
        customer_impact: CustomerImpact
    ) -> List[RecommendedAction]:
        """Generate recommended actions based on simulation results"""
        
        # Build prompt for LLM
        prompt = f"""
Based on the following simulation results, generate 3-5 recommended actions:

Scenario: {scenario.description}
Type: {scenario.scenario_type}

Revenue Impact: ${revenue_impact.expected_value:,.0f} ({revenue_impact.percentage_change:+.1f}%)
Cost Impact: ${cost_impact.expected_value:,.0f} ({cost_impact.percentage_change:+.1f}%)
Risk Score Change: {risk_impact.risk_score_change:+d}
Customer Churn Change: {customer_impact.churn_rate_change:+.2%}
Customer Satisfaction Change: {customer_impact.satisfaction_score_change:+.1f}

For each recommendation, provide:
- action_id: unique identifier
- title: concise title
- description: detailed description
- priority: 1-10
- rationale: why this action is recommended
- expected_benefit: USD value
- implementation_cost: USD value
- timeline_days: implementation timeline
- success_probability: 0.0-1.0

Output JSON with array of recommendations.
"""
        
        response = await self.llm_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a strategic business consultant. Generate actionable recommendations based on simulation results."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.4
        )
        
        import json
        rec_data = json.loads(response.choices[0].message.content)
        
        recommendations = []
        for rec in rec_data.get("recommendations", []):
            recommendations.append(RecommendedAction(**rec))
        
        return recommendations
    
    def _determine_overall_recommendation(
        self,
        net_impact: float,
        risk_impact: RiskImpact,
        recommendations: List[RecommendedAction]
    ) -> str:
        """Determine overall Go/No-Go recommendation"""
        
        # Decision logic
        if net_impact > 0 and risk_impact.risk_score_change <= 3:
            return "GO - Positive net impact with acceptable risk"
        elif net_impact > 0 and risk_impact.risk_score_change > 3:
            return "GO WITH CAUTION - Positive impact but elevated risk. Implement risk mitigations."
        elif net_impact < 0 and risk_impact.risk_score_change <= 3:
            return "CONDITIONAL - Negative impact but low risk. Consider if strategic value justifies."
        else:
            return "NO-GO - Negative impact with elevated risk. Not recommended."
    
    async def _extract_key_insights(
        self,
        scenario: ScenarioInput,
        revenue_impact: RevenueImpact,
        cost_impact: CostImpact,
        risk_impact: RiskImpact,
        customer_impact: CustomerImpact
    ) -> List[str]:
        """Extract key insights from simulation results"""
        
        insights = []
        
        # Revenue insight
        if abs(revenue_impact.percentage_change) > 5:
            insights.append(
                f"Revenue expected to change by {revenue_impact.percentage_change:+.1f}% "
                f"(${revenue_impact.absolute_change:+,.0f})"
            )
        
        # Cost insight
        if abs(cost_impact.percentage_change) > 5:
            insights.append(
                f"Costs expected to change by {cost_impact.percentage_change:+.1f}% "
                f"(${cost_impact.absolute_change:+,.0f})"
            )
        
        # Risk insight
        if abs(risk_impact.risk_score_change) >= 3:
            insights.append(
                f"Risk score expected to {'increase' if risk_impact.risk_score_change > 0 else 'decrease'} "
                f"by {abs(risk_impact.risk_score_change)} points"
            )
        
        # Customer insight
        if abs(customer_impact.churn_rate_change) > 0.01:
            insights.append(
                f"Customer churn expected to {'increase' if customer_impact.churn_rate_change > 0 else 'decrease'} "
                f"by {abs(customer_impact.churn_rate_change):.1%}"
            )
        
        # Net impact insight
        net_impact = revenue_impact.expected_value - cost_impact.expected_value
        insights.append(
            f"Net financial impact: ${net_impact:+,.0f} over {scenario.time_horizon_days} days"
        )
        
        return insights[:5]  # Top 5 insights
    
    def _document_assumptions(self, scenario: ScenarioInput) -> List[str]:
        """Document key assumptions made in simulation"""
        return [
            "Historical patterns continue to hold",
            "No major external market disruptions",
            "Normal distribution of outcomes",
            f"Simulation horizon: {scenario.time_horizon_days} days",
            "All other factors remain constant (ceteris paribus)",
        ]
    
    def _document_limitations(self, scenario: ScenarioInput, iterations: int) -> List[str]:
        """Document simulation limitations"""
        return [
            f"Based on {iterations} Monte Carlo iterations",
            "Assumes independence of variables (may have correlations)",
            "Limited by quality of historical data",
            "Does not account for black swan events",
            "Predictions become less accurate over longer time horizons",
        ]
    
    def _calculate_confidence_score(
        self,
        simulation_data: Dict[str, np.ndarray],
        historical_data: List[Dict[str, Any]],
        iterations: int
    ) -> float:
        """Calculate overall confidence score for simulation"""
        
        # Base confidence from iterations
        iteration_confidence = min(iterations / 10000, 1.0)
        
        # Historical data confidence
        if historical_data:
            avg_accuracy = np.mean([
                d.get("metadata", {}).get("prediction_accuracy", 0.7)
                for d in historical_data
            ])
            historical_confidence = avg_accuracy
        else:
            historical_confidence = 0.6  # Lower confidence without historical data
        
        # Variance confidence (lower variance = higher confidence)
        revenue_cv = np.std(simulation_data["revenue"]) / np.mean(simulation_data["revenue"])
        variance_confidence = 1.0 / (1.0 + revenue_cv)
        
        # Weighted average
        confidence = (
            0.4 * iteration_confidence +
            0.4 * historical_confidence +
            0.2 * variance_confidence
        )
        
        return round(confidence, 2)
    
    async def _analyze_affected_areas(
        self,
        scenario: ScenarioInput,
        impact_type: str
    ) -> Dict[str, List[str]]:
        """Use LLM to analyze affected business areas"""
        
        prompt = f"""
Analyze which business areas are affected by this scenario:

Scenario: {scenario.description}
Type: {scenario.scenario_type}
Impact Type: {impact_type}

Identify:
- For revenue: affected revenue streams and customer segments
- For cost: affected cost categories

Output JSON with appropriate keys.
"""
        
        response = await self.llm_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a business analyst."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        import json
        return json.loads(response.choices[0].message.content)
    
    async def _analyze_risk_factors(
        self,
        scenario: ScenarioInput,
        risk_score_change: int
    ) -> Dict[str, List[str]]:
        """Use LLM to analyze risk factors and mitigations"""
        
        prompt = f"""
Analyze risk factors and mitigation strategies:

Scenario: {scenario.description}
Risk Score Change: {risk_score_change:+d}

Identify:
- Key risk factors (3-5)
- Mitigation strategies (3-5)

Output JSON with 'factors' and 'mitigations' arrays.
"""
        
        response = await self.llm_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a risk management expert."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        import json
        return json.loads(response.choices[0].message.content)
    
    async def _store_simulation_in_memory(self, result: SimulationResult) -> None:
        """Store simulation result in ChromaDB for future learning"""
        
        memory = await get_chromadb_client()
        
        # Create text representation
        text = (
            f"Business Simulation: {result.scenario.description}. "
            f"Net impact: ${result.net_financial_impact:,.0f}. "
            f"Revenue: {result.revenue_impact.percentage_change:+.1f}%, "
            f"Cost: {result.cost_impact.percentage_change:+.1f}%, "
            f"Risk: {result.risk_impact.risk_score_change:+d}. "
            f"Recommendation: {result.overall_recommendation}"
        )
        
        await memory.add(
            collection="simulation_outcomes",
            documents=[{
                "id": result.simulation_id,
                "text": text,
                "metadata": {
                    "simulation_type": result.scenario.scenario_type,
                    "scenario_name": result.scenario.description[:100],
                    "iterations": result.iterations,
                    "net_impact": result.net_financial_impact,
                    "confidence_score": result.confidence_score,
                    "timestamp": result.timestamp,
                    "tags": ["simulation", result.scenario.scenario_type],
                }
            }]
        )


# Export
__all__ = [
    "BusinessSimulationAgent",
    "SimulationResult",
    "ScenarioInput",
    "ScenarioType",
]

# Made with Bob
