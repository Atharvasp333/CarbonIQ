"""
Deployment Analysis Route
Accepts combined CodeCarbon + Carbon Aware SDK data from the CLI
and uses Gemini to generate an intelligent deployment recommendation
(optimal time window + optimal zone).
"""

import os
import json
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cli", tags=["cli", "deployment"])


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class CodeCarbonSummary(BaseModel):
    """Subset of CodeCarbon measurement data relevant for deployment planning."""
    workload_name: str
    workload_type: Optional[str] = "general"
    duration_seconds: float
    emissions_gco2e: float
    energy_kwh: float
    carbon_intensity: Optional[float] = None   # gCO2e/kWh at measurement time
    country_name: Optional[str] = None
    cpu_energy: Optional[float] = None
    ram_energy: Optional[float] = None
    gpu_energy: Optional[float] = None


class RegionData(BaseModel):
    """Carbon intensity data for a single region from Carbon Aware SDK."""
    aws_region: str
    sdk_location: Optional[str] = None
    carbon_intensity: float          # gCO2eq/kWh
    time: Optional[str] = None
    source: Optional[str] = None


class ForecastData(BaseModel):
    """Forecast optimal window from Carbon Aware SDK."""
    aws_region: Optional[str] = None
    optimal_window_start: Optional[str] = None
    optimal_carbon_intensity: Optional[float] = None
    window_duration_minutes: Optional[int] = None
    forecast_generated_at: Optional[str] = None
    source: Optional[str] = None


class CarbonAwareSDKSummary(BaseModel):
    """Data returned by the Carbon Aware SDK client."""
    available: bool
    queried_at: Optional[str] = None
    regions: Optional[List[RegionData]] = None
    best_region: Optional[RegionData] = None
    worst_region: Optional[RegionData] = None
    average_intensity: Optional[float] = None
    total_regions_compared: Optional[int] = None
    forecast: Optional[ForecastData] = None
    error: Optional[str] = None
    source: Optional[str] = None


class DeploymentAnalysisRequest(BaseModel):
    """
    Full payload sent from the CLI's `carboniq deploy-analysis` command.
    Combines:
      - CodeCarbon measurements (actual observed footprint)
      - Carbon Aware SDK data (current/forecast grid carbon intensity across regions)
    """
    codecarbon: CodeCarbonSummary
    carbon_aware_sdk: CarbonAwareSDKSummary
    deadline: Optional[str] = Field(None, description="ISO 8601 deadline for deployment")
    preferred_regions: Optional[List[str]] = Field(
        None,
        description="User-preferred AWS regions (cost/latency constraints)"
    )
    constraints: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional constraints: budget, compliance, latency_ms, etc."
    )
    measured_at: Optional[str] = None


class DeploymentRecommendation(BaseModel):
    optimal_region: str
    optimal_time_window: Optional[str] = None
    estimated_carbon_intensity: Optional[float] = None
    estimated_emissions_gco2e: Optional[float] = None
    carbon_savings_vs_current_pct: Optional[float] = None
    priority: str = "high"
    rationale: str


class DeploymentAnalysisResponse(BaseModel):
    summary: str
    primary_recommendation: DeploymentRecommendation
    alternative_recommendations: List[DeploymentRecommendation] = []
    key_insights: List[str] = []
    carbon_reduction_potential_pct: Optional[float] = None
    analysis_timestamp: str
    data_sources: List[str]


# ---------------------------------------------------------------------------
# Helper: build Gemini prompt
# ---------------------------------------------------------------------------

def _build_analysis_prompt(request: DeploymentAnalysisRequest) -> str:
    cc = request.codecarbon
    sdk = request.carbon_aware_sdk

    regions_text = "No region data available."
    if sdk.available and sdk.regions:
        sorted_regions = sorted(sdk.regions, key=lambda r: r.carbon_intensity)
        lines = []
        for i, r in enumerate(sorted_regions, 1):
            rank_label = " 🏆 BEST" if i == 1 else (" ⚠️ WORST" if i == len(sorted_regions) else "")
            lines.append(
                f"  {i}. {r.aws_region} ({r.sdk_location or 'N/A'}): "
                f"{r.carbon_intensity:.1f} gCO2eq/kWh{rank_label}"
            )
        regions_text = "\n".join(lines)

    best_region_text = "Unknown"
    if sdk.available and sdk.best_region:
        b = sdk.best_region
        best_region_text = (
            f"{b.aws_region} ({b.sdk_location}) — "
            f"{b.carbon_intensity:.1f} gCO2eq/kWh"
        )

    forecast_text = "No forecast available."
    if sdk.available and sdk.forecast and sdk.forecast.optimal_window_start:
        f = sdk.forecast
        forecast_text = (
            f"Best window in {f.aws_region}: starts {f.optimal_window_start}, "
            f"intensity {f.optimal_carbon_intensity:.1f} gCO2eq/kWh "
            f"(for {f.window_duration_minutes} min workload)"
        )

    deadline_text = f"Deadline: {request.deadline}" if request.deadline else "No hard deadline (flexible scheduling possible)"
    preferred_text = (
        f"Preferred regions: {', '.join(request.preferred_regions)}"
        if request.preferred_regions
        else "No region preference specified"
    )
    constraints_text = (
        json.dumps(request.constraints, indent=2)
        if request.constraints
        else "None specified"
    )

    # Intensity at measurement time vs best available region
    intensity_comparison = ""
    if cc.carbon_intensity and sdk.available and sdk.best_region:
        savings = (
            (cc.carbon_intensity - sdk.best_region.carbon_intensity)
            / cc.carbon_intensity * 100
        )
        intensity_comparison = (
            f"\n  Current intensity where measured: {cc.carbon_intensity:.1f} gCO2eq/kWh"
            f"\n  Best available region intensity:   {sdk.best_region.carbon_intensity:.1f} gCO2eq/kWh"
            f"\n  Potential intensity reduction:     {savings:.1f}%"
        )

    prompt = f"""You are an expert in sustainable cloud computing and carbon-aware deployment.
Your task: analyze the combined data below and produce a JSON deployment recommendation
that tells the user EXACTLY when and WHERE to deploy their workload to minimize
carbon emissions while respecting any constraints.

═══════════════════════════════════════════════════════
📊 CODECARBON MEASUREMENT (Observed Energy & Emissions)
═══════════════════════════════════════════════════════
Workload:       {cc.workload_name} ({cc.workload_type})
Duration:       {cc.duration_seconds:.2f} seconds
Energy:         {cc.energy_kwh:.6f} kWh
Emissions:      {cc.emissions_gco2e:.4f} gCO2e
Carbon intensity where measured: {cc.carbon_intensity or 'N/A'} gCO2eq/kWh
Country:        {cc.country_name or 'N/A'}
CPU Energy:     {cc.cpu_energy or 'N/A'} kWh
RAM Energy:     {cc.ram_energy or 'N/A'} kWh{intensity_comparison}

═══════════════════════════════════════════════════════
🌍 CARBON AWARE SDK DATA (Grid Intensity Across Regions)
═══════════════════════════════════════════════════════
SDK Available: {sdk.available}
Queried At:    {sdk.queried_at or 'N/A'}
Average intensity across regions: {sdk.average_intensity or 'N/A'} gCO2eq/kWh

Regions ranked by carbon intensity (low = green):
{regions_text}

Best region right now: {best_region_text}

Time-based forecast:
{forecast_text}

═══════════════════════════════════════════════════════
⚙️  DEPLOYMENT CONSTRAINTS
═══════════════════════════════════════════════════════
{deadline_text}
{preferred_text}
Other constraints:
{constraints_text}

═══════════════════════════════════════════════════════
INSTRUCTIONS
═══════════════════════════════════════════════════════
Based on ALL the data above, provide a comprehensive deployment recommendation.
Consider:
1. Where to deploy: pick the optimal AWS region from the carbon intensity data
2. When to deploy: if forecasts are available, suggest the best time window;
   if not, explain what time of day is typically greener for the best region
3. Quantify the carbon savings vs. the current measurement
4. Provide 1–2 alternative recommendations with trade-offs
5. List 3–5 key insights about the data

Respond with ONLY valid JSON in this exact schema:
{{
  "summary": "<2-3 sentence executive summary of the recommendation>",
  "primary_recommendation": {{
    "optimal_region": "<aws-region-code>",
    "optimal_time_window": "<ISO 8601 datetime or human-readable window, e.g. '2026-11-21T02:00:00Z' or 'Tonight 2–4 AM UTC'>",
    "estimated_carbon_intensity": <float gCO2eq/kWh>,
    "estimated_emissions_gco2e": <float, estimated emissions if deployed in optimal region>,
    "carbon_savings_vs_current_pct": <float, % savings vs. current measurement region>,
    "priority": "high",
    "rationale": "<detailed explanation of why this region/time was chosen>"
  }},
  "alternative_recommendations": [
    {{
      "optimal_region": "<aws-region>",
      "optimal_time_window": "<time or null>",
      "estimated_carbon_intensity": <float>,
      "estimated_emissions_gco2e": <float>,
      "carbon_savings_vs_current_pct": <float>,
      "priority": "medium",
      "rationale": "<trade-off explanation>"
    }}
  ],
  "key_insights": [
    "<insight 1>",
    "<insight 2>",
    "<insight 3>"
  ],
  "carbon_reduction_potential_pct": <float, max achievable reduction %>
}}
"""
    return prompt


# ---------------------------------------------------------------------------
# Fallback when Gemini is not available
# ---------------------------------------------------------------------------

def _fallback_analysis(request: DeploymentAnalysisRequest) -> DeploymentAnalysisResponse:
    """Rule-based fallback when Gemini API is unavailable."""
    cc = request.codecarbon
    sdk = request.carbon_aware_sdk

    if sdk.available and sdk.best_region:
        best = sdk.best_region
        optimal_region = best.aws_region
        optimal_intensity = best.carbon_intensity
        savings_pct = None
        if cc.carbon_intensity and cc.carbon_intensity > 0:
            savings_pct = round(
                (cc.carbon_intensity - optimal_intensity) / cc.carbon_intensity * 100, 1
            )
        estimated_emissions = (
            cc.energy_kwh * optimal_intensity if optimal_intensity else cc.emissions_gco2e
        )
        rationale = (
            f"{optimal_region} currently has the lowest carbon intensity "
            f"({optimal_intensity:.1f} gCO2eq/kWh) among all queried regions. "
            f"Deploying there instead of the measurement location could save "
            f"~{savings_pct or 'N/A'}% in carbon emissions."
        )
        time_window = "Deploy now — intensity data is real-time"
        if sdk.forecast and sdk.forecast.optimal_window_start:
            time_window = sdk.forecast.optimal_window_start
    else:
        optimal_region = request.preferred_regions[0] if request.preferred_regions else "eu-west-1"
        optimal_intensity = None
        savings_pct = None
        estimated_emissions = cc.emissions_gco2e
        rationale = (
            "Carbon Aware SDK data not available. eu-west-1 (Ireland) is statistically "
            "one of the lowest-carbon AWS regions in Europe. Consider running the SDK "
            "locally to get real-time data: "
            "docker run -p 5073:80 ghcr.io/green-software-foundation/carbon-aware-sdk:latest"
        )
        time_window = "Off-peak hours (2–6 AM local time) generally have lower grid intensity"

    primary = DeploymentRecommendation(
        optimal_region=optimal_region,
        optimal_time_window=time_window,
        estimated_carbon_intensity=optimal_intensity,
        estimated_emissions_gco2e=round(estimated_emissions, 4),
        carbon_savings_vs_current_pct=savings_pct,
        priority="high",
        rationale=rationale,
    )

    alternatives = []
    if sdk.available and sdk.regions and len(sdk.regions) > 1:
        second = sorted(sdk.regions, key=lambda r: r.carbon_intensity)[1]
        alt_savings = None
        if cc.carbon_intensity and cc.carbon_intensity > 0:
            alt_savings = round(
                (cc.carbon_intensity - second.carbon_intensity) / cc.carbon_intensity * 100, 1
            )
        alternatives.append(DeploymentRecommendation(
            optimal_region=second.aws_region,
            optimal_time_window=None,
            estimated_carbon_intensity=second.carbon_intensity,
            estimated_emissions_gco2e=round(cc.energy_kwh * second.carbon_intensity, 4),
            carbon_savings_vs_current_pct=alt_savings,
            priority="medium",
            rationale=(
                f"{second.aws_region} is the second-best region with "
                f"{second.carbon_intensity:.1f} gCO2eq/kWh. Good fallback option "
                "if the primary region has latency or compliance constraints."
            ),
        ))

    insights = [
        f"Workload '{cc.workload_name}' consumed {cc.energy_kwh:.6f} kWh over {cc.duration_seconds:.1f}s.",
        f"Total measured emissions: {cc.emissions_gco2e:.4f} gCO2e.",
    ]
    if sdk.available and sdk.total_regions_compared:
        insights.append(
            f"Carbon intensity compared across {sdk.total_regions_compared} AWS regions. "
            f"Range: {sdk.regions[-1].carbon_intensity:.1f}–{sdk.regions[0].carbon_intensity:.1f} gCO2eq/kWh."
            if sdk.regions else f"Compared {sdk.total_regions_compared} regions."
        )
    if savings_pct and savings_pct > 0:
        insights.append(
            f"Moving deployment to {optimal_region} could cut emissions by ~{savings_pct}%."
        )
    insights.append(
        "Consider scheduling workloads during renewable energy peaks "
        "(often midday solar or overnight low-demand periods)."
    )

    return DeploymentAnalysisResponse(
        summary=(
            f"Based on CodeCarbon measurements and real-time grid data, "
            f"deploy '{cc.workload_name}' to {optimal_region} for the lowest carbon footprint. "
            f"{'Potential savings: ' + str(savings_pct) + '% vs. current location.' if savings_pct else ''}"
        ),
        primary_recommendation=primary,
        alternative_recommendations=alternatives,
        key_insights=insights,
        carbon_reduction_potential_pct=savings_pct,
        analysis_timestamp=datetime.utcnow().isoformat(),
        data_sources=["codecarbon", "carbon_aware_sdk" if sdk.available else "fallback_heuristics"],
    )


# ---------------------------------------------------------------------------
# Main route
# ---------------------------------------------------------------------------

@router.post("/deployment-analysis", response_model=DeploymentAnalysisResponse)
async def analyze_deployment(request: DeploymentAnalysisRequest):
    """
    🌱 Deployment Analysis Agent

    Accepts combined CodeCarbon + Carbon Aware SDK data from the CLI and
    uses Gemini (Google AI) to recommend the optimal deployment:
      • Which AWS region (zone) to deploy to
      • What time window minimizes carbon emissions
      • Quantified carbon savings vs. the current location
      • Alternative options with trade-offs

    Falls back to rule-based analysis if Gemini is unavailable.
    """
    logger.info(
        f"Deployment analysis request: workload={request.codecarbon.workload_name}, "
        f"sdk_available={request.carbon_aware_sdk.available}"
    )

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    use_gemini = bool(gemini_key and gemini_key not in ("", "your_gemini_api_key_here"))

    if use_gemini:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-2.5-flash")

            prompt = _build_analysis_prompt(request)
            logger.info("Calling Gemini for deployment analysis...")
            response = model.generate_content(prompt)

            text = response.text.strip()
            # Strip markdown code fences if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            data = json.loads(text)

            # Build response from Gemini output
            primary_data = data.get("primary_recommendation", {})
            primary = DeploymentRecommendation(
                optimal_region=primary_data.get("optimal_region", "unknown"),
                optimal_time_window=primary_data.get("optimal_time_window"),
                estimated_carbon_intensity=primary_data.get("estimated_carbon_intensity"),
                estimated_emissions_gco2e=primary_data.get("estimated_emissions_gco2e"),
                carbon_savings_vs_current_pct=primary_data.get("carbon_savings_vs_current_pct"),
                priority=primary_data.get("priority", "high"),
                rationale=primary_data.get("rationale", ""),
            )

            alternatives = []
            for alt_data in data.get("alternative_recommendations", []):
                alternatives.append(DeploymentRecommendation(
                    optimal_region=alt_data.get("optimal_region", "unknown"),
                    optimal_time_window=alt_data.get("optimal_time_window"),
                    estimated_carbon_intensity=alt_data.get("estimated_carbon_intensity"),
                    estimated_emissions_gco2e=alt_data.get("estimated_emissions_gco2e"),
                    carbon_savings_vs_current_pct=alt_data.get("carbon_savings_vs_current_pct"),
                    priority=alt_data.get("priority", "medium"),
                    rationale=alt_data.get("rationale", ""),
                ))

            sdk_sources = ["carbon_aware_sdk"] if request.carbon_aware_sdk.available else ["carbon_aware_sdk_unavailable"]

            return DeploymentAnalysisResponse(
                summary=data.get("summary", ""),
                primary_recommendation=primary,
                alternative_recommendations=alternatives,
                key_insights=data.get("key_insights", []),
                carbon_reduction_potential_pct=data.get("carbon_reduction_potential_pct"),
                analysis_timestamp=datetime.utcnow().isoformat(),
                data_sources=["codecarbon", "gemini_agent"] + sdk_sources,
            )

        except json.JSONDecodeError as e:
            logger.warning(f"Gemini returned non-JSON response: {e}. Falling back.")
        except Exception as e:
            logger.warning(f"Gemini error: {e}. Falling back to rule-based analysis.")

    # Fallback: rule-based analysis
    logger.info("Using rule-based fallback analysis.")
    return _fallback_analysis(request)
