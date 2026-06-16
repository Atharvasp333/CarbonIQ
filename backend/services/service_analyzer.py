"""
Service-Level Deep Analytics
Generates detailed analytics for individual AWS services
"""
import logging
from typing import Dict, List
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class ServiceAnalyzer:
    """Analyzes individual service metrics in depth"""
    
    def __init__(self):
        self.service_recommendations = {
            'EC2': [
                'Consider right-sizing instances based on usage patterns',
                'Use Auto Scaling to match capacity with demand',
                'Switch to Spot Instances for non-critical workloads (up to 90% savings)',
                'Schedule batch jobs during low carbon intensity periods',
                'Evaluate ARM-based Graviton instances for better efficiency'
            ],
            'Lambda': [
                'Reduce excessive invocations with request batching',
                'Optimize memory allocation to match actual usage',
                'Use provisioned concurrency only when necessary',
                'Consolidate similar functions to reduce cold starts',
                'Review execution duration for optimization opportunities'
            ],
            'S3': [
                'Move infrequently accessed objects to Glacier or Glacier Deep Archive',
                'Enable S3 Intelligent-Tiering for automatic cost optimization',
                'Reduce cross-region data transfers',
                'Implement lifecycle policies to delete old data',
                'Use S3 Transfer Acceleration for better performance'
            ],
            'SageMaker': [
                'Schedule training jobs during low carbon intensity periods',
                'Use smaller instance families for development/testing',
                'Enable managed spot training for up to 90% savings',
                'Optimize hyperparameters to reduce training time',
                'Use SageMaker Inference Recommender for deployment'
            ],
            'RDS': [
                'Right-size database instances based on CPU/memory usage',
                'Use Aurora Serverless for variable workloads',
                'Enable automated backups during low-traffic periods',
                'Consider read replicas in lower-carbon regions',
                'Implement connection pooling to reduce overhead'
            ],
            'EBS': [
                'Delete unattached volumes',
                'Snapshot old volumes and delete originals',
                'Use gp3 volumes instead of gp2 for better price/performance',
                'Right-size volume capacity',
                'Enable EBS optimization on instances'
            ],
            'DynamoDB': [
                'Use on-demand capacity for unpredictable workloads',
                'Enable auto-scaling for provisioned capacity',
                'Archive old data to S3',
                'Use DynamoDB Accelerator (DAX) for read-heavy workloads',
                'Optimize partition key design'
            ]
        }
    
    def analyze_service(self, service_name: str, emission_records: List[Dict]) -> Dict:
        """
        Generate comprehensive service-level analytics
        
        Args:
            service_name: AWS service name (EC2, Lambda, etc.)
            emission_records: Full emission records from orchestrator
        
        Returns: Complete service analytics with all sections
        """
        # Filter records for this service (case-insensitive)
        service_records = [
            r for r in emission_records 
            if r.get('service', '').lower() == service_name.lower()
        ]
        
        # Use the canonical service name from records if found
        canonical_name = service_records[0]['service'] if service_records else service_name
        
        if not service_records:
            return self._empty_analytics(service_name)
        
        # Section 1: Service Summary
        summary = self._generate_summary(canonical_name, service_records)
        
        # Section 2: Execution Timeline
        timeline = self._generate_timeline(service_records)
        
        # Section 3: Run History
        run_history = self._generate_run_history(service_records)
        
        # Section 4: Region Breakdown
        region_breakdown = self._generate_region_breakdown(service_records)
        
        # Section 5: Carbon Intensity Analysis
        carbon_analysis = self._analyze_carbon_intensity(service_records)
        
        # Section 6: Peak Emission Events
        peak_events = self._identify_peak_events(service_records)
        
        # Section 7: Optimization Insights
        optimization = self._generate_service_recommendations(service_name, service_records)
        
        # Section 8: What-If Analysis
        whatif = self._generate_whatif_scenarios(service_name, service_records)
        
        return {
            'service_name': canonical_name,
            'summary': summary,
            'execution_timeline': timeline,
            'run_history': run_history,
            'region_breakdown': region_breakdown,
            'carbon_intensity_analysis': carbon_analysis,
            'peak_emission_events': peak_events,
            'optimization_insights': optimization,
            'whatif_scenarios': whatif,
            'total_records': len(service_records),
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _generate_summary(self, service_name: str, records: List[Dict]) -> Dict:
        """Section 1: Service Summary"""
        total_emissions = sum(r['emissions_kg'] for r in records)
        total_cost = sum(r.get('cost', 0) for r in records)
        total_usage = sum(r.get('usage_amount', 0) for r in records)
        
        # Calculate average carbon intensity
        intensities = [r['carbon_intensity'] for r in records]
        avg_intensity = sum(intensities) / len(intensities) if intensities else 0
        
        # Find most active region
        region_counts = defaultdict(int)
        for r in records:
            region_counts[r.get('region', 'Unknown')] += 1
        most_active_region = max(region_counts, key=region_counts.get) if region_counts else 'Unknown'
        
        return {
            'total_emissions_kg': round(total_emissions, 2),
            'total_cost': round(total_cost, 2),
            'total_usage': round(total_usage, 2),
            'average_carbon_intensity': round(avg_intensity, 2),
            'number_of_executions': len(records),
            'most_active_region': most_active_region,
            'time_range': {
                'start': min(r.get('timestamp', '') for r in records if r.get('timestamp')),
                'end': max(r.get('timestamp', '') for r in records if r.get('timestamp'))
            }
        }
    
    def _generate_timeline(self, records: List[Dict]) -> List[Dict]:
        """Section 2: Execution Timeline"""
        timeline = []
        
        for record in sorted(records, key=lambda x: x.get('timestamp', '')):
            timeline.append({
                'timestamp': record.get('timestamp', ''),
                'start_time': record.get('timestamp', ''),
                'end_time': record.get('timestamp', ''),  # Could use end_time if available
                'carbon_intensity': record['carbon_intensity'],
                'emissions_kg': round(record['emissions_kg'], 4),
                'region': record.get('region', 'Unknown'),
                'cost': round(record.get('cost', 0), 2)
            })
        
        return timeline
    
    def _generate_run_history(self, records: List[Dict]) -> List[Dict]:
        """Section 3: Run History Table"""
        history = []
        
        for record in sorted(records, key=lambda x: x.get('timestamp', ''), reverse=True):
            history.append({
                'timestamp': record.get('timestamp', ''),
                'start_time': record.get('timestamp', ''),
                'end_time': record.get('timestamp', ''),
                'region': record.get('region', 'Unknown'),
                'usage_type': record.get('usage_type', ''),
                'usage_amount': round(record.get('usage_amount', 0), 2),
                'cost': round(record.get('cost', 0), 2),
                'carbon_intensity': record['carbon_intensity'],
                'energy_kwh': round(record['energy_kwh'], 4),
                'emissions_kg': round(record['emissions_kg'], 4),
                'resource_id': record.get('resource_id', '')
            })
        
        return history
    
    def _generate_region_breakdown(self, records: List[Dict]) -> List[Dict]:
        """Section 4: Region Breakdown"""
        region_data = defaultdict(lambda: {
            'runs': 0,
            'usage': 0,
            'emissions_kg': 0,
            'cost': 0,
            'avg_carbon_intensity': []
        })
        
        for record in records:
            region = record.get('region', 'Unknown')
            region_data[region]['runs'] += 1
            region_data[region]['usage'] += record.get('usage_amount', 0)
            region_data[region]['emissions_kg'] += record['emissions_kg']
            region_data[region]['cost'] += record.get('cost', 0)
            region_data[region]['avg_carbon_intensity'].append(record['carbon_intensity'])
        
        breakdown = []
        for region, data in region_data.items():
            avg_intensity = (
                sum(data['avg_carbon_intensity']) / len(data['avg_carbon_intensity'])
                if data['avg_carbon_intensity'] else 0
            )
            
            breakdown.append({
                'region': region,
                'runs': data['runs'],
                'usage': round(data['usage'], 2),
                'emissions_kg': round(data['emissions_kg'], 2),
                'cost': round(data['cost'], 2),
                'avg_carbon_intensity': round(avg_intensity, 2)
            })
        
        # Sort by emissions descending
        breakdown.sort(key=lambda x: x['emissions_kg'], reverse=True)
        
        return breakdown
    
    def _analyze_carbon_intensity(self, records: List[Dict]) -> Dict:
        """Section 5: Carbon Intensity Analysis"""
        # Time series data
        time_series = []
        for record in sorted(records, key=lambda x: x.get('timestamp', '')):
            time_series.append({
                'timestamp': record.get('timestamp', ''),
                'carbon_intensity': record['carbon_intensity'],
                'emissions_kg': round(record['emissions_kg'], 4),
                'usage_amount': record.get('usage_amount', 0)
            })
        
        # Identify high/low carbon periods
        intensities = [r['carbon_intensity'] for r in records]
        avg_intensity = sum(intensities) / len(intensities) if intensities else 0
        
        high_carbon_periods = [
            {
                'timestamp': r.get('timestamp', ''),
                'carbon_intensity': r['carbon_intensity'],
                'region': r.get('region', '')
            }
            for r in records 
            if r['carbon_intensity'] > avg_intensity * 1.2
        ]
        
        low_carbon_periods = [
            {
                'timestamp': r.get('timestamp', ''),
                'carbon_intensity': r['carbon_intensity'],
                'region': r.get('region', '')
            }
            for r in records 
            if r['carbon_intensity'] < avg_intensity * 0.8
        ]
        
        return {
            'time_series': time_series,
            'average_intensity': round(avg_intensity, 2),
            'max_intensity': round(max(intensities), 2) if intensities else 0,
            'min_intensity': round(min(intensities), 2) if intensities else 0,
            'high_carbon_periods': high_carbon_periods[:10],
            'low_carbon_periods': low_carbon_periods[:10]
        }
    
    def _identify_peak_events(self, records: List[Dict]) -> List[Dict]:
        """Section 6: Peak Emission Events"""
        # Sort by emissions descending
        sorted_records = sorted(records, key=lambda x: x['emissions_kg'], reverse=True)
        
        peak_events = []
        for record in sorted_records[:10]:
            peak_events.append({
                'date': record.get('timestamp', '').split('T')[0] if record.get('timestamp') else '',
                'time': record.get('timestamp', ''),
                'region': record.get('region', 'Unknown'),
                'carbon_intensity': record['carbon_intensity'],
                'emissions_kg': round(record['emissions_kg'], 4),
                'cost': round(record.get('cost', 0), 2),
                'usage_amount': record.get('usage_amount', 0),
                'resource_id': record.get('resource_id', '')
            })
        
        return peak_events
    
    def _generate_service_recommendations(self, service_name: str, records: List[Dict]) -> Dict:
        """Section 7: Optimization Insights"""
        recommendations = self.service_recommendations.get(
            service_name,
            ['Optimize resource usage', 'Monitor performance metrics', 'Review cost allocation']
        )
        
        # Calculate potential savings
        total_emissions = sum(r['emissions_kg'] for r in records)
        total_cost = sum(r.get('cost', 0) for r in records)
        
        # Estimate savings potential based on best practices
        estimated_savings = {
            'emissions_reduction_kg': round(total_emissions * 0.25, 2),  # 25% potential
            'cost_reduction': round(total_cost * 0.20, 2),  # 20% potential
            'efficiency_gain_percentage': 25
        }
        
        return {
            'recommendations': recommendations,
            'estimated_savings': estimated_savings,
            'priority_actions': recommendations[:3]
        }
    
    def _generate_whatif_scenarios(self, service_name: str, records: List[Dict]) -> List[Dict]:
        """Section 8: What-If Analysis"""
        scenarios = []
        
        # Scenario 1: Region Migration
        region_data = defaultdict(lambda: {'emissions': 0, 'count': 0})
        for r in records:
            region = r.get('region', 'Unknown')
            region_data[region]['emissions'] += r['emissions_kg']
            region_data[region]['count'] += 1
        
        if region_data:
            current_region = max(region_data, key=lambda x: region_data[x]['emissions'])
            current_emissions = region_data[current_region]['emissions']
            
            # Suggest lower carbon region
            alternative_regions = {
                'us-east-1': ('us-west-2', 0.47),  # Oregon is ~47% cleaner
                'us-east-2': ('us-west-1', 0.62),  # California is ~62% cleaner
                'ap-south-1': ('eu-west-1', 0.58),  # Ireland is ~58% cleaner
            }
            
            if current_region in alternative_regions:
                alt_region, reduction = alternative_regions[current_region]
                scenarios.append({
                    'type': 'region_migration',
                    'title': 'Migrate to Lower-Carbon Region',
                    'current': current_region,
                    'alternative': alt_region,
                    'potential_reduction_percentage': round(reduction * 100, 0),
                    'potential_reduction_kg': round(current_emissions * reduction, 2)
                })
        
        # Scenario 2: Time Shifting
        # Check if there are high carbon periods
        intensities = [r['carbon_intensity'] for r in records]
        if intensities:
            max_intensity = max(intensities)
            min_intensity = min(intensities)
            
            if max_intensity > min_intensity * 1.3:  # More than 30% difference
                reduction_pct = ((max_intensity - min_intensity) / max_intensity) * 100
                total_emissions = sum(r['emissions_kg'] for r in records)
                
                scenarios.append({
                    'type': 'time_shifting',
                    'title': 'Shift to Low-Carbon Hours',
                    'current': 'Peak carbon hours',
                    'alternative': 'Off-peak carbon hours',
                    'potential_reduction_percentage': round(reduction_pct, 0),
                    'potential_reduction_kg': round(total_emissions * (reduction_pct / 100) * 0.5, 2)
                })
        
        # Scenario 3: Instance Right-Sizing (for compute services)
        if service_name in ['EC2', 'RDS', 'SageMaker']:
            total_emissions = sum(r['emissions_kg'] for r in records)
            total_cost = sum(r.get('cost', 0) for r in records)
            
            scenarios.append({
                'type': 'rightsizing',
                'title': 'Right-Size Instances',
                'current': 'Current instance sizes',
                'alternative': 'Optimized instances',
                'potential_reduction_percentage': 20,
                'potential_reduction_kg': round(total_emissions * 0.20, 2),
                'potential_cost_savings': round(total_cost * 0.20, 2)
            })
        
        return scenarios
    
    def _empty_analytics(self, service_name: str) -> Dict:
        """Return empty analytics structure"""
        return {
            'service_name': service_name,
            'summary': {
                'total_emissions_kg': 0,
                'total_cost': 0,
                'total_usage': 0,
                'average_carbon_intensity': 0,
                'number_of_executions': 0,
                'most_active_region': 'None'
            },
            'execution_timeline': [],
            'run_history': [],
            'region_breakdown': [],
            'carbon_intensity_analysis': {
                'time_series': [],
                'high_carbon_periods': [],
                'low_carbon_periods': []
            },
            'peak_emission_events': [],
            'optimization_insights': {
                'recommendations': [],
                'estimated_savings': {}
            },
            'whatif_scenarios': [],
            'total_records': 0
        }
