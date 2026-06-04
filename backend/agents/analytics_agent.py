"""
AGENT 5: ANALYTICS AGENT
Purpose: Generate dashboard metrics and aggregations
"""
import logging
from typing import Dict, List
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class AnalyticsAgent:
    """Generates comprehensive analytics and dashboard metrics"""
    
    def __init__(self):
        self.processed_records = 0
    
    def generate_analytics(self, emission_records: List[Dict]) -> Dict:
        """
        Generate comprehensive dashboard analytics
        
        Args:
            emission_records: List of emission calculation results
        
        Returns: {
            total_emissions, total_cost, total_energy,
            service_breakdown, region_breakdown, time_series,
            top_service, top_region, highest_emission_workload
        }
        """
        if not emission_records:
            return self._empty_analytics()
        
        self.processed_records = len(emission_records)
        
        # Calculate totals
        total_emissions = sum(r['emissions_kg'] for r in emission_records)
        total_cost = sum(r.get('cost', 0) for r in emission_records)
        total_energy = sum(r['energy_kwh'] for r in emission_records)
        
        # Service breakdown
        service_breakdown = self._aggregate_by_service(emission_records)
        
        # Region breakdown
        region_breakdown = self._aggregate_by_region(emission_records)
        
        # Time series
        time_series = self._aggregate_by_time(emission_records)
        
        # Top contributors
        top_service = service_breakdown[0]['service'] if service_breakdown else 'None'
        top_region = region_breakdown[0]['region'] if region_breakdown else 'None'
        
        # Highest emission workload
        highest_workload = max(
            emission_records,
            key=lambda x: x['emissions_kg']
        )
        
        return {
            # Summary metrics
            'total_emissions_kg': round(total_emissions, 2),
            'total_cost': round(total_cost, 2),
            'total_energy_kwh': round(total_energy, 2),
            'top_service': top_service,
            'top_region': top_region,
            
            # Breakdowns
            'service_breakdown': service_breakdown,
            'region_breakdown': region_breakdown,
            'time_series': time_series,
            
            # Details
            'highest_emission_workload': {
                'service': highest_workload['service'],
                'region': highest_workload.get('region', 'Unknown'),
                'emissions_kg': round(highest_workload['emissions_kg'], 2),
                'cost': round(highest_workload.get('cost', 0), 2),
                'timestamp': highest_workload.get('timestamp', ''),
                'resource_id': highest_workload.get('resource_id', '')
            },
            
            # Metadata
            'record_count': self.processed_records,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _aggregate_by_service(self, records: List[Dict]) -> List[Dict]:
        """Aggregate emissions by service"""
        service_data = defaultdict(lambda: {
            'emissions_kg': 0,
            'cost': 0,
            'energy_kwh': 0,
            'usage_count': 0
        })
        
        for record in records:
            service = record['service']
            service_data[service]['emissions_kg'] += record['emissions_kg']
            service_data[service]['cost'] += record.get('cost', 0)
            service_data[service]['energy_kwh'] += record['energy_kwh']
            service_data[service]['usage_count'] += 1
        
        # Format results
        results = []
        for service, data in service_data.items():
            results.append({
                'service': service,
                'emissions_kg': round(data['emissions_kg'], 2),
                'cost': round(data['cost'], 2),
                'energy_kwh': round(data['energy_kwh'], 2),
                'usage_count': data['usage_count']
            })
        
        # Sort by emissions descending
        results.sort(key=lambda x: x['emissions_kg'], reverse=True)
        
        return results
    
    def _aggregate_by_region(self, records: List[Dict]) -> List[Dict]:
        """Aggregate emissions by region"""
        region_data = defaultdict(lambda: {
            'emissions_kg': 0,
            'cost': 0,
            'energy_kwh': 0,
            'zone': None,
            'avg_carbon_intensity': []
        })
        
        for record in records:
            region = record.get('region', 'Unknown')
            region_data[region]['emissions_kg'] += record['emissions_kg']
            region_data[region]['cost'] += record.get('cost', 0)
            region_data[region]['energy_kwh'] += record['energy_kwh']
            region_data[region]['zone'] = record.get('zone', '')
            region_data[region]['avg_carbon_intensity'].append(
                record['carbon_intensity']
            )
        
        # Format results
        results = []
        for region, data in region_data.items():
            avg_intensity = (
                sum(data['avg_carbon_intensity']) / len(data['avg_carbon_intensity'])
                if data['avg_carbon_intensity'] else 0
            )
            
            results.append({
                'region': region,
                'zone': data['zone'],
                'emissions_kg': round(data['emissions_kg'], 2),
                'cost': round(data['cost'], 2),
                'energy_kwh': round(data['energy_kwh'], 2),
                'avg_carbon_intensity': round(avg_intensity, 2)
            })
        
        # Sort by emissions descending
        results.sort(key=lambda x: x['emissions_kg'], reverse=True)
        
        return results
    
    def _aggregate_by_time(self, records: List[Dict]) -> List[Dict]:
        """Aggregate emissions by time (hourly)"""
        time_data = defaultdict(lambda: {
            'emissions_kg': 0,
            'cost': 0,
            'energy_kwh': 0,
            'avg_carbon_intensity': []
        })
        
        for record in records:
            timestamp = record.get('timestamp', '')
            if not timestamp:
                continue
            
            try:
                # Parse and round to hour
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour_key = dt.strftime('%Y-%m-%d %H:00')
                
                time_data[hour_key]['emissions_kg'] += record['emissions_kg']
                time_data[hour_key]['cost'] += record.get('cost', 0)
                time_data[hour_key]['energy_kwh'] += record['energy_kwh']
                time_data[hour_key]['avg_carbon_intensity'].append(
                    record['carbon_intensity']
                )
            except Exception as e:
                logger.warning(f"Invalid timestamp {timestamp}: {e}")
                continue
        
        # Format results
        results = []
        for hour, data in time_data.items():
            avg_intensity = (
                sum(data['avg_carbon_intensity']) / len(data['avg_carbon_intensity'])
                if data['avg_carbon_intensity'] else 0
            )
            
            results.append({
                'timestamp': hour,
                'emissions_kg': round(data['emissions_kg'], 2),
                'cost': round(data['cost'], 2),
                'energy_kwh': round(data['energy_kwh'], 2),
                'avg_carbon_intensity': round(avg_intensity, 2)
            })
        
        # Sort by timestamp
        results.sort(key=lambda x: x['timestamp'])
        
        return results
    
    def _empty_analytics(self) -> Dict:
        """Return empty analytics structure"""
        return {
            'total_emissions_kg': 0,
            'total_cost': 0,
            'total_energy_kwh': 0,
            'top_service': 'None',
            'top_region': 'None',
            'service_breakdown': [],
            'region_breakdown': [],
            'time_series': [],
            'highest_emission_workload': None,
            'record_count': 0,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def get_summary_stats(self) -> Dict:
        """Return summary statistics"""
        return {
            'processed_records': self.processed_records
        }
