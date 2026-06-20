"""
SHARED DATA MODELS
Common data structures used across accounting and intelligence engines
"""
from typing import Dict, List, Optional
from datetime import datetime


class NormalizedRecord:
    """Normalized CUR record after ingestion and compression"""
    def __init__(
        self,
        service: str,
        region: str,
        location: str,
        product_family: str,
        usage_type: str,
        operation: str,
        usage_amount: float,
        cost: float,
        start_time: str,
        end_time: str,
        resource_id: str = '',
        zone: str = '',
        location_name: str = ''
    ):
        self.service = service
        self.region = region
        self.location = location
        self.product_family = product_family
        self.usage_type = usage_type
        self.operation = operation
        self.usage_amount = usage_amount
        self.cost = cost
        self.start_time = start_time
        self.end_time = end_time
        self.resource_id = resource_id
        self.zone = zone
        self.location_name = location_name


class EmissionRecord:
    """Calculated emission record from accounting engine"""
    def __init__(
        self,
        service: str,
        region: str,
        zone: str,
        timestamp: str,
        usage_amount: float,
        cost: float,
        energy_kwh: float,
        carbon_intensity: float,
        emissions_kg: float,
        usage_type: str = '',
        resource_id: str = '',
        intensity_source: str = ''
    ):
        self.service = service
        self.region = region
        self.zone = zone
        self.timestamp = timestamp
        self.usage_amount = usage_amount
        self.cost = cost
        self.energy_kwh = energy_kwh
        self.carbon_intensity = carbon_intensity
        self.emissions_kg = emissions_kg
        self.usage_type = usage_type
        self.resource_id = resource_id
        self.intensity_source = intensity_source


class AnalysisSummary:
    """Precomputed analysis summary stored in database"""
    def __init__(
        self,
        total_emissions_kg: float,
        total_cost: float,
        total_energy_kwh: float,
        top_service: str,
        top_region: str,
        service_breakdown: List[Dict],
        region_breakdown: List[Dict],
        time_breakdown: List[Dict],
        record_count: int,
        generated_at: str
    ):
        self.total_emissions_kg = total_emissions_kg
        self.total_cost = total_cost
        self.total_energy_kwh = total_energy_kwh
        self.top_service = top_service
        self.top_region = top_region
        self.service_breakdown = service_breakdown
        self.region_breakdown = region_breakdown
        self.time_breakdown = time_breakdown
        self.record_count = record_count
        self.generated_at = generated_at


class OrganizationProfile:
    """Organization constraints for validation"""
    def __init__(
        self,
        organization_name: str,
        primary_user_region: str,
        workload_type: str,
        latency_sensitivity: str,
        migration_flexibility: str,
        optimization_priority: str
    ):
        self.organization_name = organization_name
        self.primary_user_region = primary_user_region
        self.workload_type = workload_type
        self.latency_sensitivity = latency_sensitivity
        self.migration_flexibility = migration_flexibility
        self.optimization_priority = optimization_priority
