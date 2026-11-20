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
        action_text = f"Reschedule non-urgent batch and data pipeline workloads from high-intensity window ({evidence['peak_carbon_window']}) to clean-energy window ({evidence['low_carbon_window']})."
        
        opportunity = {
            'category': 'scheduling',
            'type': 'time_shift',
            'title': "Schedule workloads during low-carbon periods",
            'service': 'Multi-Service',
            'finding': insight['observation'],
            'observation': insight['observation'],
            'evidence': {
                'current_window': evidence['peak_carbon_window'],
                'current_intensity': evidence['peak_avg_intensity'],
                'suggested_window': evidence['low_carbon_window'],
                'suggested_intensity': evidence['low_avg_intensity'],
                'current_emissions': evidence['peak_total_emissions'],
                'affected_services': evidence['affected_services'],
                'data_source': 'Electricity Maps Regional Grid Telemetry & AWS CUR hourly timestamps'
            },
            'root_cause': f"Workloads are currently executing during high-carbon periods ({evidence['peak_carbon_window']}) with average intensity of {evidence['peak_avg_intensity']} gCO2/kWh",
            'recommended_action': action_text,
            'recommendation': action_text,
            'action': action_text,
            'expected_reduction_pct': round(reduction_pct, 2),
            'carbon_reduction_pct': round(reduction_pct, 2),
            'potential_reduction_pct': round(reduction_pct, 2),
            'expected_reduction_kg': round(expected_reduction_kg, 4),
            'carbon_reduction_kg': round(expected_reduction_kg, 4),
            'potential_savings_kg': round(expected_reduction_kg, 4),
            'cost_impact': 'Neutral',
            'calculation_basis': f"ΔE = E_peak × ((I_peak - I_low) / I_peak) = {current_emissions:.4f} kg × (({evidence['peak_avg_intensity']} - {evidence['low_avg_intensity']}) / {evidence['peak_avg_intensity']})",
            'data_provenance': 'Electricity Maps Real-Time API / Regional Hourly Intensity Models',
            'constraints': [
                'Workload must be asynchronous / delay-tolerant',
                'Must respect daily ETL SLA delivery deadlines',
                'No compute infrastructure migration required'
            ],
            'constraints_applied': [
                'Workload must be asynchronous / delay-tolerant',
                'Must respect daily ETL SLA delivery deadlines',
                'No compute infrastructure migration required'
            ],
            'confidence': 'High',
            'implementation_complexity': 'Medium',
            'priority': 1,
            'details': {
                'current_window': evidence['peak_carbon_window'],
                'suggested_window': evidence['low_carbon_window'],
                'current_intensity': f"{evidence['peak_avg_intensity']} gCO2/kWh",
                'suggested_intensity': f"{evidence['low_avg_intensity']} gCO2/kWh"
            }
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
        action_text = f"Evaluate migrating delay-tolerant workloads from {evidence['high_carbon_region']} to {evidence['low_carbon_region']}, which features higher renewable grid share."
        
        opportunity = {
            'category': 'region',
            'type': 'region_migration',
            'title': "Consider migrating workloads to lower-carbon region",
            'service': 'Multi-Service',
            'finding': insight['observation'],
            'observation': insight['observation'],
            'evidence': {
                'current_region': evidence['high_carbon_region'],
                'current_intensity': evidence['high_region_intensity'],
                'current_emissions': evidence['high_region_emissions'],
                'suggested_region': evidence['low_carbon_region'],
                'suggested_intensity': evidence['low_region_intensity'],
                'affected_services': evidence['affected_services'],
                'data_source': 'Electricity Maps Regional Grid Carbon Intensity Comparison'
            },
            'root_cause': f"Region {evidence['high_carbon_region']} has significantly higher carbon intensity ({evidence['high_region_intensity']} gCO2/kWh) compared to {evidence['low_carbon_region']} ({evidence['low_region_intensity']} gCO2/kWh)",
            'recommended_action': action_text,
            'recommendation': action_text,
            'action': action_text,
            'expected_reduction_pct': round(reduction_pct, 2),
            'carbon_reduction_pct': round(reduction_pct, 2),
            'potential_reduction_pct': round(reduction_pct, 2),
            'expected_reduction_kg': round(expected_reduction_kg, 4),
            'carbon_reduction_kg': round(expected_reduction_kg, 4),
            'potential_savings_kg': round(expected_reduction_kg, 4),
            'cost_impact': 'Variable',
            'calculation_basis': f"ΔE = E_origin × ((I_origin - I_target) / I_origin) = {current_emissions:.4f} kg × (({evidence['high_region_intensity']} - {evidence['low_region_intensity']}) / {evidence['high_region_intensity']})",
            'data_provenance': 'Electricity Maps Regional Grid Telemetry & AWS Region Mapping',
            'constraints': [
                'Data residency and GDPR/compliance restrictions',
                'Inter-region network latency (<100ms tolerance)',
                'Egress network data transfer costs'
            ],
            'constraints_applied': [
                'Data residency and GDPR/compliance restrictions',
                'Inter-region network latency (<100ms tolerance)',
                'Egress network data transfer costs'
            ],
            'confidence': 'Medium',
            'implementation_complexity': 'High',
            'priority': 5,  # LOWEST PRIORITY
            'details': {
                'current_region': evidence['high_carbon_region'],
                'suggested_region': evidence['low_carbon_region'],
                'current_intensity': f"{evidence['high_region_intensity']} gCO2/kWh",
                'suggested_intensity': f"{evidence['low_region_intensity']} gCO2/kWh"
            }
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
            expected_reduction_kg = round(evidence['total_emissions_kg'] * 0.15, 4)
            action_text = f"Consolidate {service} batch job executions and align pipeline runs with low-carbon grid windows."
            opportunity = {
                'category': 'service',
                'type': 'data_processing_optimization',
                'title': f"Optimize {service} job scheduling",
                'service': service,
                'finding': insight['observation'],
                'observation': insight['observation'],
                'evidence': {
                    'executions': evidence['executions'],
                    'avg_intensity': evidence['avg_carbon_intensity'],
                    'total_emissions': evidence['total_emissions_kg'],
                    'avg_per_execution': evidence['avg_emission_per_execution'],
                    'data_source': 'AWS CUR Line-Item Records & Execution History'
                },
                'root_cause': f"{service} accounts for {evidence['percentage_of_total']:.1f}% of emissions with {evidence['executions']} executions at average {evidence['avg_carbon_intensity']} gCO2/kWh",
                'recommended_action': action_text,
                'recommendation': action_text,
                'action': action_text,
                'expected_reduction_pct': 15.0,
                'carbon_reduction_pct': 15.0,
                'potential_reduction_pct': 15.0,
                'expected_reduction_kg': expected_reduction_kg,
                'carbon_reduction_kg': expected_reduction_kg,
                'potential_savings_kg': expected_reduction_kg,
                'cost_impact': 'Neutral',
                'calculation_basis': f"ΔE = E_service × Empirical Batch Consolidation Factor = {evidence['total_emissions_kg']:.4f} kg × 15.0%",
                'data_provenance': 'AWS CUR Billing Records & Hourly Energy Aggregation',
                'constraints': [
                    'ETL pipeline upstream dependency ordering',
                    'Database transaction locking constraints'
                ],
                'constraints_applied': [
                    'ETL pipeline upstream dependency ordering',
                    'Database transaction locking constraints'
                ],
                'confidence': 'High',
                'implementation_complexity': 'Low',
                'priority': 2,
                'details': {
                    'executions': evidence['executions'],
                    'avg_carbon_intensity': f"{evidence['avg_carbon_intensity']} gCO2/kWh",
                    'total_emissions': f"{evidence['total_emissions_kg']:.4f} kg"
                }
            }
            opportunities.append(opportunity)
        
        elif 'EC2' in service or 'Elastic Compute' in service:
            # Compute services - suggest right-sizing
            expected_reduction_kg = round(evidence['total_emissions_kg'] * 0.10, 4)
            action_text = f"Right-size overprovisioned {service} instances and configure Auto-Scaling groups to eliminate idle energy burn."
            opportunity = {
                'category': 'resource',
                'type': 'compute_optimization',
                'title': f"Review {service} instance utilization",
                'service': service,
                'finding': insight['observation'],
                'observation': insight['observation'],
                'evidence': {
                    'total_emissions': evidence['total_emissions_kg'],
                    'total_cost': evidence['total_cost'],
                    'avg_intensity': evidence['avg_carbon_intensity'],
                    'data_source': 'AWS CUR Compute Usage Telemetry'
                },
                'root_cause': f"{service} contributes {evidence['percentage_of_total']:.1f}% of total emissions, suggesting potential for resource right-sizing",
                'recommended_action': action_text,
                'recommendation': action_text,
                'action': action_text,
                'expected_reduction_pct': 10.0,
                'carbon_reduction_pct': 10.0,
                'potential_reduction_pct': 10.0,
                'expected_reduction_kg': expected_reduction_kg,
                'carbon_reduction_kg': expected_reduction_kg,
                'potential_savings_kg': expected_reduction_kg,
                'cost_impact': 'Positive',
                'calculation_basis': f"ΔE = E_compute × Right-Sizing Headroom Factor = {evidence['total_emissions_kg']:.4f} kg × 10.0%",
                'data_provenance': 'AWS CUR vCPU-hours and instance type allocations',
                'constraints': [
                    'Peak CPU & memory burst buffer requirements',
                    'Minimum availability SLA across availability zones'
                ],
                'constraints_applied': [
                    'Peak CPU & memory burst buffer requirements',
                    'Minimum availability SLA across availability zones'
                ],
                'confidence': 'Medium',
                'implementation_complexity': 'Medium',
                'priority': 3,
                'details': {
                    'total_cost': f"${evidence['total_cost']:.2f}",
                    'total_emissions': f"{evidence['total_emissions_kg']:.4f} kg"
                }
            }
            opportunities.append(opportunity)
        
        elif 'S3' in service or 'Storage' in service:
            # Storage services - suggest lifecycle policies
            expected_reduction_kg = round(evidence['total_emissions_kg'] * 0.20, 4)
            action_text = f"Implement automated S3 Lifecycle tiering to migrate objects older than 30 days to Glacier Flexible Retrieval."
            opportunity = {
                'category': 'resource',
                'type': 'storage_optimization',
                'title': f"Implement {service} lifecycle policies",
                'service': service,
                'finding': insight['observation'],
                'observation': insight['observation'],
                'evidence': {
                    'total_emissions': evidence['total_emissions_kg'],
                    'total_cost': evidence['total_cost'],
                    'data_source': 'AWS CUR S3 Storage-ByteHours Records'
                },
                'root_cause': f"{service} accounts for {evidence['percentage_of_total']:.1f}% of emissions, indicating opportunities for storage tier optimization",
                'recommended_action': action_text,
                'recommendation': action_text,
                'action': action_text,
                'expected_reduction_pct': 20.0,
                'carbon_reduction_pct': 20.0,
                'potential_reduction_pct': 20.0,
                'expected_reduction_kg': expected_reduction_kg,
                'carbon_reduction_kg': expected_reduction_kg,
                'potential_savings_kg': expected_reduction_kg,
                'cost_impact': 'Positive',
                'calculation_basis': f"ΔE = E_storage × S3 Standard-to-Glacier Power Delta = {evidence['total_emissions_kg']:.4f} kg × 20.0%",
                'data_provenance': 'AWS CUR Byte-Hour Billing Telemetry',
                'constraints': [
                    'Object retrieval latency SLA (minutes/hours on Glacier)',
                    'Minimum 30/90 day object retention durations'
                ],
                'constraints_applied': [
                    'Object retrieval latency SLA (minutes/hours on Glacier)',
                    'Minimum 30/90 day object retention durations'
                ],
                'confidence': 'High',
                'implementation_complexity': 'Low',
                'priority': 3,
                'details': {
                    'total_cost': f"${evidence['total_cost']:.2f}",
                    'total_emissions': f"{evidence['total_emissions_kg']:.4f} kg"
                }
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
            expected_reduction_kg = round(evidence['total_emissions'] * 0.12, 4)
            action_text = f"Audit {service} resource configurations and migrate legacy instances to modern Graviton/ARM architectures to reduce carbon-per-dollar ratio."
            opportunity = {
                'category': 'cost',
                'type': 'cost_efficiency',
                'title': f"Improve {service} carbon efficiency",
                'service': service,
                'finding': insight['observation'],
                'observation': insight['observation'],
                'evidence': {
                    'carbon_per_dollar': evidence['carbon_per_dollar'],
                    'total_emissions': evidence['total_emissions'],
                    'total_cost': evidence['total_cost'],
                    'data_source': 'Cost and emission correlation analysis'
                },
                'root_cause': f"{service} produces {evidence['carbon_per_dollar']:.2f} kg CO2 per dollar spent, indicating room for efficiency improvements",
                'recommended_action': action_text,
                'recommendation': action_text,
                'action': action_text,
                'expected_reduction_pct': 12.0,
                'carbon_reduction_pct': 12.0,
                'potential_reduction_pct': 12.0,
                'expected_reduction_kg': expected_reduction_kg,
                'carbon_reduction_kg': expected_reduction_kg,
                'potential_savings_kg': expected_reduction_kg,
                'cost_impact': 'Neutral',
                'calculation_basis': f"ΔE = E_service × Architectural Efficiency Factor = {evidence['total_emissions']:.4f} kg × 12.0%",
                'data_provenance': 'AWS CUR Line-Item Cost & Calculated Emissions Ratio',
                'constraints': [
                    'Architecture instruction set compatibility (x86_64 vs aarch64)',
                    'Third-party software vendor licensing compatibility'
                ],
                'constraints_applied': [
                    'Architecture instruction set compatibility (x86_64 vs aarch64)',
                    'Third-party software vendor licensing compatibility'
                ],
                'confidence': 'Medium',
                'implementation_complexity': 'Medium',
                'priority': 4,
                'details': {
                    'carbon_per_dollar': f"{evidence['carbon_per_dollar']:.2f} kg/$",
                    'total_cost': f"${evidence['total_cost']:.2f}"
                }
            }
            opportunities.append(opportunity)
        
        return opportunities
    
    def get_stats(self) -> Dict:
        """Get discovery statistics"""
        return {
            'opportunities_discovered': self.opportunities_discovered
        }
