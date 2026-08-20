from pydantic import BaseModel
from typing import Optional


# Appliance/Server Emissions Schemas
class ApplianceUsage(BaseModel):
    AC: float = 0
    Lighting: float = 0
    Servers: float = 0
    Others: float = 0


class ApplianceEmission(BaseModel):
    appliance: str
    kwh: float
    co2_kg: float
    percentage: float = 0


class EmissionResponse(BaseModel):
    total_kwh: float
    total_co2_kg: float
    breakdown: list[ApplianceEmission]
    top_contributor: str
    source: Optional[str] = "fallback"  # "climatiq" or "fallback"


class RegionalTestRequest(BaseModel):
    region_code: str
    kwh: float


class RegionalTestResponse(BaseModel):
    region_code: str
    region_name: str
    kwh: float
    co2_kg: float
    emission_factor: float
    source: str  # "climatiq" or "fallback"
    message: str


# AWS Billing Schemas
class AWSLineItem(BaseModel):
    service: str
    region: str
    usage_amount: float
    instance_type: Optional[str] = None
    cost: float
    co2_kg: float


class AWSAnalysisResponse(BaseModel):
    total_co2_kg: float
    total_cost: float
    total_usage: float
    top_region: str
    top_service: str
    top_instance: Optional[str]
    by_service: list[dict]
    by_region: list[dict]
    by_instance: list[dict]
    line_items: list[AWSLineItem]
    idle_resources: list[dict]


class AWSInsightRequest(BaseModel):
    total_co2_kg: float
    total_cost: float
    top_region: str
    top_service: str
    by_service: list[dict]
    by_region: list[dict]


class AWSInsightResponse(BaseModel):
    recommendations: list[dict]
    summary: str
    carbon_budget_status: dict


class WhatIfAWSRequest(BaseModel):
    scenario: str  # "move_region", "downsize_instance", "remove_idle"
    target_region: Optional[str] = None
    target_instance: Optional[str] = None
    service: Optional[str] = None


class WhatIfAWSResponse(BaseModel):
    scenario_name: str
    current_co2_kg: float
    projected_co2_kg: float
    savings_kg: float
    savings_cost: float
    description: str


# Time-Based Analysis Schemas (with Electricity Maps)
class TimeBasedLineItem(BaseModel):
    service: str
    region: str
    zone: str  # Electricity Maps zone
    usage_amount: float
    timestamp: str  # ISO format
    carbon_intensity: float  # gCO2/kWh
    energy_kwh: float
    co2_kg: float
    cost: float
    source: str  # "electricity_maps", "electricity_maps_cached", or "fallback"


class TimeBasedAnalysisResponse(BaseModel):
    total_co2_kg: float
    total_cost: float
    total_energy_kwh: float
    top_region: str
    top_service: str
    by_service: list[dict]
    by_region: list[dict]
    by_time: list[dict]  # Time-series data
    line_items: list[TimeBasedLineItem]
    processed_rows: int
    skipped_rows: int
    api_calls: int  # Number of API calls made
    cached_calls: int  # Number of cached results used
    fallback_calls: int  # Number of fallback values used
    cache_size: int  # Current cache size
