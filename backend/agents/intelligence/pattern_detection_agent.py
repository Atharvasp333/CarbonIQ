"""
PATTERN DETECTION AGENT (Sustainability Intelligence Engine)
Purpose: Find WHY emissions happen by detecting patterns in stored data

Reads from:
- analysis_summary
- emission_records (if needed for deep analysis)

Detects:
- Scheduling patterns
- Repeated execution windows
- High-carbon execution windows
- High-cost low-value services
- Carbon hotspots
- Region concentration
- Emission spikes
- Service inefficiencies

RULES:
- Works ONLY from stored accounting results
- NO CUR parsing
- NO emission calculations
- NO AI/LLM
- Only deterministic pattern detection
"""
import logging
from typing import Dict, List
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class PatternDetectionAgent:
    """Detects emission patterns and root causes from accounting data"""
    
    def __init__(self):
        self.patterns_found = 0
    
    def detect_patterns(
        self,
        analysis_summary: Dict,
        emission_records: List[Dict]
    ) -> List[Dict]:
        """
        Detect emission patterns from stored accounting data
        
        Args:
            analysis_summary: Precomputed summary from analysis_summary table
            emission_records: Detailed records from emission_records table (optional)
        
        Returns:
            List of detected patterns with evidence
        """
        logger.info("="*60)
        logger.info("[Pattern Detection Agent] Analyzing Patterns")
        logger.info("="*60)
        
        patterns = []
        
        # Pattern 1: High-carbon execution windows
        time_patterns = self._detect_time_patterns(analysis_summary, emission_records)
        patterns.extend(time_patterns)
        
        # Pattern 2: Region concentration
        region_patterns = self._detect_region_patterns(analysis_summary)
        patterns.extend(region_patterns)
        
        # Pattern 3: Service inefficiencies
        service_patterns = self._detect_service_patterns(analysis_summary, emission_records)
        patterns.extend(service_patterns)
        
        # Pattern 4: Emission spikes
        spike_patterns = self._detect_emission_spikes(analysis_summary)
        patterns.extend(spike_patterns)
        
        self.patterns_found = len(patterns)
        
        logger.info(f"✓ Detected {len(patterns)} patterns")
        logger.info(f"  Time patterns: {len(time_patterns)}")
        logger.info(f"  Region patterns: {len(region_patterns)}")
        logger.info(f"  Service patterns: {len(service_patterns)}")
        logger.info(f"  Spike patterns: {len(spike_patterns)}")
        
        return patterns
    
    def _detect_time_patterns(
        self,
        summary: Dict,
        records: List[Dict]
    ) -> List[Dict]:
        """Detect time-based emission patterns"""
        patterns = []
        
        # Analyze hourly breakdown
        if not records:
            return patterns
        
        # Group by hour of day
        hourly_data = defaultdict(lambda: {
            'emissions': 0,
            'count': 0,
            'intensity': [],
            'services': set()
        })
        
        for record in records:
            try:
                dt = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                hour = dt.hour
                
                hourly_data[hour]['emissions'] += record['emissions_kg']
                hourly_data[hour]['count'] += 1
                hourly_data[hour]['intensity'].append(record['carbon_intensity'])
                hourly_data[hour]['services'].add(record['service'])
            except Exception:
                continue
        
        if not hourly_data:
            return patterns
        
        # Calculate average intensity per hour
        hourly_intensity = {}
        for hour, data in hourly_data.items():
            hourly_intensity[hour] = sum(data['intensity']) / len(data['intensity'])
        
        # Find high vs low carbon hours
        max_hour = max(hourly_intensity, key=hourly_intensity.get)
        min_hour = min(hourly_intensity, key=hourly_intensity.get)
        max_intensity = hourly_intensity[max_hour]
        min_intensity = hourly_intensity[min_hour]
        
        # If difference > 20%, report pattern
        if (max_intensity - min_intensity) / max_intensity > 0.20:
            patterns.append({
                'pattern_type': 'high_carbon_execution_window',
                'service': 'Multiple',
                'observation': f"Workloads consistently execute during high-carbon hours ({max_hour:02d}:00)",
                'evidence': {
                    'high_carbon_hour': f"{max_hour:02d}:00",
                    'high_carbon_intensity': round(max_intensity, 2),
                    'low_carbon_hour': f"{min_hour:02d}:00",
                    'low_carbon_intensity': round(min_intensity, 2),
                    'intensity_difference': round(max_intensity - min_intensity, 2),
                    'high_hour_emissions': round(hourly_data[max_hour]['emissions'], 2),
                    'services_affected': list(hourly_data[max_hour]['services'])
                },
                'impact': f"{round((max_intensity - min_intensity) / max_intensity * 100, 1)}% higher carbon intensity during peak hours"
            })
        
        return patterns
    
    def _detect_region_patterns(self, summary: Dict) -> List[Dict]:
        """Detect region concentration patterns"""
        patterns = []
        
        region_breakdown = summary.get('region_breakdown', [])
        if not region_breakdown:
            return patterns
        
        total_emissions = sum(r['emissions_kg'] for r in region_breakdown)
        
        # Check for high-carbon region concentration
        for region_data in region_breakdown:
            concentration = (region_data['emissions_kg'] / total_emissions * 100) if total_emissions > 0 else 0
            intensity = region_data['avg_carbon_intensity']
            
            # High concentration in high-carbon region
            if concentration > 40 and intensity > 500:
                patterns.append({
                    'pattern_type': 'high_carbon_region_concentration',
                    'service': 'Multiple',
                    'observation': f"High concentration ({concentration:.0f}%) of workloads in high-carbon region {region_data['region']}",
                    'evidence': {
                        'region': region_data['region'],
                        'zone': region_data['zone'],
                        'concentration_pct': round(concentration, 1),
                        'carbon_intensity': intensity,
                        'emissions_kg': region_data['emissions_kg'],
                        'cost': region_data['cost']
                    },
                    'impact': f"{region_data['emissions_kg']:.1f}kg CO2 from single high-carbon region"
                })
        
        return patterns
    
    def _detect_service_patterns(
        self,
        summary: Dict,
        records: List[Dict]
    ) -> List[Dict]:
        """Detect service efficiency patterns"""
        patterns = []
        
        service_breakdown = summary.get('service_breakdown', [])
        if not service_breakdown:
            return patterns
        
        total_emissions = sum(s['emissions_kg'] for s in service_breakdown)
        
        # Check for high-emission low-cost services (inefficient)
        for service_data in service_breakdown:
            emissions_pct = (service_data['emissions_kg'] / total_emissions * 100) if total_emissions > 0 else 0
            cost = service_data['cost']
            
            # High emissions but relatively low cost suggests inefficiency
            if emissions_pct > 30 and cost < 10:
                patterns.append({
                    'pattern_type': 'low_cost_high_emission',
                    'service': service_data['service'],
                    'observation': f"{service_data['service']} generates {emissions_pct:.0f}% of emissions but only ${cost:.2f} cost",
                    'evidence': {
                        'service': service_data['service'],
                        'emissions_kg': service_data['emissions_kg'],
                        'emissions_pct': round(emissions_pct, 1),
                        'cost': cost,
                        'energy_kwh': service_data['energy_kwh'],
                        'usage_count': service_data['usage_count']
                    },
                    'impact': f"Potential over-provisioning or inefficient usage pattern"
                })
        
        # Check for repeated execution patterns (same service, many records)
        if records:
            service_frequency = defaultdict(lambda: {'count': 0, 'regions': set(), 'hours': set()})
            
            for record in records:
                service = record['service']
                try:
                    dt = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                    hour = dt.hour
                    service_frequency[service]['count'] += 1
                    service_frequency[service]['regions'].add(record['region'])
                    service_frequency[service]['hours'].add(hour)
                except Exception:
                    continue
            
            # Identify services with repeated executions in same time window
            for service, data in service_frequency.items():
                if data['count'] > 50 and len(data['hours']) < 3:
                    patterns.append({
                        'pattern_type': 'repeated_execution_window',
                        'service': service,
                        'observation': f"{service} executes {data['count']} times within narrow time window",
                        'evidence': {
                            'service': service,
                            'execution_count': data['count'],
                            'time_windows': len(data['hours']),
                            'regions': list(data['regions'])
                        },
                        'impact': f"Workload scheduling rigidity limits optimization opportunities"
                    })
        
        return patterns
    
    def _detect_emission_spikes(self, summary: Dict) -> List[Dict]:
        """Detect emission spikes from daily breakdown"""
        patterns = []
        
        daily_breakdown = summary.get('daily_breakdown', [])
        if not daily_breakdown or len(daily_breakdown) < 3:
            return patterns
        
        # Calculate average daily emissions
        avg_daily = sum(d['emissions_kg'] for d in daily_breakdown) / len(daily_breakdown)
        
        # Find days with > 2x average
        for day_data in daily_breakdown:
            if day_data['emissions_kg'] > avg_daily * 2:
                patterns.append({
                    'pattern_type': 'emission_spike',
                    'service': 'Multiple',
                    'observation': f"Emission spike on {day_data['date']}: {day_data['emissions_kg']:.1f}kg (2x daily average)",
                    'evidence': {
                        'date': day_data['date'],
                        'emissions_kg': day_data['emissions_kg'],
                        'daily_average': round(avg_daily, 2),
                        'spike_multiplier': round(day_data['emissions_kg'] / avg_daily, 1),
                        'cost': day_data['cost']
                    },
                    'impact': f"Unexpected workload surge or inefficient batch processing"
                })
        
        return patterns
    
    def get_stats(self) -> Dict:
        """Return pattern detection statistics"""
        return {
            'patterns_found': self.patterns_found
        }
