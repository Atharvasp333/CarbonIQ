import os
import httpx
import logging

logger = logging.getLogger(__name__)

ESTIMATE_URL = "https://api.climatiq.io/data/v1/estimate"
STATIC_EMISSION_FACTOR_IN = 0.7  # kg CO2e per kWh for India

async def estimate_emissions(energy_kwh: float, region: str = "IN") -> float:
    """
    Convert energy (kWh) to carbon emissions (kg CO2e) using Climatiq API.
    Fallback to static emission factor if API fails.
    """
    api_key = os.getenv("CLIMATIQ_API_KEY")
    
    if api_key and api_key != "your_climatiq_api_key_here":
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                response = await client.post(
                    ESTIMATE_URL,
                    headers=headers,
                    json={
                        "emission_factor": {
                            "activity_id": "electricity-energy_source_grid_mix",
                            "region": "IN", # Always IN as per requirements
                            "data_version": "^6"
                        },
                        "parameters": {
                            "energy": energy_kwh,
                            "energy_unit": "kWh"
                        }
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    co2e = data.get("co2e")
                    if co2e is not None:
                        return co2e
                else:
                    logger.warning(f"Climatiq API returned {response.status_code}: {response.text}")
                    
        except Exception as e:
            logger.error(f"Climatiq API call failed: {e}")
            
    # Fallback mechanism
    logger.info("Using fallback static emission factor for IN.")
    return energy_kwh * STATIC_EMISSION_FACTOR_IN
