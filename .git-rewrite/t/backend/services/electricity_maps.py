import os
import httpx
import logging
from datetime import datetime
from typing import Optional, Dict, Tuple
from functools import lru_cache

logger = logging.getLogger(__name__)

# AWS Region to Electricity Maps Zone Mapping
REGION_TO_ZONE_MAP = {
    # US Regions
    "us-east-1": "US-MIDA-PJM",      # Virginia
    "us-east-2": "US-MIDW-MISO",     # Ohio
    "us-west-1": "US-CAL-CISO",      # California
    "us-west-2": "US-NW-PACW",       # Oregon
    
    # EU Regions
    "eu-west-1": "IE",               # Ireland
    "eu-west-2": "GB",               # London
    "eu-west-3": "FR",               # Paris
    "eu-central-1": "DE",            # Frankfurt
    "eu-north-1": "SE",              # Stockholm
    "eu-south-1": "IT-NO",           # Milan
    
    # Asia Pacific
    "ap-south-1": "IN-WE",           # Mumbai
    "ap-northeast-1": "JP-TK",       # Tokyo
    "ap-northeast-2": "KR",          # Seoul
    "ap-northeast-3": "JP-KN",       # Osaka
    "ap-southeast-1": "SG",          # Singapore
    "ap-southeast-2": "AU-NSW",      # Sydney
    "ap-east-1": "HK",               # Hong Kong
    
    # South America
    "sa-east-1": "BR-CS",            # São Paulo
    
    # Canada
    "ca-central-1": "CA-ON",         # Montreal
    
    # Middle East
    "me-south-1": "AE",              # Bahrain
    
    # Africa
    "af-south-1": "ZA",              # Cape Town
}

# Fallback carbon intensity values (gCO2/kWh) if API fails
FALLBACK_CARBON_INTENSITY = {
    "US-MIDA-PJM": 420,
    "US-MIDW-MISO": 500,
    "US-CAL-CISO": 285,
    "US-NW-PACW": 200,
    "IE": 295,
    "GB": 230,
    "FR": 60,
    "DE": 350,
    "SE": 40,
    "IT-NO": 300,
    "IN-WE": 708,
    "JP-TK": 463,
    "KR": 450,
    "JP-KN": 463,
    "SG": 493,
    "AU-NSW": 700,
    "HK": 650,
    "BR-CS": 100,
    "CA-ON": 120,
    "AE": 500,
    "ZA": 850,
    "UNKNOWN": 450,  # Global average
}


class ElectricityMapsClient:
    """Client for Electricity Maps API with caching"""
    
    def __init__(self):
        self.api_key = os.getenv("ELECTRICITY_MAPS_API_KEY")
        self.base_url = "https://api.electricitymap.org/v3"
        self.cache: Dict[str, float] = {}
    
    def map_region_to_zone(self, aws_region: str) -> str:
        """Map AWS region to Electricity Maps zone"""
        zone = REGION_TO_ZONE_MAP.get(aws_region, "UNKNOWN")
        if zone == "UNKNOWN":
            logger.warning(f"Unknown AWS region: {aws_region}, using fallback")
        return zone
    
    async def get_historical_carbon_intensity(
        self, 
        zone: str, 
        timestamp: datetime
    ) -> Tuple[float, str]:
        """
        Get historical carbon intensity for a specific zone and time.
        
        Returns:
            Tuple[float, str]: (carbon_intensity in gCO2/kWh, source)
            source can be: "electricity_maps", "fallback", or "error"
        """
        # Create cache key (zone + hour)
        cache_key = f"{zone}_{timestamp.strftime('%Y-%m-%d_%H')}"
        
        # Check cache first
        if cache_key in self.cache:
            logger.debug(f"Cache hit for {cache_key}")
            return self.cache[cache_key], "electricity_maps_cached"
        
        # If no API key, use fallback
        if not self.api_key or self.api_key == "your_electricity_maps_api_key_here":
            logger.warning("No Electricity Maps API key configured, using fallback")
            intensity = FALLBACK_CARBON_INTENSITY.get(zone, FALLBACK_CARBON_INTENSITY["UNKNOWN"])
            self.cache[cache_key] = intensity
            return intensity, "fallback"
        
        # Call API
        try:
            async with httpx.AsyncClient() as client:
                # Format timestamp for API (ISO 8601)
                dt_str = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
                
                url = f"{self.base_url}/carbon-intensity/past"
                params = {
                    "zone": zone,
                    "datetime": dt_str
                }
                headers = {
                    "auth-token": self.api_key
                }
                
                logger.info(f"Calling Electricity Maps API: zone={zone}, datetime={dt_str}")
                
                response = await client.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    intensity = data.get("carbonIntensity")
                    
                    if intensity is not None:
                        logger.info(f"✓ API success: {intensity} gCO2/kWh for {zone} at {dt_str}")
                        self.cache[cache_key] = intensity
                        return intensity, "electricity_maps"
                    else:
                        logger.warning(f"API returned no carbonIntensity for {zone}")
                        intensity = FALLBACK_CARBON_INTENSITY.get(zone, FALLBACK_CARBON_INTENSITY["UNKNOWN"])
                        self.cache[cache_key] = intensity
                        return intensity, "fallback"
                
                elif response.status_code == 401:
                    logger.error("Electricity Maps API: Invalid API key")
                    intensity = FALLBACK_CARBON_INTENSITY.get(zone, FALLBACK_CARBON_INTENSITY["UNKNOWN"])
                    self.cache[cache_key] = intensity
                    return intensity, "fallback"
                
                elif response.status_code == 404:
                    logger.warning(f"Zone {zone} not found in Electricity Maps")
                    intensity = FALLBACK_CARBON_INTENSITY.get(zone, FALLBACK_CARBON_INTENSITY["UNKNOWN"])
                    self.cache[cache_key] = intensity
                    return intensity, "fallback"
                
                else:
                    logger.error(f"API error: {response.status_code} - {response.text}")
                    intensity = FALLBACK_CARBON_INTENSITY.get(zone, FALLBACK_CARBON_INTENSITY["UNKNOWN"])
                    self.cache[cache_key] = intensity
                    return intensity, "fallback"
        
        except Exception as e:
            logger.error(f"Exception calling Electricity Maps API: {e}")
            intensity = FALLBACK_CARBON_INTENSITY.get(zone, FALLBACK_CARBON_INTENSITY["UNKNOWN"])
            self.cache[cache_key] = intensity
            return intensity, "fallback"
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "cache_size": len(self.cache),
            "cached_zones": list(set(k.split("_")[0] for k in self.cache.keys()))
        }


# Global client instance
_client = None

def get_electricity_maps_client() -> ElectricityMapsClient:
    """Get or create the global Electricity Maps client"""
    global _client
    if _client is None:
        _client = ElectricityMapsClient()
    return _client
