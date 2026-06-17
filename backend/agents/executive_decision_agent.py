"""
Executive Decision Agent
Acts as a Fortune 500 COO, synthesizing inputs from all domain agents
and generating strategic executive decisions with ROI estimates
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from backend.agents.base_agent import BaseAgent
from backend.memory.chromadb_client import get_chromadb_client

logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models for Structured Output
# ============================================================================

class Evidence(BaseModel):
    """Supporting evidence for a finding"""
    source: str = Field(description="Source agent or data source")
    finding: str = Field(description="Key finding or observation")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    impact: str = Field(description="Business impact: low, medium, high, critical")


class RootCause(BaseModel):
    """Identified root cause"""
    cause: str = Field(description="Root cause description")
    category: str = Field(description="Category: process, people, technology, external")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in root cause")
    contributing_factors: List[str] = Field(description="Contributing factors")
    evidence: List[Evidence] = Field(description="Supporting evidence")


class BusinessRisk(BaseModel):
    """Prioritized business risk"""
    risk_id: str = Field(description="Unique risk identifier")
    description: str = Field(description="Risk description")
    category: str = Field(description="Risk category")
    likelihood: int = Field(ge=1, le=5, description="Likelihood score 1-5")
    impact: int = Field(ge=1, le=5, description="Impact score 1-5")
    risk_score: int = Field(description="Calculated risk score (likelihood × impact)")
    priority: int = Field(ge=1, le=10, description="Priority ranking 1-10")
    financial_exposure: float = Field(description="Estimated financial exposure in USD")
    mitigation_status: str = Field(description="Status: unmitigated, in_progress, mitigated")


class ActionRecommendation(BaseModel):
    """Recommended action with ROI estimate"""
    action_id: str = Field(description="Unique action identifier")
    title: str = Field(description="Action title")
    description: str = Field(description="Detailed action description")
    category: str = Field(description="Category: immediate, short_term, long_term")
    priority: int = Field(ge=1, le=10, description="Priority ranking 1-10")
    estimated_cost: float = Field(description="Estimated implementation cost in USD")
    estimated_benefit: float = Field(description="Estimated annual benefit in USD")
    estimated_roi: float = Field(description="Estimated ROI as multiple (benefit/cost)")
    timeline_days: int = Field(description="Implementation timeline in days")
    dependencies: List[str] = Field(description="Dependencies on other actions")
    risks: List[str] = Field(description="Implementation risks")
    success_metrics: List[str] = Field(description="Success measurement criteria")


class ExecutiveSummary(BaseModel):
    """Executive summary of the situation"""
    situation: str = Field(description="Current situation overview")
    key_findings: List[str] = Field(description="Top 3-5 key findings")
    business_impact: str = Field(description="Overall business impact assessment")
    urgency: str = Field(description="Urgency level: low, medium, high, critical")
    recommended_approach: str = Field(description="Recommended strategic approach")


class ExecutiveDecision(BaseModel):
    """Complete executive decision output"""
    decision_id: str = Field(description="Unique decision identifier")
    timestamp: str = Field(description="Decision timestamp ISO 8601")
    
    # Executive Summary
    executive_summary: ExecutiveSummary = Field(description="Executive summary")
    
    # Analysis
    root_causes: List[RootCause] = Field(description="Identified root causes")
    business_risks: List[BusinessRisk] = Field(description="Prioritized business risks")
    
    # Recommendations
    recommendations: List[ActionRecommendation] = Field(description="Recommended actions")
    
    # Confidence & Evidence
    overall_confidence: float = Field(ge=0.0, le=1.0, description="Overall confidence score")
    evidence_summary: List[Evidence] = Field(description="Key supporting evidence")
    
    # Metadata
    agents_consulted: List[str] = Field(description="List of agents consulted")
    analysis_duration_seconds: float = Field(description="Analysis duration")
    requires_approval: bool = Field(description="Requires human approval")


# ============================================================================
# Executive Decision Agent
# ============================================================================

class ExecutiveDecisionAgent(BaseAgent):
    """
    Executive Decision Agent - Acts as Fortune 500 COO
    
    Responsibilities:
    1. Correlate findings from all domain agents
    2. Identify root causes using multiple analysis methods
    3. Prioritize business risks using risk scoring
    4. Recommend actions with ROI estimates
    5. Generate executive summaries
    6. Provide confidence scores and evidence
    """
    
    def __init__(self):
        super().__init__(
            agent_name="executive_decision_agent",
            agent_type="executive",
            domain="enterprise"
        )
        
        # Risk scoring matrix
        self.risk_matrix = {
            (1, 1): 1, (1, 2): 2, (1, 3): 3, (1, 4): 4, (1, 5): 5,
            (2, 1): 2, (2, 2): 4, (2, 3): 6, (2, 4): 8, (2, 5): 10,
            (3, 1): 3, (3, 2): 6, (3, 3): 9, (3, 4): 12, (3, 5): 15,
            (4, 1): 4, (4, 2): 8, (4, 3): 12, (4, 4): 16, (4, 5): 20,
            (5, 1): 5, (5, 2): 10, (5, 3): 15, (5, 4): 20, (5, 5): 25,
        }
    
    async def analyze(
        self,
        agent_inputs: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutiveDecision:
        """
        Analyze inputs from all domain agents and generate executive decision
        
        Args:
            agent_inputs: Dictionary mapping agent names to their analyses
            context: Additional context (workflow_id, trigger, etc.)
            
        Returns:
            ExecutiveDecision with complete analysis and recommendations
        """
        start_time = datetime.utcnow()
        
        logger.info(f"Executive Decision Agent analyzing inputs from {len(agent_inputs)} agents")
        
        # Step 1: Retrieve relevant historical context
        historical_context = await self._retrieve_historical_context(agent_inputs, context)
        
        # Step 2: Correlate findings across agents
        correlated_findings = await self._correlate_findings(agent_inputs)
        
        # Step 3: Identify root causes
        root_causes = await self._identify_root_causes(correlated_findings, historical_context)
        
        # Step 4: Prioritize business risks
        business_risks = await self._prioritize_risks(correlated_findings, root_causes)
        
        # Step 5: Generate action recommendations with ROI
        recommendations = await self._generate_recommendations(
            root_causes, business_risks, historical_context
        )
        
        # Step 6: Create executive summary
        executive_summary = await self._create_executive_summary(
            correlated_findings, root_causes, business_risks, recommendations
        )
        
        # Step 7: Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(
            agent_inputs, root_causes, recommendations
        )
        
        # Step 8: Compile evidence
        evidence_summary = self._compile_evidence(agent_inputs, correlated_findings)
        
        # Step 9: Determine if human approval required
        requires_approval = self._requires_human_approval(business_risks, recommendations)
        
        # Calculate analysis duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Create decision
        decision = ExecutiveDecision(
            decision_id=f"exec_decision_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow().isoformat(),
            executive_summary=executive_summary,
            root_causes=root_causes,
            business_risks=business_risks,
            recommendations=recommendations,
            overall_confidence=overall_confidence,
            evidence_summary=evidence_summary,
            agents_consulted=list(agent_inputs.keys()),
            analysis_duration_seconds=duration,
            requires_approval=requires_approval
        )
        
        # Store decision in memory for future learning
        await self._store_decision_in_memory(decision, context)
        
        logger.info(
            f"Executive decision generated: {len(root_causes)} root causes, "
            f"{len(business_risks)} risks, {len(recommendations)} recommendations"
        )
        
        return decision
    
    async def _retrieve_historical_context(
        self,
        agent_inputs: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant historical decisions and incidents"""
        memory = await get_chromadb_client()
        
        # Build search query from agent inputs
        query_parts = []
        for agent_name, analysis in agent_inputs.items():
            if isinstance(analysis, dict) and "summary" in analysis:
                query_parts.append(analysis["summary"])
        
        query = " ".join(query_parts[:3])  # Use top 3 summaries
        
        # Search multiple collections
        results = await memory.search_multi(
            collections=["agent_decisions", "root_cause_analyses", "executive_recommendations"],
            query=query,
            filters={"outcome": "successful"},
            top_k=3
        )
        
        # Flatten results
        historical_context = []
        for collection, docs in results.items():
            historical_context.extend(docs)
        
        return historical_context
    
    async def _correlate_findings(
        self,
        agent_inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Correlate findings across all domain agents"""
        
        # Use OpenAI to correlate findings
        prompt = self._build_correlation_prompt(agent_inputs)
        
        response = await self.llm_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Fortune 500 COO analyzing reports from domain experts. "
                        "Correlate findings across domains to identify patterns, "
                        "dependencies, and systemic issues. Focus on business impact."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        import json
        correlated = json.loads(response.choices[0].message.content)
        
        return correlated
    
    async def _identify_root_causes(
        self,
        correlated_findings: Dict[str, Any],
        historical_context: List[Dict[str, Any]]
    ) -> List[RootCause]:
        """Identify root causes using multiple analysis methods"""
        
        # Build prompt with historical context
        prompt = self._build_root_cause_prompt(correlated_findings, historical_context)
        
        response = await self.llm_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in root cause analysis. Use 5 Whys, "
                        "Fishbone diagrams, and Pareto analysis to identify root causes. "
                        "Distinguish between symptoms and actual root causes. "
                        "Provide confidence scores and supporting evidence."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        import json
        rca_data = json.loads(response.choices[0].message.content)
        
        # Parse into RootCause objects
        root_causes = []
        for rc in rca_data.get("root_causes", []):
            root_causes.append(RootCause(**rc))
        
        return root_causes
    
    async def _prioritize_risks(
        self,
        correlated_findings: Dict[str, Any],
        root_causes: List[RootCause]
    ) -> List[BusinessRisk]:
        """Prioritize business risks using risk scoring matrix"""
        
        prompt = self._build_risk_assessment_prompt(correlated_findings, root_causes)
        
        response = await self.llm_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a risk management expert. Assess business risks using "
                        "likelihood (1-5) and impact (1-5) scoring. Calculate risk scores "
                        "and prioritize. Estimate financial exposure. Consider both "
                        "immediate and long-term risks."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        import json
        risk_data = json.loads(response.choices[0].message.content)
        
        # Parse and calculate risk scores
        business_risks = []
        for risk in risk_data.get("risks", []):
            likelihood = risk["likelihood"]
            impact = risk["impact"]
            risk_score = self.risk_matrix.get((likelihood, impact), likelihood * impact)
            
            business_risks.append(BusinessRisk(
                **risk,
                risk_score=risk_score
            ))
        
        # Sort by risk score (descending)
        business_risks.sort(key=lambda r: r.risk_score, reverse=True)
        
        # Assign priority rankings
        for i, risk in enumerate(business_risks, 1):
            risk.priority = min(i, 10)  # Cap at 10
        
        return business_risks
    
    async def _generate_recommendations(
        self,
        root_causes: List[RootCause],
        business_risks: List[BusinessRisk],
        historical_context: List[Dict[str, Any]]
    ) -> List[ActionRecommendation]:
        """Generate action recommendations with ROI estimates"""
        
        prompt = self._build_recommendations_prompt(root_causes, business_risks, historical_context)
        
        response = await self.llm_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strategic business consultant. Generate actionable "
                        "recommendations with realistic ROI estimates. Categorize by "
                        "timeframe (immediate, short-term, long-term). Identify dependencies "
                        "and risks. Provide success metrics. Base estimates on industry "
                        "benchmarks and historical data."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.4
        )
        
        import json
        rec_data = json.loads(response.choices[0].message.content)
        
        # Parse into ActionRecommendation objects
        recommendations = []
        for rec in rec_data.get("recommendations", []):
            recommendations.append(ActionRecommendation(**rec))
        
        # Sort by priority
        recommendations.sort(key=lambda r: r.priority)
        
        return recommendations
    
    async def _create_executive_summary(
        self,
        correlated_findings: Dict[str, Any],
        root_causes: List[RootCause],
        business_risks: List[BusinessRisk],
        recommendations: List[ActionRecommendation]
    ) -> ExecutiveSummary:
        """Create executive summary for C-suite"""
        
        prompt = self._build_executive_summary_prompt(
            correlated_findings, root_causes, business_risks, recommendations
        )
        
        response = await self.llm_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are writing for C-suite executives. Be concise, strategic, "
                        "and action-oriented. Focus on business impact and ROI. "
                        "Use executive language. Limit to 3-5 key findings."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.4
        )
        
        import json
        summary_data = json.loads(response.choices[0].message.content)
        
        return ExecutiveSummary(**summary_data)
    
    def _calculate_overall_confidence(
        self,
        agent_inputs: Dict[str, Any],
        root_causes: List[RootCause],
        recommendations: List[ActionRecommendation]
    ) -> float:
        """Calculate overall confidence score"""
        
        # Agent confidence scores
        agent_confidences = []
        for agent_name, analysis in agent_inputs.items():
            if isinstance(analysis, dict) and "confidence_score" in analysis:
                agent_confidences.append(analysis["confidence_score"])
        
        # Root cause confidence scores
        rca_confidences = [rc.confidence for rc in root_causes]
        
        # Combine with weights
        if agent_confidences and rca_confidences:
            overall = (
                0.6 * (sum(agent_confidences) / len(agent_confidences)) +
                0.4 * (sum(rca_confidences) / len(rca_confidences))
            )
        elif agent_confidences:
            overall = sum(agent_confidences) / len(agent_confidences)
        else:
            overall = 0.7  # Default moderate confidence
        
        return round(overall, 2)
    
    def _compile_evidence(
        self,
        agent_inputs: Dict[str, Any],
        correlated_findings: Dict[str, Any]
    ) -> List[Evidence]:
        """Compile key supporting evidence"""
        
        evidence_list = []
        
        # Extract evidence from agent inputs
        for agent_name, analysis in agent_inputs.items():
            if isinstance(analysis, dict):
                evidence_list.append(Evidence(
                    source=agent_name,
                    finding=analysis.get("summary", "No summary provided"),
                    confidence=analysis.get("confidence_score", 0.7),
                    impact=analysis.get("severity", "medium")
                ))
        
        # Limit to top 5 most impactful
        evidence_list.sort(key=lambda e: e.confidence, reverse=True)
        return evidence_list[:5]
    
    def _requires_human_approval(
        self,
        business_risks: List[BusinessRisk],
        recommendations: List[ActionRecommendation]
    ) -> bool:
        """Determine if human approval is required"""
        
        # Require approval if:
        # 1. Any critical risk (score >= 20)
        # 2. High-cost recommendation (> $500K)
        # 3. High-priority recommendation (priority <= 2)
        
        for risk in business_risks:
            if risk.risk_score >= 20:
                return True
        
        for rec in recommendations:
            if rec.estimated_cost > 500000 or rec.priority <= 2:
                return True
        
        return False
    
    async def _store_decision_in_memory(
        self,
        decision: ExecutiveDecision,
        context: Optional[Dict[str, Any]]
    ) -> None:
        """Store decision in ChromaDB for future learning"""
        
        memory = await get_chromadb_client()
        
        # Create text representation
        text = (
            f"Executive Decision: {decision.executive_summary.situation}. "
            f"Root causes: {', '.join([rc.cause for rc in decision.root_causes])}. "
            f"Top recommendations: {', '.join([rec.title for rec in decision.recommendations[:3]])}. "
            f"Confidence: {decision.overall_confidence:.0%}"
        )
        
        # Store in memory
        await memory.add(
            collection="agent_decisions",
            documents=[{
                "id": decision.decision_id,
                "text": text,
                "metadata": {
                    "agent_name": self.agent_name,
                    "decision_type": "executive_decision",
                    "domain": "enterprise",
                    "confidence_score": decision.overall_confidence,
                    "timestamp": decision.timestamp,
                    "workflow_id": context.get("workflow_id") if context else None,
                    "requires_approval": decision.requires_approval,
                    "num_recommendations": len(decision.recommendations),
                    "tags": ["executive", "strategic", "multi_domain"],
                }
            }]
        )
    
    # ========================================================================
    # Prompt Building Methods
    # ========================================================================
    
    def _build_correlation_prompt(self, agent_inputs: Dict[str, Any]) -> str:
        """Build prompt for correlating findings"""
        return f"""
Analyze the following reports from domain experts and correlate findings:

{self._format_agent_inputs(agent_inputs)}

Identify:
1. Common patterns across domains
2. Dependencies and cascading effects
3. Systemic issues vs isolated incidents
4. Business impact correlations

Output JSON with: patterns, dependencies, systemic_issues, impact_analysis
"""
    
    def _build_root_cause_prompt(
        self,
        correlated_findings: Dict[str, Any],
        historical_context: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for root cause analysis"""
        return f"""
Perform root cause analysis on the following correlated findings:

{correlated_findings}

Historical context from similar situations:
{self._format_historical_context(historical_context)}

Use 5 Whys and Fishbone analysis to identify root causes.

Output JSON with array of root_causes, each containing:
- cause: string
- category: process|people|technology|external
- confidence: float 0-1
- contributing_factors: array of strings
- evidence: array of {{source, finding, confidence, impact}}
"""
    
    def _build_risk_assessment_prompt(
        self,
        correlated_findings: Dict[str, Any],
        root_causes: List[RootCause]
    ) -> str:
        """Build prompt for risk assessment"""
        return f"""
Assess business risks based on:

Correlated Findings:
{correlated_findings}

Root Causes:
{[{"cause": rc.cause, "category": rc.category} for rc in root_causes]}

For each risk, provide:
- risk_id: unique identifier
- description: clear risk description
- category: operational|financial|strategic|compliance|reputational
- likelihood: 1-5 (1=rare, 5=almost certain)
- impact: 1-5 (1=negligible, 5=catastrophic)
- priority: will be calculated
- financial_exposure: estimated USD amount
- mitigation_status: unmitigated|in_progress|mitigated

Output JSON with array of risks.
"""
    
    def _build_recommendations_prompt(
        self,
        root_causes: List[RootCause],
        business_risks: List[BusinessRisk],
        historical_context: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for generating recommendations"""
        return f"""
Generate actionable recommendations based on:

Root Causes:
{[{"cause": rc.cause, "confidence": rc.confidence} for rc in root_causes]}

Business Risks:
{[{"description": r.description, "risk_score": r.risk_score, "financial_exposure": r.financial_exposure} for r in business_risks[:5]]}

Historical Success:
{self._format_historical_context(historical_context)}

For each recommendation, provide:
- action_id: unique identifier
- title: concise title
- description: detailed description
- category: immediate|short_term|long_term
- priority: 1-10
- estimated_cost: USD
- estimated_benefit: annual USD
- estimated_roi: benefit/cost multiple
- timeline_days: implementation timeline
- dependencies: array of action_ids or descriptions
- risks: array of implementation risks
- success_metrics: array of KPIs

Output JSON with array of recommendations.
"""
    
    def _build_executive_summary_prompt(
        self,
        correlated_findings: Dict[str, Any],
        root_causes: List[RootCause],
        business_risks: List[BusinessRisk],
        recommendations: List[ActionRecommendation]
    ) -> str:
        """Build prompt for executive summary"""
        return f"""
Create an executive summary for C-suite based on:

Findings: {correlated_findings}
Root Causes: {len(root_causes)} identified
Business Risks: {len(business_risks)} prioritized
Recommendations: {len(recommendations)} actions proposed

Output JSON with:
- situation: 2-3 sentence overview
- key_findings: array of 3-5 most critical findings
- business_impact: overall impact assessment
- urgency: low|medium|high|critical
- recommended_approach: strategic approach summary
"""
    
    def _format_agent_inputs(self, agent_inputs: Dict[str, Any]) -> str:
        """Format agent inputs for prompts"""
        formatted = []
        for agent_name, analysis in agent_inputs.items():
            formatted.append(f"\n{agent_name.upper()}:")
            if isinstance(analysis, dict):
                for key, value in analysis.items():
                    formatted.append(f"  {key}: {value}")
            else:
                formatted.append(f"  {analysis}")
        return "\n".join(formatted)
    
    def _format_historical_context(self, historical_context: List[Dict[str, Any]]) -> str:
        """Format historical context for prompts"""
        if not historical_context:
            return "No relevant historical context found."
        
        formatted = []
        for i, ctx in enumerate(historical_context[:3], 1):
            formatted.append(f"\n{i}. {ctx.get('text', 'No text')[:200]}...")
        return "\n".join(formatted)


# Export
__all__ = ["ExecutiveDecisionAgent", "ExecutiveDecision"]

# Made with Bob
