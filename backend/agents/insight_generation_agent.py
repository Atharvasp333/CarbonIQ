"""
INSIGHT GENERATION AGENT
Generates factual, evidence-based findings from emission data

CRITICAL: This agent only generates OBSERVATIONS and EVIDENCE
No recommendations, no suggestions, only facts from data analysis
"""
import logging
from typing import Dict, List
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class InsightGenerationAgent:
    """
    Generates factual insights with supporting evidence from emission data
    
    Output: Structured observations with quantifiable evidence
    """
    
    def __init__(self):
        self.insights_generated = 0
    
    def generate_insights(self, emission_records: List[Dict], analytics: Dict) -> List[Dict]:
        """
        Generate evidence-based insights from emission data
        
        Args:
            emission_records: Calculated emissions from EmissionCalculationAgent
            analytics: Aggregated analytics from AnalyticsAgent
        
        Returns:
            List of insights with observations and evidence
        """
        logger.info("="*60)
        logger.info("[Insight Generation Agent] Generating Evidence-Based Insights")
        logger.info("="*60)
        
        insights = []
        
        # Service-level insights
        insights.extend(self._generate_service_insights(emission_records, analytics))
        
        # Time-based insights
        insights.extend(self._generate_time_insights(emission_records))
        
        # Region-based insights
        insights.extend(self._generate_region_insights(emission_records, analytics))
        
        # Cost-efficiency insights
        insights.extend(self._generate_cost_insights(emission_records, analytics))
        
        self.insights_generated = len(insights)
        
        logger.info(f"✓ Generated {len(insights)} evidence-based insights")
        
        return insights
    
    def _generate_service_insights(self, records: List[Dict], analytics: Dict) -> List[Dict]:
        """Generate service-level insights with evidence"""
        insights = []
        
        # Analyze each service
        service_data = defaultdict(lambda: {
            'emissions': [],
            'costs': [],
            'executions': 0,
            'intensities': [],
            'energy': []
        })
        
        total_emissions = sum(r['emissions_kg'] for r in records)
        
        for record in records:
            service = record['service']
            service_data[service]['emissions'].append(record['emissions_kg'])
            service_data[service]['costs'].append(record['cost'])
            service_data[service]['executions'] += 1
            service_data[service]['intensities'].append(record['carbon_intensity'])
            service_data[service]['energy'].append(record['energy_kwh'])
        
        # Generate insights for top emitting services
        for service, data in service_data.items():
            service_total = sum(data['emissions'])
            percentage = (service_total / total_emissions * 100) if total_emissions > 0 else 0
            
            # Only generate insight if service is significant (>5% of total)
            if percentage > 5:
                avg_intensity = sum(data['intensities']) / len(data['intensities'])
                total_cost = sum(data['costs'])
                total_energy = sum(data['energy'])
                
                insight = {
                    'type': 'service_analysis',
                    'service': service,
                    'observation': f"{service} contributes {percentage:.1f}% of total emissions",
                    'evidence': {
                        'total_emissions_kg': round(service_total, 4),
                        'percentage_of_total': round(percentage, 2),
                        'executions': data['executions'],
                        'avg_carbon_intensity': round(avg_intensity, 2),
                        'total_cost': round(total_cost, 4),
                        'total_energy_kwh': round(total_energy, 4),
                        'avg_emission_per_execution': round(service_total / data['executions'], 4)
                    },
                    'severity': 'high' if percentage > 50 else 'medium' if percentage > 20 else 'low'
                }
                
                insights.append(insight)
        
        return insights
    
    def _generate_time_insights(self, records: List[Dict]) -> List[Dict]:
        """Generate time-based insights with evidence"""
        insights = []
        
        # Analyze hourly patterns
        hourly_data = defaultdict(lambda: {
            'emissions': [],
            'intensities': [],
            'executions': 0,
            'services': set()
        })
        
        for record in records:
            try:
                dt = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                hour = dt.hour
                
                hourly_data[hour]['emissions'].append(record['emissions_kg'])
                hourly_data[hour]['intensities'].append(record['carbon_intensity'])
                hourly_data[hour]['executions'] += 1
                hourly_data[hour]['services'].add(record['service'])
            except Exception:
                continue
        
        if not hourly_data:
            return insights
        
        # Calculate average intensity per hour
        hourly_avg = {}
        for hour, data in hourly_data.items():
            hourly_avg[hour] = {
                'avg_intensity': sum(data['intensities']) / len(data['intensities']),
                'total_emissions': sum(data['emissions']),
                'executions': data['executions'],
                'services': list(data['services'])
            }
        
        # Find peak and low carbon hours
        sorted_hours = sorted(hourly_avg.items(), key=lambda x: x[1]['avg_intensity'])
        
        if len(sorted_hours) >= 2:
            # Low carbon hours
            low_hours = sorted_hours[:3]
            low_window = f"{min(h for h, _ in low_hours):02d}:00-{max(h for h, _ in low_hours)+1:02d}:00"
            avg_low_intensity = sum(d['avg_intensity'] for _, d in low_hours) / len(low_hours)
            
            # High carbon hours
            high_hours = sorted_hours[-3:]
            high_window = f"{min(h for h, _ in high_hours):02d}:00-{max(h for h, _ in high_hours)+1:02d}:00"
            avg_high_intensity = sum(d['avg_intensity'] for _, d in high_hours) / len(high_hours)
            total_high_emissions = sum(d['total_emissions'] for _, d in high_hours)
            
            # Calculate potential reduction
            potential_reduction_pct = ((avg_high_intensity - avg_low_intensity) / avg_high_intensity * 100) if avg_high_intensity > 0 else 0
            
            if potential_reduction_pct > 10:  # Only if significant
                insight = {
                    'type': 'time_analysis',
                    'service': 'Multi-Service',
                    'observation': f"Workloads execute during high-carbon periods with {potential_reduction_pct:.1f}% higher carbon intensity",
                    'evidence': {
                        'peak_carbon_window': high_window,
                        'peak_avg_intensity': round(avg_high_intensity, 2),
                        'peak_total_emissions': round(total_high_emissions, 4),
                        'low_carbon_window': low_window,
                        'low_avg_intensity': round(avg_low_intensity, 2),
                        'potential_reduction_pct': round(potential_reduction_pct, 2),
                        'affected_services': list(set(s for _, d in high_hours for s in d['services']))
                    },
                    'severity': 'high' if potential_reduction_pct > 30 else 'medium'
                }
                
                insights.append(insight)
        
        return insights
    
    def _generate_region_insights(self, records: List[Dict], analytics: Dict) -> List[Dict]:
        """Generate region-based insights with evidence"""
        insights = []
        
        # Analyze regional carbon intensity
        region_data = defaultdict(lambda: {
            'emissions': [],
            'intensities': [],
            'costs': [],
            'services': set()
        })
        
        for record in records:
            region = record['region']
            region_data[region]['emissions'].append(record['emissions_kg'])
            region_data[region]['intensities'].append(record['carbon_intensity'])
            region_data[region]['costs'].append(record['cost'])
            region_data[region]['services'].add(record['service'])
        
        # Calculate averages
        region_summary = {}
        for region, data in region_data.items():
            region_summary[region] = {
                'avg_intensity': sum(data['intensities']) / len(data['intensities']),
                'total_emissions': sum(data['emissions']),
                'total_cost': sum(data['costs']),
                'services': list(data['services'])
            }
        
        # Find high and low carbon regions
        if len(region_summary) >= 2:
            sorted_regions = sorted(region_summary.items(), key=lambda x: x[1]['avg_intensity'])
            
            lowest_region = sorted_regions[0]
            highest_region = sorted_regions[-1]
            
            # Calculate potential reduction
            intensity_diff = highest_region[1]['avg_intensity'] - lowest_region[1]['avg_intensity']
            potential_reduction_pct = (intensity_diff / highest_region[1]['avg_intensity'] * 100) if highest_region[1]['avg_intensity'] > 0 else 0
            
            if potential_reduction_pct > 15:  # Only if significant
                insight = {
                    'type': 'region_analysis',
                    'service': 'Multi-Service',
                    'observation': f"Region {highest_region[0]} has {potential_reduction_pct:.1f}% higher carbon intensity than {lowest_region[0]}",
                    'evidence': {
                        'high_carbon_region': highest_region[0],
                        'high_region_intensity': round(highest_region[1]['avg_intensity'], 2),
                        'high_region_emissions': round(highest_region[1]['total_emissions'], 4),
                        'low_carbon_region': lowest_region[0],
                        'low_region_intensity': round(lowest_region[1]['avg_intensity'], 2),
                        'potential_reduction_pct': round(potential_reduction_pct, 2),
                        'affected_services': highest_region[1]['services']
                    },
                    'severity': 'high' if potential_reduction_pct > 40 else 'medium'
                }
                
                insights.append(insight)
        
        return insights
    
    def _generate_cost_insights(self, records: List[Dict], analytics: Dict) -> List[Dict]:
        """Generate cost-efficiency insights"""
        insights = []
        
        # Calculate carbon per dollar for each service
        service_efficiency = defaultdict(lambda: {
            'emissions': 0,
            'cost': 0,
            'records': 0
        })
        
        for record in records:
            service = record['service']
            service_efficiency[service]['emissions'] += record['emissions_kg']
            service_efficiency[service]['cost'] += record['cost']
            service_efficiency[service]['records'] += 1
        
        # Find inefficient services (high emissions per dollar)
        efficiency_data = []
        for service, data in service_efficiency.items():
            if data['cost'] > 0:
                carbon_per_dollar = data['emissions'] / data['cost']
                efficiency_data.append({
                    'service': service,
                    'carbon_per_dollar': carbon_per_dollar,
                    'total_emissions': data['emissions'],
                    'total_cost': data['cost']
                })
        
        # Sort by carbon per dollar (descending)
        efficiency_data.sort(key=lambda x: x['carbon_per_dollar'], reverse=True)
        
        # Generate insight for most inefficient service
        if efficiency_data and efficiency_data[0]['carbon_per_dollar'] > 1:
            top_inefficient = efficiency_data[0]
            
            insight = {
                'type': 'cost_efficiency',
                'service': top_inefficient['service'],
                'observation': f"{top_inefficient['service']} has high carbon intensity relative to cost",
                'evidence': {
                    'carbon_per_dollar': round(top_inefficient['carbon_per_dollar'], 4),
                    'total_emissions': round(top_inefficient['total_emissions'], 4),
                    'total_cost': round(top_inefficient['total_cost'], 4)
                },
                'severity': 'medium'
            }
            
            insights.append(insight)
        
        return insights
    
    def get_stats(self) -> Dict:
        """Get insight generation statistics"""
        return {
            'insights_generated': self.insights_generated
        }
