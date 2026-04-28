import os
import httpx
import logging
from models.schemas import ApplianceUsage, EmissionResponse, ApplianceEmission

logger = logging.getLogger(__name__)

# Source: Central Electricity Authority (CEA), India 2023
# This is the official India grid emission factor used for compliance
INDIA_GRID_FACTOR = 0.716  # kg CO2e per kWh (CEA 2023 published value)

ESTIMATE_URL = "https://api.climatiq.io/data/v1/estimate"

# These activity IDs are confirmed to have India (IN) emission factors
# in Climatiq's database. Ordered by preference.
INDIA_ACTIVITY_IDS = [
    "electricity-supply_grid-source_supplier_mix",   # supplier mix - best for Scope 2
    "electricity-supply_grid-source_production_mix", # production mix - fallback
    "electricity-energy_source_grid_mix",            # generic grid mix
]

async def calculate_emissions(usage: ApplianceUsage) -> EmissionResponse:
    api_key = os.getenv("CLIMATIQ_API_KEY")

    appliances = {
        "AC": usage.AC,
        "Lighting": usage.Lighting,
        "Servers": usage.Servers,
        "Others": usage.Others
    }

    total_kwh = sum(appliances.values())
    breakdown = []

    if api_key and api_key != "your_climatiq_api_key_here":
        try:
            async with httpx.AsyncClient() as client:
                for appliance, kwh in appliances.items():
                    co2_kg = await _fetch_india_emission(client, api_key, kwh)
                    breakdown.append({
                        "appliance": appliance,
                        "kwh": kwh,
                        "co2_kg": round(co2_kg, 4)
                    })
        except Exception as e:
            logger.error(f"Climatiq failed entirely: {e}. Using CEA fallback.")
            breakdown = _fallback_calculation(appliances)
    else:
        logger.warning("No Climatiq API key. Using CEA India grid factor.")
        breakdown = _fallback_calculation(appliances)

    total_co2 = sum(item["co2_kg"] for item in breakdown)
    for item in breakdown:
        item["percentage"] = round((item["co2_kg"] / total_co2 * 100), 2) if total_co2 > 0 else 0

    breakdown_models = [ApplianceEmission(**item) for item in breakdown]
    top_contributor = max(breakdown, key=lambda x: x["co2_kg"])["appliance"]

    return EmissionResponse(
        total_kwh=total_kwh,
        total_co2_kg=round(total_co2, 2),
        breakdown=breakdown_models,
        top_contributor=top_contributor
    )


async def _fetch_india_emission(client: httpx.AsyncClient, api_key: str, kwh: float) -> float:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Try each India-specific activity ID in order
    for activity_id in INDIA_ACTIVITY_IDS:
        try:
            response = await client.post(
                ESTIMATE_URL,
                headers=headers,
                json={
                    "emission_factor": {
                        "activity_id": activity_id,
                        "region": "IN",          # India country code
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
                    logger.info(f"Climatiq India success [{activity_id}]: {co2_kg} kg for {kwh} kWh")
                    return co2_kg
            else:
                logger.warning(f"activity_id {activity_id} returned {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"activity_id {activity_id} failed: {e}")
            continue

    # All India-specific IDs failed — use global factor but scale to India
    logger.warning("All India activity IDs failed. Falling back to CEA factor.")
    return kwh * INDIA_GRID_FACTOR


def _fallback_calculation(appliances: dict) -> list:
    return [
        {
            "appliance": appliance,
            "kwh": kwh,
            "co2_kg": round(kwh * INDIA_GRID_FACTOR, 4)
        }
        for appliance, kwh in appliances.items()
    ]