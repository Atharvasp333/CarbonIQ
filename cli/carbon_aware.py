"""
Carbon Aware SDK Client
Handles communication with Carbon Aware SDK for carbon intensity data.
"""

import os
import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class CarbonAwareClient:
    """Client for Carbon Aware SDK integration."""
    
    def __init__(self):
        """Initialize Carbon Aware SDK client."""
        self.sdk_url = os.getenv("CARBON_AWARE_SDK_URL", "http://localhost:5073")
        self.enabled = os.getenv("CARBON_AWARE_SDK_ENABLED", "false").lower() == "true"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def is_available(self) -> bool:
        """
        Check if Carbon Aware SDK is available and configured.
        
        Returns:
            True if available, False otherwise
        """
        if not self.enabled:
            print("[CarbonAware] SDK is disabled in configuration")
            return False
        
        try:
            # Try a simple health check or current emissions endpoint
            response = self.session.get(
                f"{self.sdk_url}/emissions/forecasts/current",
                timeout=5,
                params={"location": "eastus"}  # Example location
            )
            
            return response.status_code == 200
        
        except requests.exceptions.RequestException:
            return False
    
    def get_current_intensity(self, location: str = "eastus") -> Optional[Dict]:
        """
        Get current carbon intensity for a location.
        
        Args:
            location: Location identifier (e.g., Azure region name)
        
        Returns:
            Dictionary with current intensity data, or None if not available
        """
        if not self.enabled:
            return None
        
        try:
            response = self.session.get(
                f"{self.sdk_url}/emissions/forecasts/current",
                params={"location": location},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_intensity_response(data)
            else:
                print(f"[CarbonAware] Failed to get current intensity: {response.status_code}")
                return None
        
        except requests.exceptions.RequestException as e:
            print(f"[CarbonAware] Error getting current intensity: {e}")
            return None
    
    def get_optimal_windows(
        self,
        duration_minutes: int,
        locations: List[str] = None,
        deadline: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get optimal execution windows with lower carbon intensity.
        
        Args:
            duration_minutes: Expected workload duration
            locations: List of location identifiers to consider
            deadline: ISO 8601 deadline timestamp
        
        Returns:
            Dictionary with optimal windows data, or None if not available
        """
        if not self.enabled:
            return None
        
        # Default locations if none provided
        if not locations:
            locations = ["eastus", "westus", "westeurope"]
        
        # Calculate time window
        start_time = datetime.utcnow()
        if deadline:
            try:
                end_time = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            except:
                # Default to 24 hours if deadline parsing fails
                end_time = start_time + timedelta(hours=24)
        else:
            end_time = start_time + timedelta(hours=24)
        
        try:
            results = []
            
            for location in locations:
                response = self.session.get(
                    f"{self.sdk_url}/emissions/forecasts/batch",
                    params={
                        "location": location,
                        "dataStartAt": start_time.isoformat(),
                        "dataEndAt": end_time.isoformat(),
                        "windowSize": duration_minutes
                    },
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    parsed = self._parse_batch_response(data, location)
                    if parsed:
                        results.append(parsed)
            
            if results:
                # Find the optimal window (lowest average intensity)
                optimal = min(results, key=lambda x: x.get('average_intensity', float('inf')))
                
                return {
                    "optimal_location": optimal.get('location'),
                    "optimal_window": optimal.get('window'),
                    "average_intensity": optimal.get('average_intensity'),
                    "all_locations": results,
                    "queried_at": datetime.utcnow().isoformat()
                }
            
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"[CarbonAware] Error getting optimal windows: {e}")
            return None
    
    def _parse_intensity_response(self, data: any) -> Dict:
        """Parse Carbon Aware SDK intensity response."""
        # The exact structure depends on the SDK version and data source
        # This is a basic parser that should be adapted to actual responses
        
        if isinstance(data, list) and len(data) > 0:
            first = data[0]
            return {
                "location": first.get("location", "unknown"),
                "rating": first.get("rating", 0),
                "time": first.get("time", ""),
                "duration": first.get("duration", 0)
            }
        elif isinstance(data, dict):
            return {
                "location": data.get("location", "unknown"),
                "rating": data.get("rating", 0),
                "time": data.get("time", ""),
                "duration": data.get("duration", 0)
            }
        
        return {}
    
    def _parse_batch_response(self, data: any, location: str) -> Optional[Dict]:
        """Parse Carbon Aware SDK batch forecast response."""
        if isinstance(data, list) and len(data) > 0:
            # Calculate average intensity across the window
            intensities = [item.get("rating", 0) for item in data if "rating" in item]
            
            if intensities:
                return {
                    "location": location,
                    "window": {
                        "start": data[0].get("time", ""),
                        "end": data[-1].get("time", "")
                    },
                    "average_intensity": sum(intensities) / len(intensities),
                    "min_intensity": min(intensities),
                    "max_intensity": max(intensities),
                    "data_points": len(data)
                }
        
        return None
