"""
RECOMMENDATION AGENT
Generates final formatted recommendations for dashboard display

Formats validated opportunities into user-friendly recommendations with:
- Clear titles
- Categories
- Carbon reduction percentages
- Cost impact
- Confidence scores
- Detailed reasoning

PURE FORMATTING - NO AI/LLM
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class RecommendationAgent:
    """
    Formats validated opportunities into final recommendations
    """
    
    def __init__(self):
        self.recommendation_stats = {
            'recommendations_generated': 0,
            'by_category': {},
            'total_potential_reduction': 0
        }
    
    def generate_recommendations(
        self,
        validated_opportunities: List[Dict],
        workload_analysis: Dict
    ) -> Dict:
        """
        Generate final recommendations from validated opportunities
        
        Args:
            validated_opportunities: Opportunities from ConstraintValidationAgent
            workload_analysis: Analysis from WorkloadAnalysisAgent
        
        Returns:
            Structured recommendations object for dashboard
        """
        logger.info("="*60)
        logger.info("[Recommendation Agent] Generating Final Recommendations")
        logger.info("="*60)
        
        recommendations = []
        
        for opp in validated_opportunities:
            recommendation = self._format_recommendation(opp)
            recommendations.append(recommendation)
            
            # Update category stats
            category = recommendation['category']
            if category not in self.recommendation_stats['by_category']:
                self.recommendation_stats['by_category'][category] = 0
            self.recommendation_stats['by_category'][category] += 1
        
        # Sort by carbon reduction potential
        recommendations.sort(key=lambda x: x['carbon_reduction_kg'], reverse=True)
        
        # Calculate total potential
        total_potential = sum(r['carbon_reduction_kg'] for r in recommendations)
        
        self.recommendation_stats['recommendations_generated'] = len(recommendations)
        self.recommendation_stats['total_potential_reduction'] = total_potential
        
        logger.info(f"✓ Generated {len(recommendations)} recommendations")
        logger.info(f"  Total Potential Reduction: {total_potential:.2f}kg CO2")
        logger.info(f"  Categories: {list(self.recommendation_stats['by_category'].keys())}")
        
        return {
            'recommendations': recommendations,
            'summary': self._generate_summary(recommendations, workload_analysis),
            'stats': self.recommendation_stats.copy()
        }
    
    def _format_recommendation(self, opp: Dict) -> Dict:
        """Format single opportunity into recommendation"""
        return {
            'id': f"{opp['type']}_{opp['service'].replace(' ', '_')}",
            'title': opp['title'],
            'category': opp['category'],
            'service': opp['service'],
            'carbon_reduction_pct': round(opp.get('carbon_reduction_pct', 0), 2),
            'carbon_reduction_kg': round(opp.get('carbon_reduction_kg', 0), 2),
            'cost_impact': opp.get('cost_impact', 'Neutral'),
            'confidence': opp.get('confidence', 'Medium'),
            'reasoning': opp.get('reasoning', ''),
            'constraints': opp.get('constraints_applied', []),
            'details': opp.get('details', {}),
            'type': opp.get('type', 'general')
        }
    
    def _generate_summary(self, recommendations: List[Dict], analysis: Dict) -> Dict:
        """Generate executive summary"""
        if not recommendations:
            return {
                'total_recommendations': 0,
                'total_potential_reduction_kg': 0,
                'total_potential_reduction_pct': 0,
                'top_category': None,
                'high_confidence_count': 0
            }
        
        total_current_emissions = analysis.get('service_analysis', {}).get('top_services', [{}])[0].get('total_emissions', 0)
        if not total_current_emissions:
            # Fallback: sum all service emissions
            total_current_emissions = sum(
                s.get('total_emissions', 0) 
                for s in analysis.get('service_analysis', {}).get('top_services', [])
            )
        
        total_reduction = sum(r['carbon_reduction_kg'] for r in recommendations)
        reduction_pct = (total_reduction / total_current_emissions * 100) if total_current_emissions > 0 else 0
        
        # Find top category
        category_totals = {}
        for r in recommendations:
            cat = r['category']
            if cat not in category_totals:
                category_totals[cat] = 0
            category_totals[cat] += r['carbon_reduction_kg']
        
        top_category = max(category_totals.items(), key=lambda x: x[1])[0] if category_totals else None
        
        # Count high confidence
        high_confidence = sum(1 for r in recommendations if r['confidence'] == 'High')
        
        return {
            'total_recommendations': len(recommendations),
            'total_potential_reduction_kg': round(total_reduction, 2),
            'total_potential_reduction_pct': round(reduction_pct, 2),
            'top_category': top_category,
            'high_confidence_count': high_confidence,
            'categories': list(category_totals.keys())
        }
    
    def get_recommendation_stats(self) -> Dict:
        """Get recommendation statistics"""
        return self.recommendation_stats.copy()
