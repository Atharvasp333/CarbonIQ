"""
Carbon Aware SDK Client
Integrates with the Green Software Foundation's Carbon Aware SDK Web API.
Docs: https://github.com/Green-Software-Foundation/carbon-aware-sdk

The SDK exposes a REST API (default port 5073) that can be run locally via Docker
or .NET. It supports data from WattTime and ElectricityMaps.

This client gracefully degrades when the SDK is not running — it falls back to
Electricity Maps (via the existing CarbonAwareClient) if available.
"""

import os
import requests
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Location mappings: AWS region → Carbon Aware SDK location name
# The SDK uses WattTime / ElectricityMaps zone names.
# ---------------------------------------------------------------------------
AWS_REGION_TO_SDK_LOCATION: Dict[str, str] = {
    "us-east-1":      "eastus",        # Virginia → Azure East US proxy (WattTime PJM)
    "us-east-2":      "eastus2",       # Ohio
    "us-west-1":      "westus",        # N. California
    "us-west-2":      "westus2",       # Oregon
    "eu-west-1":      "northeurope",   # Ireland
    "eu-west-2":      "uksouth",       # London
    "eu-west-3":      "francecentral", # Paris
    "eu-central-1":   "germanywestcentral",  # Frankfurt
    "ap-south-1":     "centralindia",  # Mumbai
    "ap-northeast-1": "japaneast",     # Tokyo
    "ap-southeast-1": "southeastasia", # Singapore
    "ap-southeast-2": "australiaeast", # Sydney
    "ca-central-1":   "canadacentral", # Canada
    "sa-east-1":      "brazilsouth",   # São Paulo
}

# Reverse mapping for display
SDK_LOCATION_TO_AWS_REGION: Dict[str, str] = {
    v: k for k, v in AWS_REGION_TO_SDK_LOCATION.items()
}

# Default list of regions to compare (covering major deployment zones)
DEFAULT_COMPARISON_REGIONS = [
    "us-east-1",
    "us-west-2",
    "eu-west-1",
    "eu-central-1",
    "ap-southeast-1",
    "ap-southeast-2",
]


class CarbonAwareSDKClient:
    """
    HTTP client for the Carbon Aware SDK Web API.

    The SDK can be started locally with:
        docker run -p 5073:80 ghcr.io/green-software-foundation/carbon-aware-sdk:latest

    Or configured via CARBON_AWARE_SDK_URL environment variable to point
    at a hosted instance.
    """

    def __init__(self):
        self.base_url = os.getenv(
            "CARBON_AWARE_SDK_URL", "http://localhost:5073"
        ).rstrip("/")
        self.timeout = int(os.getenv("CARBON_AWARE_SDK_TIMEOUT", "10"))
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "CarbonIQ-CLI/0.2.0",
        })
        self._available: Optional[bool] = None

    def is_available(self) -> bool:
        """Check if the Carbon Aware SDK Web API is reachable."""
        if self._available is not None:
            return self._available
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            self._available = response.status_code in (200, 204)
        except requests.exceptions.RequestException:
            # Try the emissions endpoint as a fallback availability probe
            try:
                response = self.session.get(
                    f"{self.base_url}/emissions/bylocation",
                    params={"location": "eastus"},
                    timeout=5
                )
                self._available = response.status_code == 200
            except requests.exceptions.RequestException:
                self._available = False
        return self._available

    # ------------------------------------------------------------------
    # Core API methods
    # ------------------------------------------------------------------

    def get_current_emissions(self, aws_region: str) -> Optional[Dict[str, Any]]:
        """
        Get current carbon intensity for an AWS region.

        Returns dict with keys:
            location, time, rating, duration, carbon_intensity_avg
        """
        location = AWS_REGION_TO_SDK_LOCATION.get(aws_region, "eastus")
        try:
            response = self.session.get(
                f"{self.base_url}/emissions/bylocation",
                params={"location": location},
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                # SDK returns a list; take the most recent entry
                if isinstance(data, list) and data:
                    entry = data[-1]
                elif isinstance(data, dict):
                    entry = data
                else:
                    return None
                return {
                    "aws_region": aws_region,
                    "sdk_location": location,
                    "time": entry.get("time"),
                    "rating": entry.get("rating"),           # gCO2eq/kWh
                    "duration": entry.get("duration"),
                    "carbon_intensity": entry.get("rating"),
                    "source": "carbon_aware_sdk",
                }
            else:
                print(f"[CarbonAwareSDK] {aws_region}: HTTP {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"[CarbonAwareSDK] Error querying {aws_region}: {e}")
            return None

    def get_best_location(
        self,
        aws_regions: List[str],
        time: Optional[str] = None,
        to_time: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Find the region with the lowest carbon intensity right now.

        Args:
            aws_regions: List of AWS region codes.
            time: ISO 8601 start time (defaults to now).
            to_time: ISO 8601 end time (defaults to time + 1h).

        Returns:
            Dict with best region details and full comparison table.
        """
        locations = [
            AWS_REGION_TO_SDK_LOCATION.get(r, r) for r in aws_regions
        ]

        if not time:
            time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if not to_time:
            dt = datetime.fromisoformat(time.replace("Z", "+00:00"))
            to_time = (dt + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            response = self.session.get(
                f"{self.base_url}/emissions/bylocations/best",
                params={
                    "locations": locations,
                    "time": time,
                    "toTime": to_time,
                },
                timeout=self.timeout
            )
            if response.status_code == 200:
                best = response.json()
                # Resolve SDK location back to AWS region
                sdk_loc = best.get("location", "")
                best_region = SDK_LOCATION_TO_AWS_REGION.get(sdk_loc, sdk_loc)
                return {
                    "best_aws_region": best_region,
                    "best_sdk_location": sdk_loc,
                    "best_rating": best.get("rating"),
                    "best_time": best.get("time"),
                    "queried_at": datetime.now(timezone.utc).isoformat(),
                    "source": "carbon_aware_sdk",
                }
            else:
                print(f"[CarbonAwareSDK] best-location HTTP {response.status_code}: {response.text[:200]}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"[CarbonAwareSDK] Error finding best location: {e}")
            return None

    def get_all_locations_emissions(
        self,
        aws_regions: List[str],
        time: Optional[str] = None,
        to_time: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get carbon intensity for multiple regions simultaneously.

        Returns list of dicts sorted by carbon_intensity ascending.
        """
        locations = [
            AWS_REGION_TO_SDK_LOCATION.get(r, r) for r in aws_regions
        ]

        if not time:
            time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if not to_time:
            dt = datetime.fromisoformat(time.replace("Z", "+00:00"))
            to_time = (dt + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            response = self.session.get(
                f"{self.base_url}/emissions/bylocations",
                params={
                    "locations": locations,
                    "time": time,
                    "toTime": to_time,
                },
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                results = []
                seen_locations = {}

                # SDK may return multiple data points per location; keep latest
                for entry in (data if isinstance(data, list) else [data]):
                    loc = entry.get("location", "")
                    aws_region = SDK_LOCATION_TO_AWS_REGION.get(loc, loc)
                    rating = entry.get("rating")
                    if rating is not None:
                        if loc not in seen_locations:
                            seen_locations[loc] = {
                                "aws_region": aws_region,
                                "sdk_location": loc,
                                "carbon_intensity": float(rating),
                                "time": entry.get("time"),
                                "source": "carbon_aware_sdk",
                            }

                results = sorted(
                    seen_locations.values(),
                    key=lambda x: x["carbon_intensity"]
                )
                return results
            else:
                print(f"[CarbonAwareSDK] bylocations HTTP {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"[CarbonAwareSDK] Error getting all locations: {e}")
            return []

    def get_forecast(
        self,
        aws_region: str,
        window_duration_minutes: int = 60,
        look_ahead_hours: int = 24,
    ) -> Optional[Dict[str, Any]]:
        """
        Get the optimal future time window for running a workload.

        Uses /emissions/forecasts/current to find the lowest-carbon
        window within the next `look_ahead_hours`.

        Args:
            aws_region: AWS region to query.
            window_duration_minutes: How long the workload will run.
            look_ahead_hours: How far ahead to search.

        Returns:
            Dict with optimal_window_start, optimal_window_end, and forecast data.
        """
        location = AWS_REGION_TO_SDK_LOCATION.get(aws_region, "eastus")
        now = datetime.now(timezone.utc)
        look_ahead_end = now + timedelta(hours=look_ahead_hours)

        try:
            response = self.session.get(
                f"{self.base_url}/emissions/forecasts/current",
                params={
                    "location": location,
                    "dataStartAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "dataEndAt": look_ahead_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "windowSize": window_duration_minutes,
                },
                timeout=self.timeout
            )
            if response.status_code == 200:
                forecast_data = response.json()
                # SDK returns list; find the optimal window
                if isinstance(forecast_data, list) and forecast_data:
                    forecast = forecast_data[0]
                    optimal = forecast.get("optimalDataPoints", [])
                    all_points = forecast.get("forecastData", [])

                    best_point = None
                    if optimal:
                        best_point = optimal[0]
                    elif all_points:
                        best_point = min(all_points, key=lambda x: x.get("value", float("inf")))

                    if best_point:
                        return {
                            "aws_region": aws_region,
                            "sdk_location": location,
                            "optimal_window_start": best_point.get("timestamp"),
                            "optimal_carbon_intensity": best_point.get("value"),
                            "window_duration_minutes": window_duration_minutes,
                            "forecast_generated_at": forecast.get("generatedAt"),
                            "source": "carbon_aware_sdk_forecast",
                        }
                return None
            else:
                print(f"[CarbonAwareSDK] forecast HTTP {response.status_code}: {response.text[:200]}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"[CarbonAwareSDK] Forecast error for {aws_region}: {e}")
            return None

    def get_average_carbon_intensity(
        self,
        aws_region: str,
        start_time: str,
        end_time: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get average carbon intensity for a region over a time range.

        Args:
            aws_region: AWS region code.
            start_time: ISO 8601 start time.
            end_time: ISO 8601 end time.

        Returns:
            Dict with average carbon intensity and time range.
        """
        location = AWS_REGION_TO_SDK_LOCATION.get(aws_region, "eastus")
        try:
            response = self.session.get(
                f"{self.base_url}/emissions/average-carbon-intensity",
                params={
                    "location": location,
                    "startTime": start_time,
                    "endTime": end_time,
                },
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "aws_region": aws_region,
                    "sdk_location": location,
                    "carbon_intensity": data.get("carbonIntensity"),
                    "start_time": start_time,
                    "end_time": end_time,
                    "source": "carbon_aware_sdk_average",
                }
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"[CarbonAwareSDK] Average intensity error: {e}")
            return None

    def compare_regions(
        self,
        aws_regions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Compare carbon intensity across multiple regions right now.
        Returns a comprehensive comparison dict ready for agent analysis.
        """
        regions = aws_regions or DEFAULT_COMPARISON_REGIONS
        all_data = self.get_all_locations_emissions(regions)

        if not all_data:
            # Fallback: query individually
            all_data = []
            for region in regions:
                result = self.get_current_emissions(region)
                if result:
                    all_data.append(result)
            all_data.sort(key=lambda x: x.get("carbon_intensity", float("inf")))

        if not all_data:
            return {
                "available": False,
                "error": "Carbon Aware SDK not reachable. Start it with: docker run -p 5073:80 ghcr.io/green-software-foundation/carbon-aware-sdk:latest",
                "regions_queried": regions,
            }

        best = all_data[0] if all_data else None
        worst = all_data[-1] if all_data else None
        avg_intensity = (
            sum(r["carbon_intensity"] for r in all_data) / len(all_data)
            if all_data else None
        )

        return {
            "available": True,
            "queried_at": datetime.now(timezone.utc).isoformat(),
            "regions": all_data,
            "best_region": best,
            "worst_region": worst,
            "average_intensity": round(avg_intensity, 2) if avg_intensity else None,
            "total_regions_compared": len(all_data),
            "source": "carbon_aware_sdk",
        }
