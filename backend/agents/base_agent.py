"""
Base Agent class for all domain-specific agents
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from openai import AsyncOpenAI

from config import settings
from memory.chromadb_client import get_chromadb_client
from database.session import get_db

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all monitoring agents
    
    Each agent is responsible for:
    1. Analyzing domain-specific metrics
    2. Detecting anomalies
    3. Generating insights
    4. Storing experiences in memory
    """
    
    def __init__(self, agent_name: str, domain: str):
        self.agent_name = agent_name
        self.domain = domain
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.logger = logging.getLogger(f"{__name__}.{agent_name}")
        
    async def analyze(
        self,
        metrics: Dict[str, Any],
        context: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Main analysis method - orchestrates the analysis workflow
        
        Args:
            metrics: Current metrics data
            context: Historical context from memory
            
        Returns:
            Analysis results including insights and anomalies
        """
        self.logger.info(f"Starting analysis for {self.domain}")
        
        try:
            # Step 1: Retrieve relevant memory
            if context is None:
                context = await self._retrieve_memory(metrics)
            
            # Step 2: Perform domain-specific analysis
            analysis_result = await self._analyze_metrics(metrics, context)
            
            # Step 3: Detect anomalies
            anomalies = await self._detect_anomalies(metrics, analysis_result)
            
            # Step 4: Generate insights
            insights = await self._generate_insights(
                metrics,
                analysis_result,
                anomalies
            )
            
            # Step 5: Store experience in memory
            await self._store_memory(metrics, analysis_result, insights)
            
            # Compile results
            result = {
                "agent_name": self.agent_name,
                "domain": self.domain,
                "timestamp": datetime.utcnow().isoformat(),
                "metrics_analyzed": len(metrics),
                "analysis": analysis_result,
                "anomalies": anomalies,
                "insights": insights,
                "confidence_score": self._calculate_confidence(analysis_result)
            }
            
            self.logger.info(
                f"Analysis complete: {len(anomalies)} anomalies detected"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            raise
    
    @abstractmethod
    async def _analyze_metrics(
        self,
        metrics: Dict[str, Any],
        context: List[Dict]
    ) -> Dict[str, Any]:
        """
        Domain-specific metric analysis
        Must be implemented by each agent
        """
        pass
    
    @abstractmethod
    async def _detect_anomalies(
        self,
        metrics: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Domain-specific anomaly detection
        Must be implemented by each agent
        """
        pass
    
    async def _retrieve_memory(
        self,
        metrics: Dict[str, Any]
    ) -> List[Dict]:
        """
        Retrieve relevant historical context from ChromaDB
        """
        try:
            chroma_client = await get_chromadb_client()
            
            # Create query text from metrics
            query_text = self._create_query_text(metrics)
            
            # Query agent memory collection
            results = await chroma_client.query(
                collection_name="agent_memory",
                query_texts=[query_text],
                n_results=settings.MEMORY_MAX_RESULTS,
                where={
                    "agent_name": self.agent_name,
                    "domain": self.domain
                }
            )
            
            return results.get("documents", [[]])[0]
            
        except Exception as e:
            self.logger.warning(f"Memory retrieval failed: {str(e)}")
            return []
    
    async def _store_memory(
        self,
        metrics: Dict[str, Any],
        analysis: Dict[str, Any],
        insights: List[str]
    ) -> None:
        """
        Store analysis experience in ChromaDB for future reference
        """
        try:
            chroma_client = await get_chromadb_client()
            
            # Create memory document
            memory_text = self._create_memory_text(metrics, analysis, insights)
            
            # Store in agent memory collection
            await chroma_client.add(
                collection_name="agent_memory",
                documents=[memory_text],
                metadatas=[{
                    "agent_name": self.agent_name,
                    "domain": self.domain,
                    "timestamp": datetime.utcnow().isoformat(),
                    "has_anomalies": len(analysis.get("anomalies", [])) > 0
                }],
                ids=[f"{self.agent_name}_{datetime.utcnow().timestamp()}"]
            )
            
        except Exception as e:
            self.logger.warning(f"Memory storage failed: {str(e)}")
    
    async def _generate_insights(
        self,
        metrics: Dict[str, Any],
        analysis: Dict[str, Any],
        anomalies: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate natural language insights using GPT-4
        """
        try:
            prompt = self._create_insight_prompt(metrics, analysis, anomalies)
            
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert {self.domain} analyst. Provide concise, actionable insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS
            )
            
            insights_text = response.choices[0].message.content
            
            # Parse insights into list
            insights = [
                line.strip("- ").strip()
                for line in insights_text.split("\n")
                if line.strip() and line.strip().startswith("-")
            ]
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Insight generation failed: {str(e)}")
            return ["Analysis completed but insight generation failed"]
    
    def _create_query_text(self, metrics: Dict[str, Any]) -> str:
        """Create query text for memory retrieval"""
        return f"Domain: {self.domain}, Metrics: {str(metrics)[:200]}"
    
    def _create_memory_text(
        self,
        metrics: Dict[str, Any],
        analysis: Dict[str, Any],
        insights: List[str]
    ) -> str:
        """Create memory text for storage"""
        return f"""
        Agent: {self.agent_name}
        Domain: {self.domain}
        Timestamp: {datetime.utcnow().isoformat()}
        Metrics Summary: {str(metrics)[:200]}
        Analysis: {str(analysis)[:300]}
        Insights: {', '.join(insights[:3])}
        """
    
    def _create_insight_prompt(
        self,
        metrics: Dict[str, Any],
        analysis: Dict[str, Any],
        anomalies: List[Dict[str, Any]]
    ) -> str:
        """Create prompt for insight generation"""
        return f"""
        Analyze the following {self.domain} data and provide 3-5 key insights:
        
        Metrics: {metrics}
        
        Analysis Results: {analysis}
        
        Anomalies Detected: {len(anomalies)}
        {anomalies if anomalies else "No anomalies detected"}
        
        Provide insights as bullet points focusing on:
        1. Key trends and patterns
        2. Potential risks or opportunities
        3. Recommended actions
        """
    
    def _calculate_confidence(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate confidence score for the analysis
        Based on data quality, completeness, and consistency
        """
        # Simple confidence calculation - can be enhanced
        base_confidence = 0.8
        
        # Adjust based on data completeness
        if analysis.get("data_quality", "good") == "poor":
            base_confidence -= 0.2
        
        return max(0.0, min(1.0, base_confidence))
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_name": self.agent_name,
            "domain": self.domain,
            "status": "active",
            "last_execution": datetime.utcnow().isoformat()
        }

# Made with Bob
