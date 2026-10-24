"""
CarbonIQ Backend Client
Handles communication with the CarbonIQ FastAPI backend.
"""

import requests
from typing import Dict, Optional
try:
    from cli.config_manager import get_api_key
except ImportError:
    from config_manager import get_api_key


class BackendClient:
    """Client for communicating with CarbonIQ backend API."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize backend client.
        
        Args:
            base_url: Base URL of the CarbonIQ API (e.g., http://localhost:8000/api)
            api_key: Optional API key for authenticating as a specific user
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or get_api_key()
        self.session = requests.Session()
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'CarbonIQ-CLI/0.1.0'
        }
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        self.session.headers.update(headers)
    
    def health_check(self) -> bool:
        """
        Check if the backend is healthy and reachable.
        
        Returns:
            True if backend is healthy, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"[Backend] Status: {data.get('status', 'unknown')}")
                
                keys_loaded = data.get('keys_loaded', {})
                print(f"[Backend] Keys loaded: {keys_loaded}")
                
                return data.get('status') == 'ok'
            else:
                print(f"[Backend] Health check failed with status {response.status_code}")
                return False
        
        except requests.exceptions.RequestException as e:
            print(f"[Backend] Connection error: {e}")
            return False
    
    def send_measurement(self, measurement_data: Dict) -> bool:
        """
        Send workload measurement data to the backend.
        
        Args:
            measurement_data: Dictionary containing measurement results
        
        Returns:
            True if successful, False otherwise
        """
        try:
            endpoint = f"{self.base_url}/cli/measurements"
            
            print(f"[Backend] Sending to: {endpoint}")
            
            response = self.session.post(
                endpoint,
                json=measurement_data,
                timeout=10
            )
            
            if response.status_code == 200 or response.status_code == 201:
                print(f"[Backend] Measurement sent successfully")
                
                # Try to parse response
                try:
                    result = response.json()
                    if result.get('measurement_id'):
                        print(f"[Backend] Measurement ID: {result['measurement_id']}")
                except:
                    pass
                
                return True
            else:
                print(f"[Backend] Failed with status {response.status_code}")
                print(f"[Backend] Response: {response.text}")
                return False
        
        except requests.exceptions.RequestException as e:
            print(f"[Backend] Error sending measurement: {e}")
            return False
    
    def get_recommendations(
        self,
        workload_id: str,
        constraints: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Get deployment recommendations from the backend.
        
        Args:
            workload_id: ID of the measured workload
            constraints: Optional constraints (regions, deadline, budget, etc.)
        
        Returns:
            Dictionary with recommendations, or None if failed
        """
        try:
            endpoint = f"{self.base_url}/cli/recommendations"
            
            payload = {
                "workload_id": workload_id,
                "constraints": constraints or {}
            }
            
            response = self.session.post(
                endpoint,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[Backend] Failed to get recommendations: {response.status_code}")
                return None
        
        except requests.exceptions.RequestException as e:
            print(f"[Backend] Error getting recommendations: {e}")
            return None
