"""
INTELLIGENCE ORCHESTRATOR
Coordinates the Sustainability Intelligence Layer

Pipeline:
1. Workload Analysis Agent → Analyze emission patterns
2. Smart Optimization Agent → Generate opportunities
3. Constraint Validation Agent → Validate against profile
4. Recommendation Agent → Format recommendations
5. Gemini Explanation Agent (Optional) → Add natural language

ALL DETERMINISTIC - Only Gemini is optional AI
"""
import logging
from typing import Dict, List, Optional

from .workload_analysis_agent import WorkloadAnalysisAgent
from .smart_optimization_agent import SmartOptimizationAgent
from .constraint_validation_agent import ConstraintValidationAgent
from .recommendation_agent import RecommendationAgent
from .gemini_explanation_agent import GeminiExplanationAgent

logger = logging.getLogger(__name__)


class IntelligenceOrchestrator:
    """
    Orchestrates the intelligence layer for sustainability recommendations
    """
    
    def __init__(self):
        self.workload_agent = WorkloadAnalysisAgent()
        self.optimization_agent = SmartOptimizationAgent()
        self.validation_agent = ConstraintValidationAgent()
        self.recommendation_agent = RecommendationAgent()
        self.explanation_agent = GeminiExplanationAgent()
        
        self.pipeline_stats = {
            'intelligence_runs': 0,
            'total_recommendations': 0
        }
    
    async def generate_intelligence(
        self,
        emission_records: List[Dict],
        cur_data: List[Dict],
        analytics: Dict,
        org_profile: Optional[Dict] = None,
        use_gemini: bool = False
    ) -> Dict:
        """
        Generate complete sustainability intelligence
        
        Args:
            emission_records: Calculated emissions
            cur_data: Raw CUR data
            analytics: Analytics from AnalyticsAgent
            org_profile: Organization profile (optional)
            use_gemini: Whether to use Gemini for explanations
        
        Returns:
            Complete intelligence package
        """
        import time
        start_time = time.time()
        
        logger.info("="*80)
        logger.info("SUSTAINABILITY INTELLIGENCE LAYER")
        logger.info("="*80)
        
        # STAGE 1: Workload Analysis
        stage_start = time.time()
        workload_analysis = self.workload_agent.analyze(
            emission_records=emission_records,
            cur_data=cur_data,
            analytics=analytics
        )
        logger.info(f"[Stage 1] Workload Analysis: {time.time() - stage_start:.2f}s")
        
        # STAGE 2: Generate Optimization Opportunities
        stage_start = time.time()
        opportunities = self.optimization_agent.generate_opportunities(
            workload_analysis=workload_analysis,
            emission_records=emission_records
        )
        logger.info(f"[Stage 2] Optimization Generation: {time.time() - stage_start:.2f}s")
        
        # STAGE 3: Validate Against Constraints
        stage_start = time.time()
        validated_opportunities = self.validation_agent.validate_opportunities(
            opportunities=opportunities,
            org_profile=org_profile
        )
        logger.info(f"[Stage 3] Constraint Validation: {time.time() - stage_start:.2f}s")
        
        # STAGE 4: Generate Recommendations
        stage_start = time.time()
        recommendation_package = self.recommendation_agent.generate_recommendations(
            validated_opportunities=validated_opportunities,
            workload_analysis=workload_analysis
        )
        logger.info(f"[Stage 4] Recommendation Generation: {time.time() - stage_start:.2f}s")
        
        # STAGE 5: Optional Gemini Explanations
        explained_package = None
        if use_gemini:
            stage_start = time.time()
            explained_package = await self.explanation_agent.explain_recommendations(
                recommendations=recommendation_package['recommendations'],
                workload_analysis=workload_analysis,
                use_gemini=True
            )
            logger.info(f"[Stage 5] Gemini Explanations: {time.time() - stage_start:.2f}s")
        
        # Update stats
        self.pipeline_stats['intelligence_runs'] += 1
        self.pipeline_stats['total_recommendations'] += len(recommendation_package['recommendations'])
        
        total_time = time.time() - start_time
        
        logger.info("="*80)
        logger.info(f"✓ Intelligence Layer Complete: {total_time:.2f}s")
        logger.info(f"  Recommendations: {len(recommendation_package['recommendations'])}")
        logger.info(f"  Potential Reduction: {recommendation_package['summary']['total_potential_reduction_kg']:.2f}kg CO2")
        logger.info("="*80)
        
        # Compile response
        response = {
            'workload_analysis': workload_analysis,
            'recommendations': recommendation_package['recommendations'],
            'summary': recommendation_package['summary'],
            'explained_recommendations': explained_package['explained_recommendations'] if explained_package else None,
            'executive_summary': explained_package['executive_summary'] if explained_package else None,
            'pipeline_stats': {
                'workload_analysis': self.workload_agent.get_analysis_stats(),
                'optimization': self.optimization_agent.get_optimization_stats(),
                'validation': self.validation_agent.get_validation_stats(),
                'recommendations': self.recommendation_agent.get_recommendation_stats(),
                'explanations': self.explanation_agent.get_explanation_stats() if use_gemini else None,
                'total_time_seconds': round(total_time, 2)
            }
        }
        
        return response
    
    def get_intelligence_stats(self) -> Dict:
        """Get overall intelligence stats"""
        return self.pipeline_stats.copy()
