"""
SUSTAINABILITY INTELLIGENCE ENGINE
Purpose: "What should the organization do?"

Pipeline:
Database (analysis_summary + emission_records + organization_profile)
→ Workload Analysis → Pattern Detection → Optimization → Constraint Validation → Recommendation → Explanation → recommendation_runs table

Inputs:
- analysis_summary (from accounting engine)
- emission_records (from accounting engine)
- organization_profile (user constraints)

Outputs:
- recommendation_runs table

RULES:
- NO CUR parsing
- NO emission calculations
- Works ONLY from stored accounting results
- May use Electricity Maps for optimization discovery ONLY
- Gemini for explanations ONLY (optional)
"""
import logging
from typing import Dict, List, Optional
from .workload_analysis_agent import WorkloadAnalysisAgent
from .pattern_detection_agent import PatternDetectionAgent
from .optimization_agent import OptimizationAgent
from .constraint_validation_agent import ConstraintValidationAgent
from .recommendation_agent import RecommendationAgent
from .explanation_agent import GeminiExplanationAgent

logger = logging.getLogger(__name__)


class SustainabilityIntelligenceEngine:
    """
    Sustainability Intelligence Engine - answers "What should we do?"
    Analyzes stored accounting data and generates recommendations
    """
    
    def __init__(self):
        self.workload_agent = WorkloadAnalysisAgent()
        self.pattern_agent = PatternDetectionAgent()
        self.optimization_agent = OptimizationAgent()
        self.constraint_agent = ConstraintValidationAgent()
        self.recommendation_agent = RecommendationAgent()
        self.explanation_agent = GeminiExplanationAgent()
    
    async def generate_insights(
        self,
        analysis_summary: Dict,
        emission_records: List[Dict],
        org_profile: Optional[Dict] = None,
        use_gemini: bool = False
    ) -> Dict:
        """
        Generate sustainability insights from stored accounting data
        
        Args:
            analysis_summary: Precomputed summary from analysis_summary table
            emission_records: Detailed records from emission_records table
            org_profile: Organization constraints from organization_profile table
            use_gemini: Whether to use Gemini for explanations
        
        Returns:
            Complete intelligence result with recommendations
        """
        import time
        start_time = time.time()
        
        logger.info("="*80)
        logger.info("SUSTAINABILITY INTELLIGENCE ENGINE")
        logger.info("="*80)
        logger.info(f"Analysis records: {len(emission_records)}")
        logger.info(f"Organization profile: {'Yes' if org_profile else 'No'}")
        logger.info(f"Gemini enabled: {use_gemini}")
        
        try:
            # STAGE 1: Workload Analysis
            logger.info("\n[1/6] Workload Analysis Agent")
            logger.info("-"*80)
            workload_analysis = self.workload_agent.analyze(
                emission_records=emission_records,
                cur_data=[],  # Not needed - we use stored data
                analytics=analysis_summary
            )
            workload_stats = self.workload_agent.get_analysis_stats()
            logger.info(f"✓ Analyzed workload patterns")
            logger.info(f"  Services: {workload_stats['services_identified']}")
            logger.info(f"  Regions: {workload_stats['regions_identified']}")
            logger.info(f"  Hotspots: {workload_stats['hotspots_found']}")
            
            # STAGE 2: Pattern Detection
            logger.info("\n[2/6] Pattern Detection Agent")
            logger.info("-"*80)
            patterns = self.pattern_agent.detect_patterns(
                analysis_summary=analysis_summary,
                emission_records=emission_records
            )
            pattern_stats = self.pattern_agent.get_stats()
            logger.info(f"✓ Detected {pattern_stats['patterns_found']} patterns")
            
            # STAGE 3: Optimization Discovery
            logger.info("\n[3/6] Optimization Agent")
            logger.info("-"*80)
            opportunities = await self.optimization_agent.discover_opportunities(
                patterns=patterns,
                analysis_summary=analysis_summary
            )
            optimization_stats = self.optimization_agent.get_stats()
            logger.info(f"✓ Discovered {optimization_stats['opportunities_found']} opportunities")
            logger.info(f"  Electricity Maps enabled: {optimization_stats['electricity_maps_enabled']}")
            
            # STAGE 4: Constraint Validation
            logger.info("\n[4/6] Constraint Validation Agent")
            logger.info("-"*80)
            validated_opportunities = self.constraint_agent.validate_opportunities(
                opportunities=opportunities,
                org_profile=org_profile
            )
            validation_stats = self.constraint_agent.get_validation_stats()
            logger.info(f"✓ Validated opportunities")
            logger.info(f"  High confidence: {validation_stats['high_confidence']}")
            logger.info(f"  Medium confidence: {validation_stats['medium_confidence']}")
            logger.info(f"  Low confidence: {validation_stats['low_confidence']}")
            logger.info(f"  Rejected: {validation_stats['rejected']}")
            
            # STAGE 5: Recommendation Generation
            logger.info("\n[5/6] Recommendation Agent")
            logger.info("-"*80)
            recommendations_result = self.recommendation_agent.generate_recommendations(
                validated_opportunities=validated_opportunities,
                workload_analysis=workload_analysis,
                org_profile=org_profile
            )
            recommendations = recommendations_result['recommendations']
            recommendation_stats = self.recommendation_agent.get_recommendation_stats()
            logger.info(f"✓ Generated {len(recommendations)} recommendations")
            logger.info(f"  Total potential reduction: {recommendations_result['summary']['total_potential_reduction_kg']:.2f}kg CO2")
            
            # STAGE 6: Explanation (Always run to apply structured fallback explanations and filters)
            logger.info("\n[6/6] Explanation Agent")
            logger.info("-"*80)
            explained_result = await self.explanation_agent.explain_recommendations(
                recommendations=recommendations,
                workload_analysis=workload_analysis,
                use_gemini=use_gemini
            )
            explained_recommendations = explained_result['explained_recommendations']
            explanation_stats = self.explanation_agent.get_explanation_stats()
            logger.info(f"✓ Generated explanations")
            logger.info(f"  Gemini calls: {explanation_stats.get('gemini_calls', 0)}")
            logger.info(f"  Fallback used: {explanation_stats.get('fallback_used', 0)}")
            
            duration = time.time() - start_time
            
            logger.info("\n" + "="*80)
            logger.info("INTELLIGENCE ENGINE COMPLETE")
            logger.info("="*80)
            logger.info(f"Patterns Detected: {len(patterns)}")
            logger.info(f"Opportunities Found: {len(opportunities)}")
            logger.info(f"Recommendations: {len(recommendations)}")
            logger.info(f"Potential Reduction: {recommendations_result['summary']['total_potential_reduction_kg']:.2f}kg CO2")
            logger.info(f"Duration: {duration:.2f}s")
            logger.info("="*80 + "\n")
            
            return {
                'success': True,
                'workload_analysis': workload_analysis,
                'patterns': patterns,
                'opportunities': opportunities,
                'validated_opportunities': validated_opportunities,
                'recommendations': explained_recommendations,
                'summary': recommendations_result['summary'],
                'intelligence_stats': {
                    'workload_analysis': workload_stats,
                    'pattern_detection': pattern_stats,
                    'optimization': optimization_stats,
                    'constraint_validation': validation_stats,
                    'recommendation': recommendation_stats,
                    'explanation': explanation_stats,
                    'duration_seconds': round(duration, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Intelligence engine error: {str(e)}", exc_info=True)
            return self._error_response(f"Intelligence engine error: {str(e)}")
    
    def _error_response(self, message: str) -> Dict:
        """Generate error response"""
        return {
            'success': False,
            'error': message,
            'workload_analysis': {},
            'patterns': [],
            'opportunities': [],
            'validated_opportunities': [],
            'recommendations': [],
            'summary': {},
            'intelligence_stats': {}
        }
