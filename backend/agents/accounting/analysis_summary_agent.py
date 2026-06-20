"""
ANALYSIS SUMMARY AGENT (Carbon Accounting Engine)
Purpose: Generate aggregated analytics and store to database

Outputs:
- Service breakdown
- Region breakdown  
- Time-series data
- Top emission hotspots
- Summary statistics
"""
import logging
from typing import Dict, List
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class AnalysisSummaryAgent:
    """Generates comprehensive analytics from emission records"""
    
    def __init__(self):
        self.processed_records = 0
    
    def generate_summary(self, emission_records: List[Dict]) -> Dict:
        """
        Generate comprehensive summary analytics
        
        Args:
            emission_records: List of emission calculation results
        
        Returns:
            Complete analysis summary for storage and dashboard display
        """
        if not emission_records:
            return self._empty_summary()
        
        self.processed_records = len(emission_records)
        
        logger.info(f"[Analysis Summary Agent] Processing {len(emission_records)} emission records...")
        
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
        
        # Daily breakdown
        daily_breakdown = self._aggregate_by_day(emission_records)
        
        # Top hotspots
        top_hotspots = self._identify_hotspots(emission_records)
        
        # Top contributors
        top_service = service_breakdown[0]['service'] if service_breakdown else 'None'
        top_region = region_breakdown[0]['region'] if region_breakdown else 'None'
        
        summary = {
            # Summary metrics
            'total_emissions_kg': round(total_emissions, 2),
            'total_cost': round(total_cost, 2),
            'total_energy_kwh': round(total_energy, 2),
            'top_service': top_service,
            'top_region': top_region,
            'record_count': self.processed_records,
            'generated_at': datetime.utcnow().isoformat(),
            
            # Breakdowns
            'service_breakdown': service_breakdown,
            'region_breakdown': region_breakdown,
            'time_series': time_series,
            'daily_breakdown': daily_breakdown,
            'top_hotspots': top_hotspots,
        }
        
        logger.info(f"✓ Analysis summary generated")
        logger.info(f"  Total Emissions: {total_emissions:.2f}kg CO2")
        logger.info(f"  Total Cost: ${total_cost:.2f}")
        logger.info(f"  Services: {len(service_breakdown)}")
        logger.info(f"  Regions: {len(region_breakdown)}")
        
        return summary
    
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
        
        results = []
        for service, data in service_data.items():
            results.append({
                'service': service,
                'emissions_kg': round(data['emissions_kg'], 2),
                'cost': round(data['cost'], 2),
                'energy_kwh': round(data['energy_kwh'], 2),
                'usage_count': data['usage_count']
            })
        
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
            region_data[region]['avg_carbon_intensity'].append(record['carbon_intensity'])
        
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
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour_key = dt.strftime('%Y-%m-%d %H:00')
                
                time_data[hour_key]['emissions_kg'] += record['emissions_kg']
                time_data[hour_key]['cost'] += record.get('cost', 0)
                time_data[hour_key]['energy_kwh'] += record['energy_kwh']
                time_data[hour_key]['avg_carbon_intensity'].append(record['carbon_intensity'])
            except Exception as e:
                logger.warning(f"Invalid timestamp {timestamp}: {e}")
                continue
        
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
        
        results.sort(key=lambda x: x['timestamp'])
        return results
    
    def _aggregate_by_day(self, records: List[Dict]) -> List[Dict]:
        """Aggregate emissions by day"""
        daily_data = defaultdict(lambda: {
            'emissions_kg': 0,
            'cost': 0,
            'energy_kwh': 0,
            'count': 0
        })
        
        for record in records:
            timestamp = record.get('timestamp', '')
            if not timestamp:
                continue
            
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                day_key = dt.strftime('%Y-%m-%d')
                
                daily_data[day_key]['emissions_kg'] += record['emissions_kg']
                daily_data[day_key]['cost'] += record.get('cost', 0)
                daily_data[day_key]['energy_kwh'] += record['energy_kwh']
                daily_data[day_key]['count'] += 1
            except Exception:
                continue
        
        results = []
        for day, data in daily_data.items():
            results.append({
                'date': day,
                'emissions_kg': round(data['emissions_kg'], 2),
                'cost': round(data['cost'], 2),
                'energy_kwh': round(data['energy_kwh'], 2),
                'count': data['count']
            })
        
        results.sort(key=lambda x: x['date'])
        return results
    
    def _identify_hotspots(self, records: List[Dict], limit: int = 10) -> List[Dict]:
        """Identify top emission hotspots"""
        sorted_records = sorted(records, key=lambda x: x['emissions_kg'], reverse=True)
        
        hotspots = []
        for record in sorted_records[:limit]:
            hotspots.append({
                'service': record['service'],
                'region': record['region'],
                'zone': record['zone'],
                'timestamp': record['timestamp'],
                'emissions_kg': round(record['emissions_kg'], 2),
                'cost': round(record.get('cost', 0), 2),
                'carbon_intensity': record['carbon_intensity'],
                'energy_kwh': round(record['energy_kwh'], 2)
            })
        
        return hotspots
    
    def _empty_summary(self) -> Dict:
        """Return empty summary structure"""
        return {
            'total_emissions_kg': 0,
            'total_cost': 0,
            'total_energy_kwh': 0,
            'top_service': 'None',
            'top_region': 'None',
            'record_count': 0,
            'generated_at': datetime.utcnow().isoformat(),
            'service_breakdown': [],
            'region_breakdown': [],
            'time_series': [],
            'daily_breakdown': [],
            'top_hotspots': [],
        }
    
    def get_stats(self) -> Dict:
        """Return processing statistics"""
        return {
            'processed_records': self.processed_records
        }
