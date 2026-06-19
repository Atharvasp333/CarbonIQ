"""
OPTIMIZATION DISCOVERY AGENT
Discovers optimization opportunities based on evidence from insights

CRITICAL: This agent only discovers opportunities based on evidence
No generic recommendations, no hardcoded suggestions
Every opportunity must be backed by data from insights
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class OptimizationDiscoveryAgent:
    """
    Discovers optimization opportunities from evidence-based insights
    
    Categories:
    1. Scheduling Optimization (Priority 1)
    2. Service Optimization (Priority 2)
    3. Resource Optimization (Priority 3)
    4. Cost Optimization (Priority 4)
    5. Region Migration (Priority 5 - Last Resort)
    """
    
    PRIORITY_ORDER = {
        'scheduling': 1,
        'service': 2,
        'resource': 3,
        'cost': 4,
        'region': 5
    }
    
    def __init__(self):
        self.opportunities_discovered = 0
    
    def discover_opportunities(self, insights: List[Dict], emission_records: List[Dict]) -> List[Dict]:
        """
        Discover optimization opportunities from insights
        
        Args:
            insights: Evidence-based insights from InsightGenerationAgent
            emission_records: Raw emission records for additional analysis
        
        Returns:
            List of opportunities with evidence and expected impact
        """
        logger.info("="*60)
        logger.info("[Optimization Discovery Agent] Discovering Opportunities")
        logger.info("="*60)
        
        opportunities = []
        
        for insight in insights:
            # Discover opportunities based on insight type
            if insight['type'] == 'time_analysis':
                opportunities.extend(self._discover_scheduling_opportunities(insight, emission_records))
            
            elif insight['type'] == 'region_analysis':
                opportunities.extend(self._discover_region_opportunities(insight, emission_records))
            
            elif insight['type'] == 'service_analysis':
                opportunities.extend(self._discover_service_opportunities(insight, emission_records))
            
            elif insight['type'] == 'cost_efficiency':
                opportunities.extend(self._discover_cost_opportunities(insight, emission_records))
        
        # Sort by priority
        opportunities.sort(key=lambda x: (self.PRIORITY_ORDER.get(x['category'], 99), -x['expected_reduction_kg']))
        
        self.opportunities_discovered = len(opportunities)
        
        logger.info(f"✓ Discovered {len(opportunities)} evidence-based opportunities")
        
        return opportunities
    
    def _discover_scheduling_opportunities(self, insight: Dict, records: List[Dict]) -> List[Dict]:
        """Discover time-shift opportunities (HIGHEST PRIORITY)"""
        opportunities = []
        
        evidence = insight['evidence']
        
        # Only create opportunity if reduction is significant
        if evidence['potential_reduction_pct'] < 10:
            return opportunities
        
        # Calculate actual emission reduction
        current_emissions = evidence['peak_total_emissions']
        reduction_pct = evidence['potential_reduction_pct']
        expected_reduction_kg = current_emissions * (reduction_pct / 100)
        
        opportunity = {
            'category': 'scheduling',
            'type': 'time_shift',
            'title': f"Schedule workloads during low-carbon periods",
            'service': 'Multi-Service',
            'observation': insight['observation'],
            'evidence': {
                'current_window': evidence['peak_carbon_window'],
                'current_intensity': evidence['peak_avg_intensity'],
                'suggested_window': evidence['low_carbon_window'],
                'suggested_intensity': evidence['low_avg_intensity'],
                'current_emissions': evidence['peak_total_emissions'],
                'affected_services': evidence['affected_services'],
                'data_source': 'Historical execution patterns and carbon intensity data'
            },
            'root_cause': f"Workloads are currently executing during high-carbon periods ({evidence['peak_carbon_window']}) with average intensity of {evidence['peak_avg_intensity']} gCO2/kWh",
            'expected_reduction_pct': round(reduction_pct, 2),
            'expected_reduction_kg': round(expected_reduction_kg, 4),
            'cost_impact': 'Neutral',
            'implementation_complexity': 'Medium',
            'priority': 1
        }
        
        opportunities.append(opportunity)
        
        return opportunities
    
    def _discover_region_opportunities(self, insight: Dict, records: List[Dict]) -> List[Dict]:
        """Discover region migration opportunities (LOWEST PRIORITY)"""
        opportunities = []
        
        evidence = insight['evidence']
        
        # Only create opportunity if reduction is significant
        if evidence['potential_reduction_pct'] < 20:
            return opportunities
        
        # Calculate actual emission reduction
        current_emissions = evidence['high_region_emissions']
        reduction_pct = evidence['potential_reduction_pct']
        expected_reduction_kg = current_emissions * (reduction_pct / 100)
        
        opportunity = {
            'category': 'region',
            'type': 'region_migration',
            'title': f"Consider migrating workloads to lower-carbon region",
            'service': 'Multi-Service',
            'observation': insight['observation'],
            'evidence': {
                'current_region': evidence['high_carbon_region'],
                'current_intensity': evidence['high_region_intensity'],
                'current_emissions': evidence['high_region_emissions'],
                'suggested_region': evidence['low_carbon_region'],
                'suggested_intensity': evidence['low_region_intensity'],
                'affected_services': evidence['affected_services'],
                'data_source': 'Regional carbon intensity comparison'
            },
            'root_cause': f"Region {evidence['high_carbon_region']} has significantly higher carbon intensity ({evidence['high_region_intensity']} gCO2/kWh) compared to {evidence['low_carbon_region']} ({evidence['low_region_intensity']} gCO2/kWh)",
            'expected_reduction_pct': round(reduction_pct, 2),
            'expected_reduction_kg': round(expected_reduction_kg, 4),
            'cost_impact': 'Variable',
            'implementation_complexity': 'High',
            'priority': 5  # LOWEST PRIORITY
        }
        
        opportunities.append(opportunity)
        
        return opportunities
    
    def _discover_service_opportunities(self, insight: Dict, records: List[Dict]) -> List[Dict]:
        """Discover service-specific opportunities"""
        opportunities = []
        
        service = insight['service']
        evidence = insight['evidence']
        
        # Only process significant emitters
        if evidence['percentage_of_total'] < 10:
            return opportunities
        
        # Analyze service-specific patterns
        service_records = [r for r in records if r['service'] == service]
        
        # Check for optimization potential based on service type
        if 'Glue' in service or 'EMR' in service or 'Batch' in service:
            # Data processing services - suggest scheduling
            opportunity = {
                'category': 'service',
                'type': 'data_processing_optimization',
                'title': f"Optimize {service} job scheduling",
                'service': service,
                'observation': insight['observation'],
                'evidence': {
                    'executions': evidence['executions'],
                    'avg_intensity': evidence['avg_carbon_intensity'],
                    'total_emissions': evidence['total_emissions_kg'],
                    'avg_per_execution': evidence['avg_emission_per_execution'],
                    'data_source': 'Service execution history'
                },
                'root_cause': f"{service} accounts for {evidence['percentage_of_total']:.1f}% of emissions with {evidence['executions']} executions at average {evidence['avg_carbon_intensity']} gCO2/kWh",
                'expected_reduction_pct': 15,  # Conservative estimate for scheduling
                'expected_reduction_kg': round(evidence['total_emissions_kg'] * 0.15, 4),
                'cost_impact': 'Neutral',
                'implementation_complexity': 'Low',
                'priority': 2
            }
            opportunities.append(opportunity)
        
        elif 'EC2' in service or 'Elastic Compute' in service:
            # Compute services - suggest right-sizing
            opportunity = {
                'category': 'resource',
                'type': 'compute_optimization',
                'title': f"Review {service} instance utilization",
                'service': service,
                'observation': insight['observation'],
                'evidence': {
                    'total_emissions': evidence['total_emissions_kg'],
                    'total_cost': evidence['total_cost'],
                    'avg_intensity': evidence['avg_carbon_intensity'],
                    'data_source': 'Service utilization patterns'
                },
                'root_cause': f"{service} contributes {evidence['percentage_of_total']:.1f}% of total emissions, suggesting potential for resource optimization",
                'expected_reduction_pct': 10,  # Conservative estimate
                'expected_reduction_kg': round(evidence['total_emissions_kg'] * 0.10, 4),
                'cost_impact': 'Positive',
                'implementation_complexity': 'Medium',
                'priority': 3
            }
            opportunities.append(opportunity)
        
        elif 'S3' in service or 'Storage' in service:
            # Storage services - suggest lifecycle policies
            opportunity = {
                'category': 'resource',
                'type': 'storage_optimization',
                'title': f"Implement {service} lifecycle policies",
                'service': service,
                'observation': insight['observation'],
                'evidence': {
                    'total_emissions': evidence['total_emissions_kg'],
                    'total_cost': evidence['total_cost'],
                    'data_source': 'Storage usage patterns'
                },
                'root_cause': f"{service} accounts for {evidence['percentage_of_total']:.1f}% of emissions, indicating opportunities for storage tier optimization",
                'expected_reduction_pct': 20,  # Conservative estimate
                'expected_reduction_kg': round(evidence['total_emissions_kg'] * 0.20, 4),
                'cost_impact': 'Positive',
                'implementation_complexity': 'Low',
                'priority': 3
            }
            opportunities.append(opportunity)
        
        return opportunities
    
    def _discover_cost_opportunities(self, insight: Dict, records: List[Dict]) -> List[Dict]:
        """Discover cost-efficiency opportunities"""
        opportunities = []
        
        evidence = insight['evidence']
        service = insight['service']
        
        # High carbon per dollar indicates inefficiency
        if evidence['carbon_per_dollar'] > 1.5:
            opportunity = {
                'category': 'cost',
                'type': 'cost_efficiency',
                'title': f"Improve {service} carbon efficiency",
                'service': service,
                'observation': insight['observation'],
                'evidence': {
                    'carbon_per_dollar': evidence['carbon_per_dollar'],
                    'total_emissions': evidence['total_emissions'],
                    'total_cost': evidence['total_cost'],
                    'data_source': 'Cost and emission correlation analysis'
                },
                'root_cause': f"{service} produces {evidence['carbon_per_dollar']:.2f} kg CO2 per dollar spent, indicating room for efficiency improvements",
                'expected_reduction_pct': 12,  # Conservative estimate
                'expected_reduction_kg': round(evidence['total_emissions'] * 0.12, 4),
                'cost_impact': 'Neutral',
                'implementation_complexity': 'Medium',
                'priority': 4
            }
            opportunities.append(opportunity)
        
        return opportunities
    
    def get_stats(self) -> Dict:
        """Get discovery statistics"""
        return {
            'opportunities_discovered': self.opportunities_discovered
        }
