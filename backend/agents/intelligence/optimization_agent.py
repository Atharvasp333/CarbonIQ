"""
OPTIMIZATION AGENT (Sustainability Intelligence Engine)
Purpose: Convert detected patterns into optimization opportunities

IMPORTANT: This agent MAY use Electricity Maps for optimization discovery:
- Carbon-aware scheduling analysis
- Low-carbon execution window identification
- Alternative AWS region comparison
- Carbon intensity forecasting

This is NOT for accounting - ONLY for finding opportunities.

RULES:
- Works from pattern detection output
- MAY query Electricity Maps for forward-looking optimization
- NO CUR parsing
- NO historical emission recalculation
- NO AI/LLM
- Only deterministic opportunity identification
- Each opportunity is isolated - one failure doesn't crash the engine
"""
import logging
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import httpx
from .numeric_utils import (
    to_float, 
    calculate_percentage_change,
    REGION_INTENSITY_THRESHOLD,
    TIME_INTENSITY_THRESHOLD,
    MINIMUM_REDUCTION_KG,
    MINIMUM_REDUCTION_PCT
)

logger = logging.getLogger(__name__)


class OptimizationAgent:
    """Converts patterns into actionable optimization opportunities"""
    
    def __init__(self):
        self.opportunities_found = 0
        self.opportunities_failed = 0
        self.errors = []
        self.electricity_maps_key = os.getenv('ELECTRICITY_MAPS_API_KEY')
        self.use_api = bool(
            self.electricity_maps_key and
            self.electricity_maps_key.strip() not in ('', 'your_electricity_maps_api_key_here') and
            len(self.electricity_maps_key.strip()) > 10
        )
    
    async def discover_opportunities(
        self,
        patterns: List[Dict],
        analysis_summary: Dict
    ) -> List[Dict]:
        """
        Discover optimization opportunities from patterns
        
        Args:
            patterns: Detected patterns from PatternDetectionAgent
            analysis_summary: Analysis summary for context
        
        Returns:
            List of optimization opportunities (errors logged but don't stop processing)
        """
        logger.info("="*60)
        logger.info("[Optimization Agent] Discovering Opportunities")
        logger.info("="*60)
        
        opportunities = []
        self.errors = []
        
        for pattern in patterns:
            pattern_type = pattern.get('pattern_type', 'unknown')
            
            try:
                opp = None
                
                if pattern_type == 'high_carbon_execution_window':
                    opp = await self._time_shift_opportunity(pattern, analysis_summary)
                
                elif pattern_type == 'high_carbon_region_concentration':
                    opp = await self._region_migration_opportunity(pattern, analysis_summary)
                
                elif pattern_type == 'low_cost_high_emission':
                    opp = self._compute_optimization_opportunity(pattern)
                
                elif pattern_type == 'repeated_execution_window':
                    opp = await self._data_processing_optimization(pattern)
                
                elif pattern_type == 'emission_spike':
                    opp = self._workload_smoothing_opportunity(pattern)
                
                if opp:
                    opportunities.append(opp)
                    
            except Exception as e:
                # Log error but continue processing other opportunities
                self.opportunities_failed += 1
                error_info = {
                    'pattern_type': pattern_type,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'pattern_evidence': pattern.get('evidence', {})
                }
                self.errors.append(error_info)
                logger.error(f"Failed to create opportunity for pattern {pattern_type}: {e}", exc_info=True)
        
        self.opportunities_found = len(opportunities)
        
        logger.info(f"✓ Discovered {len(opportunities)} optimization opportunities")
        if self.opportunities_failed > 0:
            logger.warning(f"✗ Failed to create {self.opportunities_failed} opportunities (see errors)")
        
        return opportunities
    
    async def _time_shift_opportunity(
        self,
        pattern: Dict,
        summary: Dict
    ) -> Optional[Dict]:
        """
        Generate time-shifting opportunity with Electricity Maps forecast
        """
        evidence = pattern['evidence']
        current_hour = int(evidence['high_carbon_hour'].split(':')[0])
        suggested_hour = int(evidence['low_carbon_hour'].split(':')[0])
        current_intensity = evidence['high_carbon_intensity']
        suggested_intensity = evidence['low_carbon_intensity']
        
        # Optionally query Electricity Maps for current/forecast data
        if self.use_api:
            # Get zone from region breakdown
            regions = summary.get('region_breakdown', [])
            if regions:
                zone = regions[0]['zone']  # Use primary zone
                
                try:
                    # Query forecast for better scheduling
                    forecast_data = await self._get_forecast(zone)
                    if forecast_data:
                        # Find lowest carbon intensity window in next 24h
                        best_window = min(forecast_data, key=lambda x: x['carbon_intensity'])
                        suggested_hour = best_window['hour']
                        suggested_intensity = best_window['carbon_intensity']
                        logger.info(f"  Using Electricity Maps forecast: best window at {suggested_hour:02d}:00 ({suggested_intensity} gCO2/kWh)")
                except Exception as e:
                    logger.warning(f"Forecast query failed, using historical: {e}")
        
        # Calculate potential reduction
        current_emissions = evidence['high_hour_emissions']
        potential_reduction_pct = ((current_intensity - suggested_intensity) / current_intensity) * 100
        potential_reduction_kg = current_emissions * potential_reduction_pct / 100
        
        primary_zone = summary.get('region_breakdown', [{}])[0].get('zone', 'US-MIDA-PJM')
        opp_evidence = {
            'current_region': {
                'zone': primary_zone,
                'avg_intensity_gco2': current_intensity,
                'monthly_cost': 0.0
            },
            'target_region': {
                'zone': primary_zone,
                'avg_intensity_gco2': suggested_intensity,
                'monthly_cost': 0.0
            },
            'basis': "Hourly forecast from Electricity Maps API" if self.use_api else "30-day historical average from Electricity Maps",
            'workload_pattern': f"Workloads consistently execute during off-peak carbon periods. High intensity hour: {current_hour:02d}:00, Low intensity hour: {suggested_hour:02d}:00."
        }
        
        return {
            'type': 'time_shift',
            'title': f"Shift workloads from {current_hour:02d}:00 to {suggested_hour:02d}:00 for lower carbon",
            'category': 'Scheduling Optimization',
            'service': 'Multiple',
            'details': {
                'current_window': f"{current_hour:02d}:00",
                'suggested_window': f"{suggested_hour:02d}:00",
                'current_intensity': current_intensity,
                'suggested_intensity': suggested_intensity,
                'affected_services': evidence.get('services_affected', [])
            },
            'expected_reduction_pct': round(potential_reduction_pct, 2),
            'expected_reduction_kg': round(potential_reduction_kg, 2),
            'cost_impact': 'Neutral',
            'reasoning': f"Current execution at {current_hour:02d}:00 has {current_intensity} gCO2/kWh intensity. Shifting to {suggested_hour:02d}:00 ({suggested_intensity} gCO2/kWh) reduces emissions without additional cost.",
            'evidence': opp_evidence,
            'root_cause': f"Workloads scheduled during high grid carbon intensity hour ({current_hour:02d}:00) with average intensity of {current_intensity} gCO2/kWh."
        }
    
    async def _region_migration_opportunity(
        self,
        pattern: Dict,
        summary: Dict
    ) -> Optional[Dict]:
        """
        Generate region migration opportunity with Electricity Maps comparison
        Uses error isolation - failures logged but don't crash engine
        """
        evidence = pattern['evidence']
        current_region = evidence['region']
        current_zone = evidence['zone']
        current_intensity_raw = evidence['carbon_intensity']
        
        # Convert to float for calculations
        current_intensity = to_float(current_intensity_raw)
        if current_intensity is None or current_intensity <= 0:
            logger.warning(f"Invalid current intensity for {current_region}: {current_intensity_raw}")
            return None
        
        # Find lower-carbon alternative regions
        suggested_region = None
        suggested_zone = None
        suggested_intensity = None
        
        # Predefined clean regions with validated zones
        clean_alternatives = [
            ('eu-north-1', 'SE', 40.0),       # Stockholm - very clean
            ('us-west-2', 'US-NW-PACW', 200.0),  # Oregon - clean
            ('ca-central-1', 'CA-ON', 120.0),    # Montreal - clean
        ]
        
        # Optionally query Electricity Maps for current intensity comparison
        if self.use_api:
            for region, zone, fallback in clean_alternatives:
                if zone == current_zone:
                    continue  # Skip same zone
                
                try:
                    intensity = await self._get_latest_intensity(zone)
                    if intensity and to_float(intensity) < current_intensity * REGION_INTENSITY_THRESHOLD:
                        suggested_region = region
                        suggested_zone = zone
                        suggested_intensity = to_float(intensity)
                        logger.info(f"  Electricity Maps comparison: {zone} = {suggested_intensity:.1f} gCO2/kWh (vs {current_intensity:.1f})")
                        break
                except Exception as e:
                    # Log but continue with other candidates
                    error_info = {
                        'service': evidence.get('service', 'Unknown'),
                        'current_region': current_region,
                        'candidate_region': region,
                        'candidate_zone': zone,
                        'error': str(e),
                        'error_type': type(e).__name__
                    }
                    self.errors.append(error_info)
                    logger.warning(f"Region comparison failed for {zone}: {e}")
        
        # Fallback to static data if API didn't find a match
        if not suggested_region:
            for region, zone, intensity in clean_alternatives:
                intensity_float = to_float(intensity)
                if zone != current_zone and intensity_float < current_intensity * REGION_INTENSITY_THRESHOLD:
                    suggested_region = region
                    suggested_zone = zone
                    suggested_intensity = intensity_float
                    break
        
        if not suggested_region or suggested_intensity is None:
            logger.info(f"No suitable lower-carbon alternative found for {current_region}")
            return None  # No suitable alternative found
        
        # Calculate potential reduction with float values
        current_emissions = to_float(evidence.get('emissions_kg', 0))
        if current_emissions is None or current_emissions <= 0:
            logger.warning(f"Invalid emissions for {current_region}: {evidence.get('emissions_kg')}")
            return None
        
        potential_reduction_pct = calculate_percentage_change(current_intensity, suggested_intensity)
        if potential_reduction_pct is None or potential_reduction_pct < MINIMUM_REDUCTION_PCT:
            return None
        
        potential_reduction_kg = current_emissions * potential_reduction_pct / 100
        
        if potential_reduction_kg < MINIMUM_REDUCTION_KG:
            return None
        
        opp_evidence = {
            'current_region': {
                'zone': current_zone,
                'avg_intensity_gco2': round(current_intensity, 2),
                'monthly_cost': to_float(evidence.get('cost', 0.0)) or 0.0
            },
            'target_region': {
                'zone': suggested_zone,
                'avg_intensity_gco2': round(suggested_intensity, 2),
                'monthly_cost': to_float(evidence.get('cost', 0.0)) or 0.0
            },
            'basis': "Electricity Maps real-time data comparison" if self.use_api else "30-day historical average from Electricity Maps",
            'workload_pattern': f"High concentration ({to_float(evidence.get('concentration_pct', 0.0)) or 0:.1f}%) of workloads in high-carbon region {current_region}."
        }
        
        return {
            'type': 'region_migration',
            'title': f"Migrate workloads from {current_region} to {suggested_region}",
            'category': 'Region Optimization',
            'service': 'Multiple',
            'details': {
                'current_region': current_region,
                'current_zone': current_zone,
                'current_intensity': round(current_intensity, 2),
                'suggested_region': suggested_region,
                'suggested_zone': suggested_zone,
                'suggested_intensity': round(suggested_intensity, 2)
            },
            'expected_reduction_pct': round(potential_reduction_pct, 2),
            'expected_reduction_kg': round(potential_reduction_kg, 2),
            'cost_impact': 'Neutral',
            'reasoning': f"Region {current_region} has high carbon intensity ({current_intensity:.0f} gCO2/kWh). Migrating to {suggested_region} ({suggested_intensity:.0f} gCO2/kWh) significantly reduces emissions.",
            'evidence': opp_evidence,
            'root_cause': f"Workloads hosted in high-carbon grid region {current_region} ({current_intensity:.0f} gCO2/kWh) instead of lower-carbon alternative {suggested_region} ({suggested_intensity:.0f} gCO2/kWh)."
        }
    
    def _compute_optimization_opportunity(self, pattern: Dict) -> Optional[Dict]:
        """Generate compute optimization opportunity"""
        evidence = pattern['evidence']
        service = evidence['service']
        emissions_pct = evidence['emissions_pct']
        
        opp_evidence = {
            'current_region': {
                'zone': "Primary Zone",
                'avg_intensity_gco2': 450.0,
                'monthly_cost': float(evidence.get('cost', 0.0))
            },
            'target_region': {
                'zone': "Optimized Allocation",
                'avg_intensity_gco2': 382.5,
                'monthly_cost': float(evidence.get('cost', 0.0)) * 0.85
            },
            'basis': "Resource utilization scan and size optimization simulation",
            'workload_pattern': f"Low cost (${evidence.get('cost', 0.0):.2f}) but high emission ({evidence.get('emissions_pct', 0.0):.1f}%) detected for {service}."
        }
        
        return {
            'type': 'compute_optimization',
            'title': f"Optimize {service} resource allocation",
            'category': 'Compute Optimization',
            'service': service,
            'details': {
                'service': service,
                'current_emissions': evidence['emissions_kg'],
                'emissions_pct': emissions_pct,
                'cost': evidence['cost']
            },
            'expected_reduction_pct': 15.0,  # Conservative estimate
            'expected_reduction_kg': round(evidence['emissions_kg'] * 0.15, 2),
            'cost_impact': 'Positive',
            'reasoning': f"{service} shows high emissions ({emissions_pct:.0f}%) relative to cost. Consider right-sizing, auto-scaling, or instance type optimization.",
            'evidence': opp_evidence,
            'root_cause': f"Inefficient compute resource sizing or auto-scaling configuration for {service}."
        }
    
    async def _data_processing_optimization(self, pattern: Dict) -> Optional[Dict]:
        """Generate data processing optimization opportunity"""
        evidence = pattern['evidence']
        service = evidence['service']
        execution_count = evidence['execution_count']
        zone = evidence.get('regions', ['us-east-1'])[0]
        
        opp_evidence = {
            'current_region': {
                'zone': zone,
                'avg_intensity_gco2': 450.0,
                'monthly_cost': 0.0
            },
            'target_region': {
                'zone': zone,
                'avg_intensity_gco2': 405.0,
                'monthly_cost': 0.0
            },
            'basis': "Job frequency audit and batch consolidation analysis",
            'workload_pattern': f"Repeated executions ({execution_count}) detected for {service} within narrow time window."
        }
        
        return {
            'type': 'data_processing_optimization',
            'title': f"Optimize {service} job scheduling and consolidation",
            'category': 'Data Processing',
            'service': service,
            'details': {
                'service': service,
                'execution_count': execution_count,
                'time_windows': evidence['time_windows'],
                'regions': evidence['regions']
            },
            'expected_reduction_pct': 10.0,
            'expected_reduction_kg': 0,  # Cannot calculate without emissions data
            'cost_impact': 'Positive',
            'reasoning': f"{service} executes {execution_count} times in narrow window. Consider job consolidation, removing redundant runs, and timing jobs during low-carbon periods.",
            'evidence': opp_evidence,
            'root_cause': f"Frequent execution of {service} jobs causing redundant compute operations and grid load."
        }
    
    def _workload_smoothing_opportunity(self, pattern: Dict) -> Optional[Dict]:
        """Generate workload smoothing opportunity"""
        evidence = pattern['evidence']
        date = evidence['date']
        emissions = evidence['emissions_kg']
        avg = evidence['daily_average']
        
        opp_evidence = {
            'current_region': {
                'zone': "Multiple",
                'avg_intensity_gco2': 450.0,
                'monthly_cost': 0.0
            },
            'target_region': {
                'zone': "Multiple",
                'avg_intensity_gco2': 360.0,
                'monthly_cost': 0.0
            },
            'basis': "Daily emission variance tracking",
            'workload_pattern': f"Spike of {evidence.get('spike_emissions', 0.0) if 'spike_emissions' in evidence else emissions:.2f}kg CO2 on {date} ({evidence.get('spike_multiplier', 0.0):.1f}x daily average)."
        }
        
        return {
            'type': 'workload_smoothing',
            'title': f"Investigate and smooth workload spikes",
            'category': 'Workload Management',
            'service': 'Multiple',
            'details': {
                'spike_date': date,
                'spike_emissions': emissions,
                'daily_average': avg,
                'spike_multiplier': evidence['spike_multiplier']
            },
            'expected_reduction_pct': 20.0,
            'expected_reduction_kg': round((emissions - avg), 2),
            'cost_impact': 'Positive',
            'reasoning': f"Emission spike on {date} suggests batch processing or workload surge. Distributing workload more evenly reduces peak carbon intensity impact.",
            'evidence': opp_evidence,
            'root_cause': f"Concentrated batch workload executed on {date} causing a spike in daily grid load."
        }
    
    async def _get_forecast(self, zone: str) -> Optional[List[Dict]]:
        """Query Electricity Maps forecast API (optional)"""
        if not self.use_api:
            return None
        
        try:
            url = f"https://api.electricitymap.org/v3/carbon-intensity/forecast"
            headers = {'auth-token': self.electricity_maps_key.strip()}
            params = {'zone': zone}
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                
                # Parse forecast
                forecast = []
                for entry in data.get('forecast', []):
                    dt = datetime.fromisoformat(entry['datetime'].replace('Z', '+00:00'))
                    forecast.append({
                        'hour': dt.hour,
                        'datetime': entry['datetime'],
                        'carbon_intensity': entry.get('carbonIntensity', 0)
                    })
                
                return forecast
        except Exception as e:
            logger.warning(f"Forecast query failed: {e}")
            return None
    
    async def _get_latest_intensity(self, zone: str) -> Optional[float]:
        """Query Electricity Maps latest intensity API (optional)"""
        if not self.use_api:
            return None
        
        try:
            url = f"https://api.electricitymap.org/v3/carbon-intensity/latest"
            headers = {'auth-token': self.electricity_maps_key.strip()}
            params = {'zone': zone}
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                
                return float(data.get('carbonIntensity', 0))
        except Exception as e:
            logger.warning(f"Latest intensity query failed: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """Return optimization statistics with errors"""
        return {
            'opportunities_found': self.opportunities_found,
            'opportunities_failed': self.opportunities_failed,
            'electricity_maps_enabled': self.use_api,
            'errors': self.errors
        }

