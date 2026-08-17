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
from typing import Dict, List, Optional

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
        workload_analysis: Dict,
        org_profile: Optional[Dict] = None
    ) -> Dict:
        """
        Generate final recommendations from validated opportunities
        
        Args:
            validated_opportunities: Opportunities from ConstraintValidationAgent
            workload_analysis: Analysis from WorkloadAnalysisAgent
            org_profile: Optional organization profile with constraints
        
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
        
        # Sort recommendations by optimization_priority weights
        priority = 'Balance Both'
        if org_profile:
            priority = org_profile.get('optimization_priority', 'Balance Both')
        
        def sort_key(rec):
            # Sort rejected to the bottom
            is_rejected = 1 if rec.get('constraint_status') == 'rejected' else 0
            co2_savings = rec.get('carbon_reduction_kg', 0.0)
            cost_impact = rec.get('cost_impact', 'Neutral')
            
            cost_score = 0.0
            if cost_impact == 'Positive':
                cost_score = 10.0
            elif cost_impact == 'Negative':
                cost_score = -10.0
                
            if priority == 'Reduce Carbon':
                score = co2_savings * 1.0 + cost_score * 0.1
            elif priority == 'Reduce Cost':
                score = co2_savings * 0.1 + cost_score * 1.0
            else: # Balance Both
                score = co2_savings * 0.5 + cost_score * 0.5
                
            return (is_rejected, -score) # rejected is 1, non-rejected is 0, so sorting ascending on is_rejected and then descending on score
            
        recommendations.sort(key=sort_key)
        
        # Calculate total potential (excluding rejected from the calculation)
        total_potential = sum(
            r['carbon_reduction_kg'] 
            for r in recommendations 
            if r.get('constraint_status') != 'rejected'
        )
        
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
        """Format single opportunity into recommendation with highly specific title and impact metrics"""
        opp_type = opp.get('type', 'general')
        service = opp.get('service', 'AWS Resource')
        evidence = opp.get('evidence', {})
        current_region = evidence.get('current_region', {})
        target_region = evidence.get('target_region', {})
        
        current_intensity = current_region.get('avg_intensity_gco2', 450.0)
        target_intensity = target_region.get('avg_intensity_gco2', 360.0)
        
        # 1. SPECIFIC TITLE GENERATION
        title = opp.get('title', '')
        if opp_type == 'time_shift':
            details = opp.get('details', {})
            current_window = details.get('current_window', '14:00')
            suggested_window = details.get('suggested_window', '02:00')
            title = f"Shift {service} execution window from {current_window} to {suggested_window}"
        elif opp_type == 'region_migration':
            details = opp.get('details', {})
            curr_reg = details.get('current_region', 'ap-south-1')
            sugg_reg = details.get('suggested_region', 'eu-north-1')
            title = f"Migrate {service} resources from {curr_reg} to {sugg_reg}"
        elif opp_type == 'compute_optimization':
            title = f"Right-size provisioned {service} capacity to align with workload demand"
        elif opp_type == 'data_processing_optimization':
            details = opp.get('details', {})
            exec_count = details.get('execution_count', 5)
            title = f"Consolidate {service} executions (currently running {exec_count}x daily)"
        elif opp_type == 'workload_smoothing':
            details = opp.get('details', {})
            spike_date = details.get('spike_date', 'today')
            title = f"Smooth emissions spikes detected on {spike_date} for {service}"

        # 2. SPECIFIC IMPACT GENERATION
        reduction_pct = round(opp.get('expected_reduction_pct', 0), 2)
        if reduction_pct == 0 and current_intensity > 0:
            reduction_pct = round(((current_intensity - target_intensity) / current_intensity) * 100, 2)
            
        impact = f"Reduces emissions by ~{reduction_pct:.0f}% (from {current_intensity:.0f} gCO2/kWh avg to {target_intensity:.0f} gCO2/kWh avg)"

        return {
            'id': f"{opp_type}_{service.replace(' ', '_')}",
            'title': title,
            'impact': impact,
            'category': opp['category'],
            'service': service,
            'carbon_reduction_pct': reduction_pct,
            'carbon_reduction_kg': round(opp.get('expected_reduction_kg', 0), 2),
            'cost_impact': opp.get('cost_impact', 'Neutral'),
            'confidence': opp.get('confidence', 'Medium'),
            'reasoning': opp.get('reasoning', ''),
            'constraints': opp.get('constraints_applied', []),
            'details': opp.get('details', {}),
            'type': opp_type,
            'evidence': evidence,
            'root_cause': opp.get('root_cause', ''),
            'constraint_status': opp.get('constraint_status', 'compatible'),
            'constraint_reason': opp.get('constraint_reason', ''),
            'effort': opp.get('effort', 'Medium'),
            'implementation_complexity': opp.get('implementation_complexity', 'Medium')
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
