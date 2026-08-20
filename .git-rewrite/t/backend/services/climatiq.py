import os
import httpx
import logging
from models.schemas import ApplianceUsage, EmissionResponse, ApplianceEmission, RegionalTestRequest, RegionalTestResponse

logger = logging.getLogger(__name__)

# Regional emission factors (kg CO2e per kWh)
REGIONAL_FACTORS = {
    "IN": {"name": "India", "factor": 0.716, "type": "Fossil-heavy"},
    "US": {"name": "USA", "factor": 0.42, "type": "Mixed"},
    "DE": {"name": "Germany", "factor": 0.35, "type": "Mixed (renewables growing)"},
    "GB": {"name": "UK", "factor": 0.23, "type": "Cleaner grid"},
    "FR": {"name": "France", "factor": 0.06, "type": "Nuclear-heavy"},
    "NO": {"name": "Norway", "factor": 0.025, "type": "Renewable-heavy"},
    "SE": {"name": "Sweden", "factor": 0.04, "type": "Renewable-heavy"},
    "CN": {"name": "China", "factor": 0.70, "type": "Coal-heavy"},
    "AU": {"name": "Australia", "factor": 0.70, "type": "Fossil-heavy"},
    "JP": {"name": "Japan", "factor": 0.45, "type": "Mixed"},
    "BR": {"name": "Brazil", "factor": 0.10, "type": "Hydro-heavy"},
    "CA": {"name": "Canada", "factor": 0.12, "type": "Clean grid"},
    "ZA": {"name": "South Africa", "factor": 0.85, "type": "Coal-heavy"},
    "EU": {"name": "EU (generic)", "factor": 0.25, "type": "Mixed"},
    "GLOBAL": {"name": "Global avg", "factor": 0.45, "type": "Mixed"},
}

# Default to India for backward compatibility
INDIA_GRID_FACTOR = REGIONAL_FACTORS["IN"]["factor"]

ESTIMATE_URL = "https://api.climatiq.io/data/v1/estimate"

# These activity IDs are confirmed to have India (IN) emission factors
# in Climatiq's database. Ordered by preference.
INDIA_ACTIVITY_IDS = [
    "electricity-supply_grid-source_supplier_mix",   # supplier mix - best for Scope 2
    "electricity-supply_grid-source_production_mix", # production mix - fallback
    "electricity-energy_source_grid_mix",            # generic grid mix
]

async def calculate_emissions(usage: ApplianceUsage, region_code: str = "IN") -> EmissionResponse:
    api_key = os.getenv("CLIMATIQ_API_KEY")

    appliances = {
        "AC": usage.AC,
        "Lighting": usage.Lighting,
        "Servers": usage.Servers,
        "Others": usage.Others
    }

    total_kwh = sum(appliances.values())
    breakdown = []
    source = "fallback"

    if api_key and api_key != "your_climatiq_api_key_here":
        try:
            async with httpx.AsyncClient() as client:
                for appliance, kwh in appliances.items():
                    co2_kg, item_source = await _fetch_regional_emission(client, api_key, kwh, region_code)
                    if item_source == "climatiq":
                        source = "climatiq"
                    breakdown.append({
                        "appliance": appliance,
                        "kwh": kwh,
                        "co2_kg": round(co2_kg, 4)
                    })
        except Exception as e:
            logger.error(f"Climatiq failed entirely: {e}. Using regional fallback.")
            breakdown = _fallback_calculation(appliances, region_code)
    else:
        logger.warning(f"No Climatiq API key. Using regional grid factor for {region_code}.")
        breakdown = _fallback_calculation(appliances, region_code)

    total_co2 = sum(item["co2_kg"] for item in breakdown)
    for item in breakdown:
        item["percentage"] = round((item["co2_kg"] / total_co2 * 100), 2) if total_co2 > 0 else 0

    breakdown_models = [ApplianceEmission(**item) for item in breakdown]
    top_contributor = max(breakdown, key=lambda x: x["co2_kg"])["appliance"] if breakdown else "None"

    return EmissionResponse(
        total_kwh=total_kwh,
        total_co2_kg=round(total_co2, 2),
        breakdown=breakdown_models,
        top_contributor=top_contributor,
        source=source
    )


async def _fetch_regional_emission(client: httpx.AsyncClient, api_key: str, kwh: float, region_code: str) -> tuple[float, str]:
    """Fetch emission from Climatiq API for any region, return (co2_kg, source)"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Try each activity ID in order
    for activity_id in INDIA_ACTIVITY_IDS:
        try:
            response = await client.post(
                ESTIMATE_URL,
                headers=headers,
                json={
                    "emission_factor": {
                        "activity_id": activity_id,
                        "region": region_code,
                        "data_version": "^6"
                    },
                    "parameters": {
                        "energy": kwh,
                        "energy_unit": "kWh"
                    }
                },
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                co2_kg = data.get("co2e")
                if co2_kg is not None:
                    logger.info(f"Climatiq {region_code} success [{activity_id}]: {co2_kg} kg for {kwh} kWh")
                    return co2_kg, "climatiq"
            else:
                logger.warning(f"activity_id {activity_id} for {region_code} returned {response.status_code}")
        except Exception as e:
            logger.warning(f"activity_id {activity_id} for {region_code} failed: {e}")
            continue

    # All activity IDs failed — use regional fallback factor
    logger.warning(f"All activity IDs failed for {region_code}. Falling back to regional factor.")
    regional_factor = REGIONAL_FACTORS.get(region_code, REGIONAL_FACTORS["GLOBAL"])["factor"]
    return kwh * regional_factor, "fallback"


async def _fetch_india_emission(client: httpx.AsyncClient, api_key: str, kwh: float) -> float:
    """Legacy function for backward compatibility"""
    co2_kg, _ = await _fetch_regional_emission(client, api_key, kwh, "IN")
    return co2_kg


def _fallback_calculation(appliances: dict, region_code: str = "IN") -> list:
    regional_factor = REGIONAL_FACTORS.get(region_code, REGIONAL_FACTORS["GLOBAL"])["factor"]
    return [
        {
            "appliance": appliance,
            "kwh": kwh,
            "co2_kg": round(kwh * regional_factor, 4)
        }
        for appliance, kwh in appliances.items()
    ]


async def test_regional_emission(request: RegionalTestRequest) -> RegionalTestResponse:
    """Test emission calculation for a specific region"""
    api_key = os.getenv("CLIMATIQ_API_KEY")
    region_code = request.region_code.upper()
    kwh = request.kwh
    
    # Get regional info
    regional_info = REGIONAL_FACTORS.get(region_code, REGIONAL_FACTORS["GLOBAL"])
    region_name = regional_info["name"]
    fallback_factor = regional_info["factor"]
    
    source = "fallback"
    co2_kg = kwh * fallback_factor
    message = f"Using fallback factor ({fallback_factor} kg CO₂/kWh)"
    
    # Try Climatiq API if available
    if api_key and api_key != "your_climatiq_api_key_here":
        try:
            async with httpx.AsyncClient() as client:
                co2_kg, source = await _fetch_regional_emission(client, api_key, kwh, region_code)
                if source == "climatiq":
                    message = f"✓ Climatiq API responded successfully"
                else:
                    message = f"Climatiq API failed, using fallback factor ({fallback_factor} kg CO₂/kWh)"
        except Exception as e:
            logger.error(f"Test failed for {region_code}: {e}")
            message = f"Error: {str(e)}, using fallback"
    else:
        message = "No Climatiq API key configured, using fallback factor"
    
    return RegionalTestResponse(
        region_code=region_code,
        region_name=region_name,
        kwh=kwh,
        co2_kg=round(co2_kg, 4),
        emission_factor=round(co2_kg / kwh if kwh > 0 else 0, 4),
        source=source,
        message=message
    )