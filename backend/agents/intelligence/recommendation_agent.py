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
        """Format single opportunity into recommendation with highly specific title, complete evidence, and implementation steps"""
        opp_type = opp.get('type', 'general')
        service = opp.get('service', 'AWS Resource')
        evidence = opp.get('evidence', {})
        current_region = evidence.get('current_region', {})
        target_region = evidence.get('target_region', {})
        details = opp.get('details', {})
        
        current_intensity = current_region.get('avg_intensity_gco2', 450.0)
        target_intensity = target_region.get('avg_intensity_gco2', 360.0)
        current_zone = current_region.get('zone', 'Unknown')
        target_zone = target_region.get('zone', 'Unknown')
        
        # 1. SPECIFIC TITLE GENERATION
        title = opp.get('title', '')
        if opp_type == 'time_shift':
            current_window = details.get('current_window', '14:00')
            suggested_window = details.get('suggested_window', '02:00')
            execution_count = details.get('affected_executions', details.get('execution_count', 0))
            title = f"Shift {service} batch processing ({execution_count} executions) from {current_window} to {suggested_window}"
        elif opp_type == 'region_migration':
            curr_reg = details.get('current_region', 'ap-south-1')
            sugg_reg = details.get('suggested_region', 'eu-north-1')
            title = f"Migrate {service} from {curr_reg} ({current_intensity:.0f} gCO2/kWh) to {sugg_reg} ({target_intensity:.0f} gCO2/kWh)"
        elif opp_type == 'compute_optimization':
            title = f"Right-size {service} based on measured {details.get('emissions_pct', 0):.1f}% emission concentration"
        elif opp_type == 'data_processing_optimization':
            exec_count = details.get('execution_count', 5)
            title = f"Consolidate {service} batch jobs ({exec_count} executions detected)"
        elif opp_type == 'workload_smoothing':
            spike_date = details.get('spike_date', 'today')
            spike_mult = details.get('spike_multiplier', 2.0)
            title = f"Smooth {service} workload spikes (detected {spike_mult:.1f}x daily average on {spike_date})"

        # 2. EVIDENCE COMPILATION
        root_cause = opp.get('root_cause', '')
        if not root_cause:
            if opp_type == 'time_shift':
                root_cause = f"{service} executed {details.get('affected_executions', 0)} times during high-carbon window ({current_window}) at {current_intensity:.0f} gCO2/kWh average intensity."
            elif opp_type == 'region_migration':
                root_cause = f"{service} operates in {details.get('current_region', 'high-carbon region')} with {current_intensity:.0f} gCO2/kWh grid intensity, significantly higher than {details.get('suggested_region', 'cleaner alternatives')} at {target_intensity:.0f} gCO2/kWh."
            else:
                root_cause = opp.get('reasoning', 'Optimization opportunity identified based on workload analysis.')
        
        # 3. SOLUTION / IMPLEMENTATION STEPS
        solution = ""
        implementation_steps = []
        
        if opp_type == 'time_shift':
            solution = f"Reschedule {service} batch jobs from {current_window} to {suggested_window} when grid carbon intensity is lower. Verify downstream dependencies and SLA requirements before applying changes."
            implementation_steps = [
                f"Identify {service} jobs currently scheduled at {current_window}",
                f"Check downstream dependencies and SLA constraints",
                f"Test rescheduling to {suggested_window} for a subset of jobs",
                f"Monitor carbon intensity during new execution window",
                f"Gradually roll out schedule change to all eligible jobs"
            ]
        elif opp_type == 'region_migration':
            solution = f"Migrate {service} workloads from {details.get('current_region', 'current region')} to {details.get('suggested_region', 'cleaner region')}. Evaluate data residency requirements, latency impact, and migration complexity."
            implementation_steps = [
                f"Audit data residency and compliance requirements for {service}",
                f"Measure baseline latency from {details.get('current_region', 'current')} region",
                f"Test workload performance in {details.get('suggested_region', 'target')} region",
                f"Plan phased migration starting with non-critical workloads",
                f"Execute migration and validate emissions reduction"
            ]
        elif opp_type == 'compute_optimization':
            solution = f"Analyze {service} resource utilization and right-size based on actual demand. Consider auto-scaling configuration and instance type optimization."
            implementation_steps = [
                f"Enable CloudWatch detailed monitoring for {service}",
                f"Review 30-day utilization patterns (CPU, memory, network)",
                f"Identify over-provisioned instances or poorly configured auto-scaling",
                f"Test smaller instance types or revised scaling policies",
                f"Apply optimizations and monitor impact on emissions and cost"
            ]
        elif opp_type == 'data_processing_optimization':
            solution = f"Consolidate {service} batch jobs to reduce redundant executions. Review job dependencies and consider combining similar workloads."
            implementation_steps = [
                f"Audit {service} job schedule and identify {details.get('execution_count', 0)} executions",
                f"Analyze job dependencies and data freshness requirements",
                f"Consolidate redundant or overlapping jobs where feasible",
                f"Implement batching for similar data processing tasks",
                f"Monitor consolidated job performance and emissions"
            ]
        elif opp_type == 'workload_smoothing':
            solution = f"Distribute {service} workload more evenly to avoid emissions spikes. Investigate batch processing triggers and consider spreading execution windows."
            implementation_steps = [
                f"Identify cause of workload spike on {details.get('spike_date', 'spike date')}",
                f"Review batch trigger configuration and timing",
                f"Implement rate limiting or staggered execution",
                f"Spread workload across multiple time windows",
                f"Monitor daily emissions to confirm smoothing effect"
            ]
        else:
            solution = opp.get('reasoning', 'Review and implement optimization as appropriate.')
            implementation_steps = [
                f"Review {service} configuration and usage patterns",
                "Implement recommended changes in test environment",
                "Validate emissions impact before production deployment",
                "Monitor and adjust based on results"
            ]
        
        # 4. IMPACT CALCULATION
        reduction_pct = round(opp.get('expected_reduction_pct', 0), 2)
        if reduction_pct == 0 and current_intensity > 0 and target_intensity > 0:
            reduction_pct = round(((current_intensity - target_intensity) / current_intensity) * 100, 2)
        
        reduction_kg = round(opp.get('expected_reduction_kg', 0), 2)
        
        impact_description = f"Reduces emissions by ~{reduction_pct:.0f}% (from {current_intensity:.0f} gCO2/kWh avg to {target_intensity:.0f} gCO2/kWh avg). Estimated reduction: {reduction_kg:.2f} kg CO₂."
        
        # 5. CARBON COMPARISON FOR UI
        carbon_comparison = {
            'current_gco2_kwh': round(current_intensity, 2),
            'target_gco2_kwh': round(target_intensity, 2),
            'reduction_pct': reduction_pct,
            'reduction_kg': reduction_kg
        }
        
        # 6. CONSTRAINT SUMMARY
        constraints_summary = {
            'applied_constraints': opp.get('constraints_applied', []),
            'constraint_status': opp.get('constraint_status', 'compatible'),
            'constraint_reason': opp.get('constraint_reason', '')
        }

        return {
            'id': f"{opp_type}_{service.replace(' ', '_')}_{hash(title) % 10000}",
            'title': title,
            'impact': impact_description,
            'category': opp['category'],
            'service': service,
            'carbon_reduction_pct': reduction_pct,
            'carbon_reduction_kg': reduction_kg,
            'cost_impact': opp.get('cost_impact', 'Neutral'),
            'confidence': opp.get('confidence', 'Medium'),
            'reasoning': opp.get('reasoning', ''),
            'solution': solution,
            'implementation_steps': implementation_steps,
            'constraints': opp.get('constraints_applied', []),
            'carbon_comparison': carbon_comparison,
            'details': details,
            'type': opp_type,
            'evidence': evidence,
            'root_cause': root_cause,
            'constraint_status': opp.get('constraint_status', 'compatible'),
            'constraint_reason': opp.get('constraint_reason', ''),
            'effort': opp.get('effort', 'Medium'),
            'implementation_complexity': opp.get('implementation_complexity', 'Medium'),
            'data_sources': ['emission_records', 'analysis_summary', 'organization_profile', 'electricity_maps']
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
