"""
EXPLAINABLE INTELLIGENCE ORCHESTRATOR (DEPRECATED - USE intelligence_engine.py)
Coordinates the evidence-based recommendation pipeline

For new code, use:
    from agents.intelligence.intelligence_engine import SustainabilityIntelligenceEngine

Pipeline:
1. Insight Generation Agent → Generate factual observations with evidence
2. Optimization Discovery Agent → Find opportunities backed by evidence
3. Constraint Validation Agent → Validate against org profile
4. AI Recommendation Agent → Generate explainable recommendations

ALL DETERMINISTIC EXCEPT FINAL EXPLANATION (optional Gemini)
"""
import logging
from typing import Dict, List, Optional
import time

# Updated imports for new structure
from .insight_generation_agent import InsightGenerationAgent
from .optimization_discovery_agent import OptimizationDiscoveryAgent
from .intelligence.constraint_validation_agent import ConstraintValidationAgent
from .ai_recommendation_agent import AIRecommendationAgent

logger = logging.getLogger(__name__)
logger.warning("DEPRECATED: Using old explainable_intelligence_orchestrator.py. Please migrate to intelligence_engine.py")


class ExplainableIntelligenceOrchestrator:
    """
    Orchestrates the explainable intelligence pipeline
    
    Key Principles:
    - Every recommendation backed by evidence
    - No generic suggestions
    - Clear root cause analysis
    - Transparent confidence scoring
    """
    
    def __init__(self):
        self.insight_agent = InsightGenerationAgent()
        self.discovery_agent = OptimizationDiscoveryAgent()
        self.validation_agent = ConstraintValidationAgent()
        self.recommendation_agent = AIRecommendationAgent()
        
        self.pipeline_runs = 0
    
    async def generate_intelligence(
        self,
        emission_records: List[Dict],
        analytics: Dict,
        org_profile: Optional[Dict] = None,
        use_ai: bool = False
    ) -> Dict:
        """
        Generate explainable sustainability intelligence
        
        Args:
            emission_records: Calculated emissions from EmissionCalculationAgent
            analytics: Analytics from AnalyticsAgent
            org_profile: Organization profile (optional)
            use_ai: Whether to use Gemini for explanations (default: False)
        
        Returns:
            Complete explainable intelligence package
        """
        start_time = time.time()
        
        logger.info("="*80)
        logger.info("EXPLAINABLE INTELLIGENCE PIPELINE")
        logger.info("="*80)
        
        # STAGE 1: Generate Evidence-Based Insights
        stage_start = time.time()
        logger.info("[Stage 1/4] Generating Evidence-Based Insights...")
        
        insights = self.insight_agent.generate_insights(
            emission_records=emission_records,
            analytics=analytics
        )
        
        stage_duration = time.time() - stage_start
        logger.info(f"✓ Stage 1 Complete: {len(insights)} insights generated ({stage_duration:.2f}s)")
        
        if not insights:
            logger.warning("No insights generated - insufficient data or no patterns found")
            return self._empty_response()
        
        # STAGE 2: Discover Optimization Opportunities
        stage_start = time.time()
        logger.info("[Stage 2/4] Discovering Optimization Opportunities...")
        
        opportunities = self.discovery_agent.discover_opportunities(
            insights=insights,
            emission_records=emission_records
        )
        
        stage_duration = time.time() - stage_start
        logger.info(f"✓ Stage 2 Complete: {len(opportunities)} opportunities discovered ({stage_duration:.2f}s)")
        
        if not opportunities:
            logger.warning("No optimization opportunities discovered")
            return {
                'insights': insights,
                'opportunities': [],
                'recommendations': [],
                'summary': self._generate_summary(insights, [], []),
                'pipeline_stats': self._get_pipeline_stats(time.time() - start_time)
            }
        
        # STAGE 3: Validate Against Constraints
        stage_start = time.time()
        logger.info("[Stage 3/4] Validating Against Organization Constraints...")
        
        validated_opportunities = self.validation_agent.validate_opportunities(
            opportunities=opportunities,
            org_profile=org_profile
        )
        
        stage_duration = time.time() - stage_start
        logger.info(f"✓ Stage 3 Complete: {len(validated_opportunities)} opportunities validated ({stage_duration:.2f}s)")
        
        # STAGE 4: Generate Explainable Recommendations
        stage_start = time.time()
        logger.info(f"[Stage 4/4] Generating Explainable Recommendations (AI: {use_ai})...")
        
        recommendations = await self.recommendation_agent.generate_recommendations(
            opportunities=validated_opportunities,
            org_profile=org_profile,
            use_ai=use_ai
        )
        
        stage_duration = time.time() - stage_start
        logger.info(f"✓ Stage 4 Complete: {len(recommendations)} recommendations generated ({stage_duration:.2f}s)")
        
        # Calculate totals
        total_time = time.time() - start_time
        self.pipeline_runs += 1
        
        logger.info("="*80)
        logger.info(f"✓✓✓ EXPLAINABLE INTELLIGENCE COMPLETE ({total_time:.2f}s) ✓✓✓")
        logger.info(f"  Insights: {len(insights)}")
        logger.info(f"  Opportunities: {len(opportunities)}")
        logger.info(f"  Validated: {len(validated_opportunities)}")
        logger.info(f"  Recommendations: {len(recommendations)}")
        logger.info("="*80)
        
        return {
            'insights': insights,
            'opportunities': validated_opportunities,
            'recommendations': recommendations,
            'summary': self._generate_summary(insights, validated_opportunities, recommendations),
            'pipeline_stats': self._get_pipeline_stats(total_time)
        }
    
    def _generate_summary(self, insights: List[Dict], opportunities: List[Dict], recommendations: List[Dict]) -> Dict:
        """Generate executive summary"""
        
        if not recommendations:
            return {
                'total_insights': len(insights),
                'total_opportunities': len(opportunities),
                'total_recommendations': 0,
                'total_potential_reduction_kg': 0,
                'high_priority_count': 0,
                'categories': []
            }
        
        total_reduction = sum(r.get('expected_reduction_kg', 0) for r in recommendations)
        high_priority = sum(1 for r in recommendations if r.get('priority', 99) <= 2)
        
        categories = list(set(r.get('category', 'unknown') for r in recommendations))
        
        # Find top recommendation
        top_rec = max(recommendations, key=lambda x: x.get('expected_reduction_kg', 0))
        
        return {
            'total_insights': len(insights),
            'total_opportunities': len(opportunities),
            'total_recommendations': len(recommendations),
            'total_potential_reduction_kg': round(total_reduction, 4),
            'high_priority_count': high_priority,
            'categories': categories,
            'top_recommendation': {
                'title': top_rec.get('title'),
                'reduction_kg': top_rec.get('expected_reduction_kg'),
                'category': top_rec.get('category')
            }
        }
    
    def _get_pipeline_stats(self, total_time: float) -> Dict:
        """Get pipeline statistics"""
        return {
            'total_time_seconds': round(total_time, 2),
            'insight_generation': self.insight_agent.get_stats(),
            'optimization_discovery': self.discovery_agent.get_stats(),
            'constraint_validation': self.validation_agent.get_validation_stats(),
            'ai_recommendations': self.recommendation_agent.get_stats(),
            'pipeline_runs': self.pipeline_runs
        }
    
    def _empty_response(self) -> Dict:
        """Return empty response when no data"""
        return {
            'insights': [],
            'opportunities': [],
            'recommendations': [],
            'summary': {
                'total_insights': 0,
                'total_opportunities': 0,
                'total_recommendations': 0,
                'total_potential_reduction_kg': 0,
                'high_priority_count': 0,
                'categories': []
            },
            'pipeline_stats': self._get_pipeline_stats(0)
        }
    
    def get_stats(self) -> Dict:
        """Get orchestrator statistics"""
        return {
            'pipeline_runs': self.pipeline_runs
        }
