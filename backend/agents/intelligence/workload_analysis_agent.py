"""
WORKLOAD ANALYSIS AGENT
Primary intelligence layer for CarbonIQ sustainability recommendations

This agent analyzes emission data to identify:
- Top emitting services and regions
- Carbon hotspots (high emission events)
- Time-based patterns (peak/low carbon windows)
- Region shift opportunities
- Time shift opportunities

PURE DETERMINISTIC ANALYTICS - NO AI/LLM
"""
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class WorkloadAnalysisAgent:
    """
    Analyzes workload emission data to generate sustainability insights
    """
    
    def __init__(self):
        self.analysis_stats = {
            'records_analyzed': 0,
            'services_identified': 0,
            'regions_identified': 0,
            'hotspots_found': 0,
            'opportunities_identified': 0
        }
    
    def analyze(
        self,
        emission_records: List[Dict],
        cur_data: List[Dict],
        analytics: Dict
    ) -> Dict:
        """
        Comprehensive workload analysis
        
        Args:
            emission_records: Calculated emissions from EmissionCalculationAgent
            cur_data: Raw CUR data from IngestionAgent
            analytics: Analytics from AnalyticsAgent
        
        Returns:
            Structured insights object with all analysis results
        """
        logger.info("="*60)
        logger.info("[Workload Analysis Agent] Starting Analysis")
        logger.info("="*60)
        
        self.analysis_stats['records_analyzed'] = len(emission_records)
        
        # Service Analysis
        service_analysis = self._analyze_services(emission_records)
        self.analysis_stats['services_identified'] = len(service_analysis['top_services'])
        
        # Region Analysis
        region_analysis = self._analyze_regions(emission_records)
        self.analysis_stats['regions_identified'] = len(region_analysis['top_regions'])
        
        # Time Analysis
        time_analysis = self._analyze_time_patterns(emission_records)
        
        # Carbon Hotspots
        hotspots = self._identify_hotspots(emission_records)
        self.analysis_stats['hotspots_found'] = len(hotspots)
        
        # Service Utilization Patterns
        utilization = self._analyze_utilization(emission_records)
        
        # Region Shift Opportunities
        region_opportunities = self._find_region_opportunities(emission_records, region_analysis)
        
        # Time Shift Opportunities
        time_opportunities = self._find_time_opportunities(emission_records, time_analysis)
        
        self.analysis_stats['opportunities_identified'] = (
            len(region_opportunities) + len(time_opportunities)
        )
        
        logger.info(f"✓ Analysis Complete:")
        logger.info(f"  Services Analyzed: {self.analysis_stats['services_identified']}")
        logger.info(f"  Regions Analyzed: {self.analysis_stats['regions_identified']}")
        logger.info(f"  Hotspots Found: {self.analysis_stats['hotspots_found']}")
        logger.info(f"  Opportunities: {self.analysis_stats['opportunities_identified']}")
        
        return {
            'service_analysis': service_analysis,
            'region_analysis': region_analysis,
            'time_analysis': time_analysis,
            'hotspots': hotspots,
            'utilization': utilization,
            'region_opportunities': region_opportunities,
            'time_opportunities': time_opportunities,
            'stats': self.analysis_stats.copy()
        }
    
    def _analyze_services(self, records: List[Dict]) -> Dict:
        """Analyze service-level emissions with detailed evidence"""
        service_data = defaultdict(lambda: {
            'total_emissions': 0,
            'total_cost': 0,
            'total_energy': 0,
            'count': 0,
            'avg_emissions': 0,
            'regions': set(),
            'zones': set(),
            'carbon_intensities': [],
            'execution_dates': [],
            'resource_ids': set()
        })
        
        total_emissions = sum(float(r['emissions_kg']) for r in records)
        
        for record in records:
            service = record['service']
            service_data[service]['total_emissions'] += float(record['emissions_kg'])
            service_data[service]['total_cost'] += float(record['cost'])
            service_data[service]['total_energy'] += float(record['energy_kwh'])
            service_data[service]['count'] += 1
            service_data[service]['regions'].add(record['region'])
            service_data[service]['zones'].add(record['zone'])
            service_data[service]['carbon_intensities'].append(float(record['carbon_intensity']))
            service_data[service]['resource_ids'].add(record.get('resource_id', ''))
            
            # Track execution dates
            # Handle both timestamp (from API) and record_date (from DB)
            timestamp_val = record.get('timestamp') or record.get('record_date')
            if timestamp_val:
                try:
                    if isinstance(timestamp_val, str):
                        dt = datetime.fromisoformat(timestamp_val.replace('Z', '+00:00'))
                    else:
                        # Already a date/datetime object
                        dt = timestamp_val if isinstance(timestamp_val, datetime) else datetime.combine(timestamp_val, datetime.min.time())
                    service_data[service]['execution_dates'].append(dt)
                except Exception:
                    pass
        
        # Calculate averages, percentages, and evidence
        for service, data in service_data.items():
            data['avg_emissions'] = data['total_emissions'] / data['count']
            data['percentage'] = (data['total_emissions'] / total_emissions * 100) if total_emissions > 0 else 0
            
            # Evidence calculations
            if data['carbon_intensities']:
                data['avg_carbon_intensity'] = sum(data['carbon_intensities']) / len(data['carbon_intensities'])
                data['min_carbon_intensity'] = min(data['carbon_intensities'])
                data['max_carbon_intensity'] = max(data['carbon_intensities'])
            else:
                data['avg_carbon_intensity'] = 0
                data['min_carbon_intensity'] = 0
                data['max_carbon_intensity'] = 0
            
            # Convert sets to lists for JSON serialization
            data['regions'] = list(data['regions'])
            data['zones'] = list(data['zones'])
            data['resource_ids'] = list(data['resource_ids'])
            
            # Keep only summary of dates (first, last, count)
            if data['execution_dates']:
                data['first_execution'] = min(data['execution_dates']).isoformat()
                data['last_execution'] = max(data['execution_dates']).isoformat()
            del data['execution_dates']  # Remove to avoid bloat
            del data['carbon_intensities']  # Keep only aggregates
        
        # Sort by total emissions
        top_services = sorted(
            [{'service': s, **d} for s, d in service_data.items()],
            key=lambda x: x['total_emissions'],
            reverse=True
        )[:10]
        
        return {
            'total_services': len(service_data),
            'top_services': top_services,
            'service_breakdown': dict(service_data)
        }
    
    def _analyze_regions(self, records: List[Dict]) -> Dict:
        """Analyze region-level emissions and carbon intensity"""
        region_data = defaultdict(lambda: {
            'total_emissions': 0,
            'total_cost': 0,
            'total_energy': 0,
            'count': 0,
            'avg_carbon_intensity': 0,
            'carbon_intensities': []
        })
        
        total_emissions = sum(float(r['emissions_kg']) for r in records)
        
        for record in records:
            region = record['region']
            region_data[region]['total_emissions'] += float(record['emissions_kg'])
            region_data[region]['total_cost'] += float(record['cost'])
            region_data[region]['total_energy'] += float(record['energy_kwh'])
            region_data[region]['count'] += 1
            region_data[region]['carbon_intensities'].append(float(record['carbon_intensity']))
        
        # Calculate averages
        for region, data in region_data.items():
            data['avg_carbon_intensity'] = sum(data['carbon_intensities']) / len(data['carbon_intensities'])
            data['percentage'] = (data['total_emissions'] / total_emissions * 100) if total_emissions > 0 else 0
            del data['carbon_intensities']  # Remove raw list
        
        # Sort by emissions
        top_regions = sorted(
            [{'region': r, **d} for r, d in region_data.items()],
            key=lambda x: x['total_emissions'],
            reverse=True
        )[:10]
        
        # Find highest and lowest carbon intensity regions
        all_regions = [{'region': r, **d} for r, d in region_data.items()]
        highest_intensity_region = max(all_regions, key=lambda x: x['avg_carbon_intensity']) if all_regions else None
        lowest_intensity_region = min(all_regions, key=lambda x: x['avg_carbon_intensity']) if all_regions else None
        
        return {
            'total_regions': len(region_data),
            'top_regions': top_regions,
            'highest_intensity_region': highest_intensity_region,
            'lowest_intensity_region': lowest_intensity_region,
            'region_breakdown': dict(region_data)
        }
    
    def _analyze_time_patterns(self, records: List[Dict]) -> Dict:
        """Analyze time-based emission patterns with detailed execution windows"""
        # Group by hour, day, week, month
        hourly_data = defaultdict(lambda: {
            'emissions': 0, 
            'count': 0, 
            'avg_intensity': 0, 
            'intensities': [],
            'services': set()
        })
        daily_data = defaultdict(lambda: {'emissions': 0, 'count': 0})
        monthly_data = defaultdict(lambda: {'emissions': 0, 'count': 0})
        
        # Track service-specific execution windows
        service_time_windows = defaultdict(lambda: defaultdict(lambda: {
            'count': 0,
            'emissions': 0,
            'intensities': []
        }))
        
        for record in records:
            # Handle both timestamp (from API) and record_date (from DB)
            timestamp_val = record.get('timestamp') or record.get('record_date')
            if not timestamp_val:
                continue
                
            try:
                if isinstance(timestamp_val, str):
                    dt = datetime.fromisoformat(timestamp_val.replace('Z', '+00:00'))
                else:
                    # Already a date/datetime object
                    dt = timestamp_val if isinstance(timestamp_val, datetime) else datetime.combine(timestamp_val, datetime.min.time())
                
                hour = dt.hour
                date = dt.date()
                month = dt.strftime('%Y-%m')
                service = record['service']
                
                hourly_data[hour]['emissions'] += float(record['emissions_kg'])
                hourly_data[hour]['count'] += 1
                hourly_data[hour]['intensities'].append(float(record['carbon_intensity']))
                hourly_data[hour]['services'].add(service)
                
                daily_data[str(date)]['emissions'] += float(record['emissions_kg'])
                daily_data[str(date)]['count'] += 1
                
                monthly_data[month]['emissions'] += float(record['emissions_kg'])
                monthly_data[month]['count'] += 1
                
                # Track service time windows
                service_time_windows[service][hour]['count'] += 1
                service_time_windows[service][hour]['emissions'] += float(record['emissions_kg'])
                service_time_windows[service][hour]['intensities'].append(float(record['carbon_intensity']))
                
            except Exception as e:
                logger.warning(f"Failed to parse timestamp: {timestamp_val} - {e}")
                continue
        
        # Calculate hourly averages with evidence
        for hour, data in hourly_data.items():
            if data['intensities']:
                data['avg_intensity'] = sum(data['intensities']) / len(data['intensities'])
                data['min_intensity'] = min(data['intensities'])
                data['max_intensity'] = max(data['intensities'])
            else:
                data['avg_intensity'] = 0
                data['min_intensity'] = 0
                data['max_intensity'] = 0
            
            data['services'] = list(data['services'])
            del data['intensities']
        
        # Calculate service time window evidence
        service_execution_patterns = {}
        for service, hours in service_time_windows.items():
            # Find primary execution window
            if hours:
                most_common_hour = max(hours.items(), key=lambda x: x[1]['count'])
                avg_intensities = {
                    h: sum(d['intensities']) / len(d['intensities']) if d['intensities'] else 0 
                    for h, d in hours.items()
                }
                
                service_execution_patterns[service] = {
                    'primary_hour': most_common_hour[0],
                    'primary_hour_executions': most_common_hour[1]['count'],
                    'primary_hour_emissions': most_common_hour[1]['emissions'],
                    'primary_hour_intensity': avg_intensities[most_common_hour[0]],
                    'hourly_distribution': {h: d['count'] for h, d in hours.items()},
                    'hourly_intensities': avg_intensities
                }
        
        # Find peak and low carbon hours
        hourly_sorted = sorted(hourly_data.items(), key=lambda x: x[1]['avg_intensity'])
        lowest_carbon_hours = [{'hour': h, **d} for h, d in hourly_sorted[:5]]
        highest_carbon_hours = [{'hour': h, **d} for h, d in hourly_sorted[-5:]]
        
        # Find highest emission days
        daily_sorted = sorted(daily_data.items(), key=lambda x: x[1]['emissions'], reverse=True)
        highest_emission_days = [{'date': d, **data} for d, data in daily_sorted[:10]]
        
        # Find highest emission months
        monthly_sorted = sorted(monthly_data.items(), key=lambda x: x[1]['emissions'], reverse=True)
        highest_emission_months = [{'month': m, **data} for m, data in monthly_sorted[:6]]
        
        return {
            'hourly_breakdown': dict(hourly_data),
            'daily_breakdown': dict(daily_data),
            'monthly_breakdown': dict(monthly_data),
            'service_execution_patterns': service_execution_patterns,
            'lowest_carbon_hours': lowest_carbon_hours,
            'highest_carbon_hours': highest_carbon_hours,
            'highest_emission_days': highest_emission_days,
            'highest_emission_months': highest_emission_months
        }
    
    def _identify_hotspots(self, records: List[Dict]) -> List[Dict]:
        """Identify top 10 carbon hotspot events"""
        # Sort by emissions
        sorted_records = sorted(records, key=lambda x: x['emissions_kg'], reverse=True)
        
        hotspots = []
        for record in sorted_records[:10]:
            # Handle both timestamp (from API) and record_date (from DB)
            timestamp_val = record.get('timestamp') or record.get('record_date')
            if timestamp_val:
                if isinstance(timestamp_val, str):
                    timestamp_str = timestamp_val
                else:
                    # Convert date/datetime to ISO string
                    timestamp_str = timestamp_val.isoformat() if hasattr(timestamp_val, 'isoformat') else str(timestamp_val)
            else:
                timestamp_str = 'Unknown'
            
            hotspots.append({
                'service': record['service'],
                'region': record['region'],
                'zone': record['zone'],
                'timestamp': timestamp_str,
                'emissions_kg': float(record['emissions_kg']),
                'cost': float(record['cost']),
                'carbon_intensity': float(record['carbon_intensity']),
                'energy_kwh': float(record['energy_kwh'])
            })
        
        return hotspots
    
    def _analyze_utilization(self, records: List[Dict]) -> Dict:
        """Analyze service utilization patterns"""
        service_usage = defaultdict(lambda: {
            'total_usage': 0,
            'total_emissions': 0,
            'total_cost': 0,
            'count': 0,
            'efficiency': 0  # emissions per usage unit
        })
        
        for record in records:
            service = record['service']
            service_usage[service]['total_usage'] += float(record['usage_amount'])
            service_usage[service]['total_emissions'] += float(record['emissions_kg'])
            service_usage[service]['total_cost'] += float(record['cost'])
            service_usage[service]['count'] += 1
        
        # Calculate efficiency
        for service, data in service_usage.items():
            if data['total_usage'] > 0:
                data['efficiency'] = data['total_emissions'] / data['total_usage']
        
        # Identify inefficient services (high carbon per usage)
        inefficient = sorted(
            [{'service': s, **d} for s, d in service_usage.items()],
            key=lambda x: x['efficiency'],
            reverse=True
        )[:5]
        
        # Identify frequently running services
        frequent = sorted(
            [{'service': s, **d} for s, d in service_usage.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]
        
        return {
            'service_usage': dict(service_usage),
            'inefficient_services': inefficient,
            'frequently_running': frequent
        }
    
    def _find_region_opportunities(self, records: List[Dict], region_analysis: Dict) -> List[Dict]:
        """Identify region migration opportunities"""
        opportunities = []
        
        # Get current region distribution
        region_breakdown = region_analysis['region_breakdown']
        lowest_intensity = region_analysis.get('lowest_intensity_region')
        
        if not lowest_intensity:
            return []
        
        # For each high-emission region, calculate potential savings
        for region, data in region_breakdown.items():
            current_intensity = float(data['avg_carbon_intensity'])
            target_intensity = float(lowest_intensity['avg_carbon_intensity'])
            
            # Skip if already low carbon
            if current_intensity <= target_intensity * 1.1:  # Within 10% tolerance
                continue
            
            # Calculate potential reduction
            potential_reduction_pct = ((current_intensity - target_intensity) / current_intensity) * 100
            potential_savings_kg = (float(data['total_emissions']) * potential_reduction_pct) / 100
            
            # Only include significant opportunities
            if potential_reduction_pct > 10 and potential_savings_kg > 5:
                opportunities.append({
                    'current_region': region,
                    'suggested_region': lowest_intensity['region'],
                    'current_intensity': round(current_intensity, 2),
                    'suggested_intensity': round(target_intensity, 2),
                    'potential_reduction_pct': round(potential_reduction_pct, 2),
                    'potential_savings_kg': round(potential_savings_kg, 2),
                    'current_emissions': round(float(data['total_emissions']), 2),
                    'current_cost': round(float(data['total_cost']), 2)
                })
        
        # Sort by potential savings
        opportunities.sort(key=lambda x: x['potential_savings_kg'], reverse=True)
        
        return opportunities[:10]
    
    def _find_time_opportunities(self, records: List[Dict], time_analysis: Dict) -> List[Dict]:
        """Identify time-shift opportunities"""
        opportunities = []
        
        # Get hourly breakdown
        hourly_breakdown = time_analysis['hourly_breakdown']
        lowest_hours = time_analysis['lowest_carbon_hours']
        
        if not lowest_hours:
            return []
        
        # Find services running during high-carbon hours
        service_time_data = defaultdict(lambda: defaultdict(lambda: {
            'emissions': 0,
            'count': 0,
            'avg_intensity': 0,
            'intensities': []
        }))
        
        for record in records:
            # Handle both timestamp (from API) and record_date (from DB)
            timestamp_val = record.get('timestamp') or record.get('record_date')
            if not timestamp_val:
                continue
                
            try:
                if isinstance(timestamp_val, str):
                    dt = datetime.fromisoformat(timestamp_val.replace('Z', '+00:00'))
                else:
                    # Already a date/datetime object
                    dt = timestamp_val if isinstance(timestamp_val, datetime) else datetime.combine(timestamp_val, datetime.min.time())
                
                hour = dt.hour
                service = record['service']
                region = record['region']
                
                key = f"{service}_{region}"
                service_time_data[key][hour]['emissions'] += float(record['emissions_kg'])
                service_time_data[key][hour]['count'] += 1
                service_time_data[key][hour]['intensities'].append(float(record['carbon_intensity']))
            except Exception as e:
                logger.warning(f"Failed to parse timestamp in time opportunities: {timestamp_val} - {e}")
                continue
        
        # Calculate averages
        for key, hours in service_time_data.items():
            for hour, data in hours.items():
                if data['intensities']:
                    data['avg_intensity'] = sum(data['intensities']) / len(data['intensities'])
        
        # Find shift opportunities
        best_hour = lowest_hours[0]['hour']
        best_intensity = float(lowest_hours[0]['avg_intensity'])
        
        for key, hours in service_time_data.items():
            service, region = key.split('_', 1)
            
            # Calculate current average intensity
            total_emissions = sum(h['emissions'] for h in hours.values())
            avg_current_intensity = sum(
                h['avg_intensity'] * h['count'] for h in hours.values()
            ) / sum(h['count'] for h in hours.values()) if hours else 0
            
            # Calculate potential reduction
            if avg_current_intensity > best_intensity * 1.15:  # At least 15% higher
                potential_reduction_pct = ((avg_current_intensity - best_intensity) / avg_current_intensity) * 100
                potential_savings_kg = (total_emissions * potential_reduction_pct) / 100
                
                if potential_savings_kg > 5:  # Significant savings
                    opportunities.append({
                        'service': service,
                        'region': region,
                        'current_avg_intensity': round(avg_current_intensity, 2),
                        'suggested_avg_intensity': round(best_intensity, 2),
                        'suggested_time_window': f"{best_hour:02d}:00-{(best_hour+1)%24:02d}:00 UTC",
                        'potential_reduction_pct': round(potential_reduction_pct, 2),
                        'potential_savings_kg': round(potential_savings_kg, 2),
                        'current_emissions': round(total_emissions, 2)
                    })
        
        # Sort by potential savings
        opportunities.sort(key=lambda x: x['potential_savings_kg'], reverse=True)
        
        return opportunities[:10]
    
    def get_analysis_stats(self) -> Dict:
        """Get analysis statistics"""
        return self.analysis_stats.copy()
