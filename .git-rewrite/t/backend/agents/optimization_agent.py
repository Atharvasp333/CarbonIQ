"""
AGENT 6: OPTIMIZATION AGENT
Purpose: Identify emission reduction opportunities
"""
import logging
from typing import Dict, List
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class OptimizationAgent:
    """Analyzes workloads and identifies emission reduction opportunities"""
    
    # Regional efficiency baseline (gCO2/kWh)
    REGION_EFFICIENCY = {
        'us-east-1': 415,
        'us-east-2': 744,
        'us-west-1': 285,
        'us-west-2': 220,
        'eu-west-1': 295,
        'eu-central-1': 338,
        'ap-south-1': 708,
        'ap-southeast-1': 493,
        'ap-northeast-1': 463,
    }
    
    def __init__(self):
        self.opportunities_found = 0
    
    def analyze_opportunities(
        self,
        emission_records: List[Dict],
        analytics: Dict
    ) -> Dict:
        """
        Analyze emissions data and generate optimization recommendations
        
        Returns: {
            findings: List of insights
            opportunities: List of actionable recommendations
            reduction_estimates: Potential savings
        }
        """
        if not emission_records:
            return self._empty_optimization()
        
        findings = []
        opportunities = []
        reduction_estimates = {
            'total_potential_reduction_kg': 0,
            'total_potential_cost_savings': 0
        }
        
        # 1. Region efficiency analysis
        region_opps = self._analyze_region_efficiency(
            emission_records, analytics
        )
        findings.extend(region_opps['findings'])
        opportunities.extend(region_opps['opportunities'])
        reduction_estimates['total_potential_reduction_kg'] += region_opps['reduction_kg']
        reduction_estimates['total_potential_cost_savings'] += region_opps['cost_savings']
        
        # 2. Time-based efficiency analysis
        time_opps = self._analyze_time_efficiency(
            emission_records, analytics
        )
        findings.extend(time_opps['findings'])
        opportunities.extend(time_opps['opportunities'])
        reduction_estimates['total_potential_reduction_kg'] += time_opps['reduction_kg']
        
        # 3. Service efficiency analysis
        service_opps = self._analyze_service_efficiency(
            emission_records, analytics
        )
        findings.extend(service_opps['findings'])
        opportunities.extend(service_opps['opportunities'])
        
        # 4. Heavy emitter identification
        heavy_emitters = self._identify_heavy_emitters(emission_records)
        findings.extend(heavy_emitters)
        
        self.opportunities_found = len(opportunities)
        
        return {
            'findings': findings,
            'opportunities': opportunities,
            'reduction_estimates': {
                'total_potential_reduction_kg': round(
                    reduction_estimates['total_potential_reduction_kg'], 2
                ),
                'total_potential_cost_savings': round(
                    reduction_estimates['total_potential_cost_savings'], 2
                ),
                'percentage_reduction': round(
                    (reduction_estimates['total_potential_reduction_kg'] / 
                     analytics['total_emissions_kg'] * 100)
                    if analytics['total_emissions_kg'] > 0 else 0,
                    1
                )
            },
            'priority_actions': self._prioritize_opportunities(opportunities),
            'analyzed_at': datetime.utcnow().isoformat()
        }
    
    def _analyze_region_efficiency(
        self,
        records: List[Dict],
        analytics: Dict
    ) -> Dict:
        """Analyze regional efficiency and suggest better regions"""
        findings = []
        opportunities = []
        reduction_kg = 0
        cost_savings = 0
        
        # Group by region
        region_data = defaultdict(lambda: {
            'emissions_kg': 0,
            'energy_kwh': 0,
            'cost': 0,
            'avg_intensity': []
        })
        
        for record in records:
            region = record.get('region', 'Unknown')
            region_data[region]['emissions_kg'] += record['emissions_kg']
            region_data[region]['energy_kwh'] += record['energy_kwh']
            region_data[region]['cost'] += record.get('cost', 0)
            region_data[region]['avg_intensity'].append(record['carbon_intensity'])
        
        # Find high carbon regions
        for region, data in region_data.items():
            avg_intensity = (
                sum(data['avg_intensity']) / len(data['avg_intensity'])
                if data['avg_intensity'] else 0
            )
            
            # Check if region has high carbon intensity (> 500 gCO2/kWh)
            if avg_intensity > 500:
                findings.append({
                    'type': 'high_carbon_region',
                    'severity': 'high',
                    'region': region,
                    'avg_carbon_intensity': round(avg_intensity, 2),
                    'emissions_kg': round(data['emissions_kg'], 2),
                    'message': f"Region {region} has high carbon intensity ({round(avg_intensity, 0)} gCO2/kWh)"
                })
                
                # Suggest cleaner regions
                clean_region, clean_intensity = self._find_cleaner_region(avg_intensity)
                if clean_region:
                    # Calculate potential savings
                    potential_reduction = (
                        data['energy_kwh'] * (avg_intensity - clean_intensity) / 1000
                    )
                    
                    opportunities.append({
                        'type': 'region_migration',
                        'priority': 'high',
                        'from_region': region,
                        'to_region': clean_region,
                        'current_intensity': round(avg_intensity, 0),
                        'target_intensity': round(clean_intensity, 0),
                        'reduction_kg': round(potential_reduction, 2),
                        'reduction_percentage': round(
                            (avg_intensity - clean_intensity) / avg_intensity * 100, 1
                        ),
                        'description': (
                            f"Migrate workloads from {region} to {clean_region} "
                            f"to reduce emissions by {round(potential_reduction, 1)}kg "
                            f"({round((avg_intensity - clean_intensity) / avg_intensity * 100, 0)}%)"
                        )
                    })
                    
                    reduction_kg += potential_reduction
                    cost_savings += data['cost'] * 0.15  # Assume 15% cost reduction
        
        return {
            'findings': findings,
            'opportunities': opportunities,
            'reduction_kg': reduction_kg,
            'cost_savings': cost_savings
        }
    
    def _analyze_time_efficiency(
        self,
        records: List[Dict],
        analytics: Dict
    ) -> Dict:
        """Analyze time-based patterns and suggest optimal execution windows"""
        findings = []
        opportunities = []
        reduction_kg = 0
        
        # Group by hour of day
        hour_data = defaultdict(lambda: {
            'emissions_kg': 0,
            'energy_kwh': 0,
            'avg_intensity': [],
            'count': 0
        })
        
        for record in records:
            timestamp = record.get('timestamp', '')
            if not timestamp:
                continue
            
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour = dt.hour
                
                hour_data[hour]['emissions_kg'] += record['emissions_kg']
                hour_data[hour]['energy_kwh'] += record['energy_kwh']
                hour_data[hour]['avg_intensity'].append(record['carbon_intensity'])
                hour_data[hour]['count'] += 1
            except Exception:
                continue
        
        if not hour_data:
            return {'findings': [], 'opportunities': [], 'reduction_kg': 0}
        
        # Calculate average intensity per hour
        hour_intensities = {}
        for hour, data in hour_data.items():
            hour_intensities[hour] = (
                sum(data['avg_intensity']) / len(data['avg_intensity'])
                if data['avg_intensity'] else 0
            )
        
        # Find peak and off-peak hours
        if hour_intensities:
            max_hour = max(hour_intensities, key=hour_intensities.get)
            min_hour = min(hour_intensities, key=hour_intensities.get)
            max_intensity = hour_intensities[max_hour]
            min_intensity = hour_intensities[min_hour]
            
            # If difference > 20%, suggest time shifting
            intensity_diff_pct = (
                (max_intensity - min_intensity) / max_intensity * 100
            )
            
            if intensity_diff_pct > 20:
                findings.append({
                    'type': 'time_pattern',
                    'severity': 'medium',
                    'peak_hour': max_hour,
                    'peak_intensity': round(max_intensity, 0),
                    'off_peak_hour': min_hour,
                    'off_peak_intensity': round(min_intensity, 0),
                    'message': (
                        f"Workloads executed at hour {max_hour}:00 had "
                        f"{round(intensity_diff_pct, 0)}% higher carbon intensity "
                        f"than hour {min_hour}:00"
                    )
                })
                
                # Calculate potential savings from shifting
                peak_energy = hour_data[max_hour]['energy_kwh']
                potential_reduction = (
                    peak_energy * (max_intensity - min_intensity) / 1000
                )
                
                opportunities.append({
                    'type': 'time_shifting',
                    'priority': 'medium',
                    'from_time': f"{max_hour}:00",
                    'to_time': f"{min_hour}:00",
                    'reduction_kg': round(potential_reduction, 2),
                    'description': (
                        f"Shift batch workloads from {max_hour}:00 to {min_hour}:00 "
                        f"to reduce emissions by {round(potential_reduction, 1)}kg "
                        f"({round(intensity_diff_pct, 0)}% reduction)"
                    )
                })
                
                reduction_kg += potential_reduction
        
        return {
            'findings': findings,
            'opportunities': opportunities,
            'reduction_kg': reduction_kg
        }
    
    def _analyze_service_efficiency(
        self,
        records: List[Dict],
        analytics: Dict
    ) -> Dict:
        """Analyze service efficiency"""
        findings = []
        opportunities = []
        
        # Get service breakdown
        service_breakdown = analytics.get('service_breakdown', [])
        
        for service_data in service_breakdown[:3]:  # Top 3 services
            service = service_data['service']
            emissions = service_data['emissions_kg']
            
            # Check if service is a heavy emitter (> 40% of total)
            percentage = (
                emissions / analytics['total_emissions_kg'] * 100
                if analytics['total_emissions_kg'] > 0 else 0
            )
            
            if percentage > 40:
                findings.append({
                    'type': 'service_concentration',
                    'severity': 'medium',
                    'service': service,
                    'emissions_kg': round(emissions, 2),
                    'percentage': round(percentage, 1),
                    'message': (
                        f"{service} accounts for {round(percentage, 0)}% "
                        f"of total emissions"
                    )
                })
                
                # Service-specific recommendations
                if service == 'EC2':
                    opportunities.append({
                        'type': 'service_optimization',
                        'priority': 'medium',
                        'service': service,
                        'description': (
                            f"Consider rightsizing EC2 instances, using Spot instances, "
                            f"or implementing auto-scaling to reduce {service} emissions"
                        )
                    })
                elif service == 'SageMaker':
                    opportunities.append({
                        'type': 'service_optimization',
                        'priority': 'medium',
                        'service': service,
                        'description': (
                            f"Schedule SageMaker training jobs during low carbon "
                            f"intensity hours to reduce emissions"
                        )
                    })
        
        return {
            'findings': findings,
            'opportunities': opportunities
        }
    
    def _identify_heavy_emitters(self, records: List[Dict]) -> List[Dict]:
        """Identify individual high-emission workloads"""
        findings = []
        
        # Sort by emissions
        sorted_records = sorted(
            records,
            key=lambda x: x['emissions_kg'],
            reverse=True
        )
        
        # Check top 3 emitters
        for i, record in enumerate(sorted_records[:3], 1):
            if record['emissions_kg'] > 1.0:  # > 1kg threshold
                findings.append({
                    'type': 'heavy_emitter',
                    'severity': 'high' if i == 1 else 'medium',
                    'rank': i,
                    'service': record['service'],
                    'region': record.get('region', 'Unknown'),
                    'emissions_kg': round(record['emissions_kg'], 2),
                    'resource_id': record.get('resource_id', ''),
                    'message': (
                        f"#{i} emitter: {record['service']} in "
                        f"{record.get('region', 'Unknown')} "
                        f"({round(record['emissions_kg'], 1)}kg CO2)"
                    )
                })
        
        return findings
    
    def _find_cleaner_region(self, current_intensity: float) -> tuple:
        """Find a cleaner region alternative"""
        # Find region with lowest intensity
        clean_regions = [
            ('us-west-2', 220),
            ('us-west-1', 285),
            ('eu-west-1', 295),
        ]
        
        for region, intensity in clean_regions:
            if intensity < current_intensity * 0.7:  # At least 30% cleaner
                return region, intensity
        
        return None, None
    
    def _prioritize_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """Prioritize opportunities by impact and feasibility"""
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        
        sorted_opps = sorted(
            opportunities,
            key=lambda x: (
                priority_order.get(x.get('priority', 'low'), 0),
                x.get('reduction_kg', 0)
            ),
            reverse=True
        )
        
        return sorted_opps[:5]  # Top 5 priorities
    
    def _empty_optimization(self) -> Dict:
        """Return empty optimization structure"""
        return {
            'findings': [],
            'opportunities': [],
            'reduction_estimates': {
                'total_potential_reduction_kg': 0,
                'total_potential_cost_savings': 0,
                'percentage_reduction': 0
            },
            'priority_actions': [],
            'analyzed_at': datetime.utcnow().isoformat()
        }
    
    def get_optimization_stats(self) -> Dict:
        """Return optimization statistics"""
        return {
            'opportunities_found': self.opportunities_found
        }
