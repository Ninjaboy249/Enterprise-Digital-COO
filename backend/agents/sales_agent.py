"""
Sales Agent - Monitors and analyzes sales metrics
"""
from typing import Dict, List, Any
import numpy as np
from datetime import datetime, timedelta

from agents.base_agent import BaseAgent


class SalesAgent(BaseAgent):
    """
    Sales monitoring agent
    
    Monitors:
    - Revenue trends and forecasts
    - Sales pipeline health
    - Customer acquisition costs
    - Conversion rates
    - Regional performance
    - Product performance
    """
    
    def __init__(self):
        super().__init__(agent_name="sales_agent", domain="sales")
        
        # Sales-specific thresholds
        self.revenue_drop_threshold = 0.15  # 15% drop
        self.pipeline_stagnation_days = 30
        self.conversion_rate_threshold = 0.10  # 10% below average
        
    async def _analyze_metrics(
        self,
        metrics: Dict[str, Any],
        context: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze sales metrics
        """
        analysis = {
            "revenue_analysis": self._analyze_revenue(metrics),
            "pipeline_analysis": self._analyze_pipeline(metrics),
            "conversion_analysis": self._analyze_conversion(metrics),
            "regional_analysis": self._analyze_regional_performance(metrics),
            "product_analysis": self._analyze_product_performance(metrics),
            "trends": self._identify_trends(metrics, context)
        }
        
        return analysis
    
    async def _detect_anomalies(
        self,
        metrics: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Detect sales anomalies
        """
        anomalies = []
        
        # Revenue anomalies
        revenue_analysis = analysis.get("revenue_analysis", {})
        if revenue_analysis.get("drop_percentage", 0) > self.revenue_drop_threshold:
            anomalies.append({
                "type": "revenue_drop",
                "severity": "high",
                "description": f"Revenue dropped by {revenue_analysis['drop_percentage']:.1%}",
                "metric": "revenue",
                "expected_value": revenue_analysis.get("expected_revenue"),
                "actual_value": revenue_analysis.get("actual_revenue"),
                "confidence": 0.9
            })
        
        # Pipeline anomalies
        pipeline_analysis = analysis.get("pipeline_analysis", {})
        if pipeline_analysis.get("stagnant_deals", 0) > 5:
            anomalies.append({
                "type": "pipeline_stagnation",
                "severity": "medium",
                "description": f"{pipeline_analysis['stagnant_deals']} deals stagnant for over {self.pipeline_stagnation_days} days",
                "metric": "pipeline_health",
                "confidence": 0.85
            })
        
        # Conversion rate anomalies
        conversion_analysis = analysis.get("conversion_analysis", {})
        if conversion_analysis.get("below_threshold", False):
            anomalies.append({
                "type": "low_conversion_rate",
                "severity": "medium",
                "description": f"Conversion rate {conversion_analysis['current_rate']:.1%} is below threshold",
                "metric": "conversion_rate",
                "expected_value": conversion_analysis.get("average_rate"),
                "actual_value": conversion_analysis.get("current_rate"),
                "confidence": 0.8
            })
        
        # Regional anomalies
        regional_analysis = analysis.get("regional_analysis", {})
        for region, data in regional_analysis.items():
            if data.get("performance_drop", 0) > 0.20:  # 20% drop
                anomalies.append({
                    "type": "regional_underperformance",
                    "severity": "medium",
                    "description": f"Region {region} performance dropped by {data['performance_drop']:.1%}",
                    "metric": "regional_revenue",
                    "region": region,
                    "confidence": 0.75
                })
        
        return anomalies
    
    def _analyze_revenue(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze revenue trends"""
        current_revenue = metrics.get("revenue", 0)
        previous_revenue = metrics.get("previous_revenue", current_revenue)
        
        drop_percentage = 0
        if previous_revenue > 0:
            drop_percentage = (previous_revenue - current_revenue) / previous_revenue
        
        return {
            "actual_revenue": current_revenue,
            "expected_revenue": previous_revenue,
            "drop_percentage": drop_percentage,
            "trend": "declining" if drop_percentage > 0 else "growing"
        }
    
    def _analyze_pipeline(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sales pipeline health"""
        pipeline_data = metrics.get("pipeline", [])
        
        stagnant_deals = 0
        total_value = 0
        
        for deal in pipeline_data:
            age_days = deal.get("age_days", 0)
            if age_days > self.pipeline_stagnation_days:
                stagnant_deals += 1
            total_value += deal.get("value", 0)
        
        return {
            "total_deals": len(pipeline_data),
            "stagnant_deals": stagnant_deals,
            "total_pipeline_value": total_value,
            "average_deal_size": total_value / len(pipeline_data) if pipeline_data else 0,
            "health_score": 1 - (stagnant_deals / len(pipeline_data)) if pipeline_data else 1.0
        }
    
    def _analyze_conversion(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze conversion rates"""
        current_rate = metrics.get("conversion_rate", 0)
        average_rate = metrics.get("average_conversion_rate", current_rate)
        
        below_threshold = (average_rate - current_rate) > self.conversion_rate_threshold
        
        return {
            "current_rate": current_rate,
            "average_rate": average_rate,
            "below_threshold": below_threshold,
            "variance": current_rate - average_rate
        }
    
    def _analyze_regional_performance(
        self,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze performance by region"""
        regional_data = metrics.get("regional_performance", {})
        
        analysis = {}
        for region, data in regional_data.items():
            current = data.get("current_revenue", 0)
            previous = data.get("previous_revenue", current)
            
            performance_drop = 0
            if previous > 0:
                performance_drop = (previous - current) / previous
            
            analysis[region] = {
                "current_revenue": current,
                "previous_revenue": previous,
                "performance_drop": performance_drop,
                "trend": "declining" if performance_drop > 0 else "growing"
            }
        
        return analysis
    
    def _analyze_product_performance(
        self,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze performance by product"""
        product_data = metrics.get("product_performance", {})
        
        analysis = {}
        for product, data in product_data.items():
            analysis[product] = {
                "revenue": data.get("revenue", 0),
                "units_sold": data.get("units_sold", 0),
                "growth_rate": data.get("growth_rate", 0)
            }
        
        return analysis
    
    def _identify_trends(
        self,
        metrics: Dict[str, Any],
        context: List[Dict]
    ) -> List[str]:
        """Identify sales trends from historical context"""
        trends = []
        
        # Simple trend identification
        revenue = metrics.get("revenue", 0)
        previous_revenue = metrics.get("previous_revenue", revenue)
        
        if revenue > previous_revenue * 1.1:
            trends.append("Strong revenue growth")
        elif revenue < previous_revenue * 0.9:
            trends.append("Revenue decline")
        else:
            trends.append("Stable revenue")
        
        # Pipeline trends
        pipeline_value = metrics.get("pipeline_value", 0)
        if pipeline_value > metrics.get("previous_pipeline_value", pipeline_value):
            trends.append("Growing pipeline")
        
        return trends


# Create singleton instance
sales_agent = SalesAgent()

# Made with Bob
