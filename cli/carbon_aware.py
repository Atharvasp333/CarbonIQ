"""
Carbon Intensity Client
Uses Electricity Maps API to get real-time carbon intensity data.
"""

import os
import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


# AWS Region to Electricity Maps Zone Mapping
REGION_TO_ZONE_MAP = {
    "us-east-1": "US-MIDA-PJM",      # Virginia
    "us-east-2": "US-MIDW-MISO",     # Ohio
    "us-west-1": "US-CAL-CISO",      # California
    "us-west-2": "US-NW-PACW",       # Oregon
    "eu-west-1": "IE",               # Ireland
    "eu-west-2": "GB",               # London
    "eu-west-3": "FR",               # Paris
    "eu-central-1": "DE",            # Frankfurt
    "ap-south-1": "IN-WE",           # Mumbai
    "ap-northeast-1": "JP-TK",       # Tokyo
    "ap-southeast-1": "SG",          # Singapore
    "ap-southeast-2": "AU-NSW",      # Sydney
}


class CarbonAwareClient:
    """Client for Electricity Maps integration."""
    
    def __init__(self):
        """Initialize Electricity Maps client."""
        self.api_key = os.getenv("ELECTRICITY_MAPS_API_KEY", "").strip()
        self.base_url = "https://api.electricitymap.org/v3"
        self.enabled = bool(self.api_key and self.api_key != "your_electricity_maps_api_key_here")
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                'auth-token': self.api_key
            })
    
    def is_available(self) -> bool:
        """
        Check if Electricity Maps API is available and configured.
        
        Returns:
            True if available, False otherwise
        """
        if not self.enabled:
            print("[ElectricityMaps] API key not configured")
            return False
        
        try:
            # Try a simple query to validate API key
            response = self.session.get(
                f"{self.base_url}/carbon-intensity/latest",
                params={"zone": "US-CAL-CISO"},
                timeout=5
            )
            
            if response.status_code == 200:
                print("[ElectricityMaps] ✓ API is available")
                return True
            elif response.status_code == 401:
                print("[ElectricityMaps] ✗ Invalid API key")
                return False
            else:
                print(f"[ElectricityMaps] API returned status {response.status_code}")
                return False
        
        except requests.exceptions.RequestException as e:
            print(f"[ElectricityMaps] Connection error: {e}")
            return False
    
    def get_current_intensity(self, aws_region: str = "us-east-1") -> Optional[Dict]:
        """
        Get current carbon intensity for an AWS region.
        
        Args:
            aws_region: AWS region code (e.g., us-east-1)
        
        Returns:
            Dictionary with current intensity data, or None if not available
        """
        if not self.enabled:
            return None
        
        # Map AWS region to Electricity Maps zone
        zone = REGION_TO_ZONE_MAP.get(aws_region, "US-MIDA-PJM")
        
        try:
            response = self.session.get(
                f"{self.base_url}/carbon-intensity/latest",
                params={"zone": zone},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "aws_region": aws_region,
                    "zone": zone,
                    "carbon_intensity": data.get("carbonIntensity"),
                    "datetime": data.get("datetime"),
                    "fossil_fuel_percentage": data.get("fossilFuelPercentage"),
                    "renewable_percentage": data.get("renewablePercentage")
                }
            else:
                print(f"[ElectricityMaps] Failed to get current intensity: {response.status_code}")
                return None
        
        except requests.exceptions.RequestException as e:
            print(f"[ElectricityMaps] Error getting current intensity: {e}")
            return None
    
    def get_optimal_windows(
        self,
        duration_minutes: int,
        regions: List[str] = None,
        deadline: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get optimal execution windows with lower carbon intensity across AWS regions.
        
        Args:
            duration_minutes: Expected workload duration
            regions: List of AWS region codes to consider
            deadline: ISO 8601 deadline timestamp
        
        Returns:
            Dictionary with optimal windows data, or None if not available
        """
        if not self.enabled:
            return None
        
        # Default regions if none provided
        if not regions:
            regions = ["us-east-1", "us-west-2", "eu-west-1"]
        
        try:
            results = []
            
            for aws_region in regions:
                zone = REGION_TO_ZONE_MAP.get(aws_region, "US-MIDA-PJM")
                
                # Get current intensity for this zone
                response = self.session.get(
                    f"{self.base_url}/carbon-intensity/latest",
                    params={"zone": zone},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    intensity = data.get("carbonIntensity")
                    
                    if intensity:
                        results.append({
                            "aws_region": aws_region,
                            "zone": zone,
                            "carbon_intensity": intensity,
                            "datetime": data.get("datetime"),
                            "fossil_fuel_percentage": data.get("fossilFuelPercentage"),
                            "renewable_percentage": data.get("renewablePercentage")
                        })
            
            if results:
                # Find the optimal region (lowest carbon intensity)
                optimal = min(results, key=lambda x: x.get('carbon_intensity', float('inf')))
                
                return {
                    "optimal_region": optimal.get('aws_region'),
                    "optimal_zone": optimal.get('zone'),
                    "optimal_intensity": optimal.get('carbon_intensity'),
                    "all_regions": results,
                    "queried_at": datetime.utcnow().isoformat(),
                    "duration_minutes": duration_minutes
                }
            
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"[ElectricityMaps] Error getting optimal windows: {e}")
            return None
