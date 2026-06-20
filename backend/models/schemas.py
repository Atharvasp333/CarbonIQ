from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


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


# Organization Profile Schemas
class OrganizationProfileCreate(BaseModel):
    organization_name: str
    primary_user_region: str  # India, North America, Europe, Asia Pacific, Global
    workload_type: str  # Production, Development, Testing, Analytics, Machine Learning, Mixed
    latency_sensitivity: str  # High, Medium, Low
    migration_flexibility: str  # Yes, Some Workloads, No
    optimization_priority: str  # Reduce Carbon, Reduce Cost, Balance Both


class OrganizationProfileUpdate(BaseModel):
    organization_name: Optional[str] = None
    primary_user_region: Optional[str] = None
    workload_type: Optional[str] = None
    latency_sensitivity: Optional[str] = None
    migration_flexibility: Optional[str] = None
    optimization_priority: Optional[str] = None


class OrganizationProfileResponse(BaseModel):
    id: int
    organization_name: str
    primary_user_region: str
    workload_type: str
    latency_sensitivity: str
    migration_flexibility: str
    optimization_priority: str
    created_at: datetime
    updated_at: datetime


# Sustainability Intelligence Schemas
class CarbonHotspot(BaseModel):
    service: str
    region: str
    zone: str
    timestamp: str
    emissions_kg: float
    cost: float
    carbon_intensity: float


class RegionOpportunity(BaseModel):
    current_region: str
    suggested_region: str
    current_intensity: float
    suggested_intensity: float
    potential_reduction_pct: float
    potential_savings_kg: float
    confidence: str  # High, Medium, Low
    reasoning: str


class TimeOpportunity(BaseModel):
    service: str
    region: str
    current_time_window: str
    suggested_time_window: str
    current_avg_intensity: float
    suggested_avg_intensity: float
    potential_reduction_pct: float
    potential_savings_kg: float
    confidence: str
    reasoning: str


class ServiceRecommendation(BaseModel):
    title: str
    category: str  # EC2, Lambda, S3, RDS, SageMaker, Region, Time
    service: str
    carbon_reduction_pct: float
    cost_impact: str  # Negative, Neutral, Positive
    confidence: str  # High, Medium, Low
    reasoning: str
    details: dict


class SustainabilityInsights(BaseModel):
    service_analysis: dict
    region_analysis: dict
    time_analysis: dict
    hotspots: List[CarbonHotspot]
    region_opportunities: List[RegionOpportunity]
    time_opportunities: List[TimeOpportunity]
    recommendations: List[ServiceRecommendation]



# ============================================================
# User Ownership & Intelligence Schemas (Migration 001)
# ============================================================

class AnalysisSummaryCreate(BaseModel):
    """Request to create/update precomputed analysis summary."""
    service_breakdown: dict
    region_breakdown: dict
    daily_breakdown: Optional[dict] = None
    time_breakdown: Optional[dict] = None
    top_hotspots: Optional[list] = None
    metadata: Optional[dict] = None


class AnalysisSummaryResponse(BaseModel):
    """Response containing cached analysis summary."""
    id: int
    user_id: int
    analysis_id: int
    service_breakdown: dict
    region_breakdown: dict
    daily_breakdown: Optional[dict]
    time_breakdown: Optional[dict]
    top_hotspots: Optional[list]
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime


class RecommendationRunCreate(BaseModel):
    """Request to create AI recommendation run."""
    run_type: str  # 'sustainability', 'cost', 'performance', 'explainable'
    findings: dict
    recommendations: list
    hotspots: Optional[list] = None
    region_opportunities: Optional[list] = None
    time_opportunities: Optional[list] = None
    confidence_score: Optional[float] = None
    metadata: Optional[dict] = None


class RecommendationRunResponse(BaseModel):
    """Response containing cached AI recommendations."""
    id: int
    user_id: int
    analysis_id: int
    run_type: str
    generated_at: datetime
    findings: dict
    recommendations: list
    hotspots: Optional[list]
    region_opportunities: Optional[list]
    time_opportunities: Optional[list]
    confidence_score: Optional[float]
    metadata: Optional[dict]
    status: str


class UserInsightCreate(BaseModel):
    """Request to create/update user insight."""
    insight_type: str  # 'monthly_trend', 'cost_alert', 'carbon_goal', 'service_pattern'
    time_period: Optional[str] = None  # 'daily', 'weekly', 'monthly', 'yearly'
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    total_emissions_kg: Optional[float] = None
    total_cost: Optional[float] = None
    total_energy_kwh: Optional[float] = None
    analysis_count: Optional[int] = None
    top_services: Optional[dict] = None
    top_regions: Optional[dict] = None
    trends: Optional[dict] = None
    alerts: Optional[dict] = None


class UserInsightResponse(BaseModel):
    """Response containing user insight data."""
    id: int
    user_id: int
    insight_type: str
    time_period: Optional[str]
    period_start: Optional[datetime]
    period_end: Optional[datetime]
    total_emissions_kg: Optional[float]
    total_cost: Optional[float]
    total_energy_kwh: Optional[float]
    analysis_count: Optional[int]
    top_services: Optional[dict]
    top_regions: Optional[dict]
    trends: Optional[dict]
    alerts: Optional[dict]
    created_at: datetime
    updated_at: datetime


class AuditLogEntry(BaseModel):
    """Audit log entry for compliance tracking."""
    id: int
    user_id: Optional[int]
    action: str  # 'create', 'read', 'update', 'delete'
    entity_type: str
    entity_id: Optional[int]
    ip_address: Optional[str]
    user_agent: Optional[str]
    details: Optional[dict]
    created_at: datetime


class AnalysisHistoryResponse(BaseModel):
    """Response for user's analysis history."""
    id: int
    user_id: int
    filename: Optional[str]
    uploaded_at: datetime
    total_emissions: Optional[float]
    total_cost: Optional[float]
    total_energy: Optional[float]
    top_service: Optional[str]
    top_region: Optional[str]
    original_rows: Optional[int]
    compressed_rows: Optional[int]
    api_calls: Optional[int]


class UserDataStats(BaseModel):
    """Statistics about user's data ownership."""
    user_id: int
    email: str
    analyses_count: int
    emission_records_count: int
    api_logs_count: int
    org_profiles_count: int
    total_emissions_kg: Optional[float]
    total_cost: Optional[float]
    earliest_analysis: Optional[datetime]
    latest_analysis: Optional[datetime]
