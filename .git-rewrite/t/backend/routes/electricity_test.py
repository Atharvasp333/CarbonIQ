from fastapi import APIRouter, HTTPException, Query
import requests
import os
from datetime import datetime

router = APIRouter()

ELECTRICITY_MAPS_ZONES = {
    "India": [
        {"code": "IN", "name": "Mainland India"},
        {"code": "IN-EA", "name": "East India"},
        {"code": "IN-WE", "name": "West India"},
        {"code": "IN-SO", "name": "South India"},
        {"code": "IN-NO", "name": "North India"}
    ],
    "USA": [
        {"code": "US-CAL-CISO", "name": "California"},
        {"code": "US-TEX-ERCO", "name": "Texas"},
        {"code": "US-MIDA-PJM", "name": "Mid-Atlantic"}
    ],
    "Europe": [
        {"code": "FR", "name": "France"},
        {"code": "DE", "name": "Germany"},
        {"code": "GB", "name": "United Kingdom"},
        {"code": "NO", "name": "Norway"}
    ]
}


@router.get("/electricity/test")
async def test_electricity_maps(
    zone: str = Query(..., description="Electricity Maps zone code"),
    datetime_str: str = Query(..., alias="datetime", description="Datetime in format YYYY-MM-DD HH:MM")
):
    """Test Electricity Maps API integration"""
    
    api_key = os.getenv("ELECTRICITY_MAPS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Electricity Maps API key not configured")
    
    # Validate zone
    all_zones = []
    for region_zones in ELECTRICITY_MAPS_ZONES.values():
        all_zones.extend([z["code"] for z in region_zones])
    
    if zone not in all_zones:
        raise HTTPException(status_code=400, detail=f"Invalid zone: {zone}")
    
    # Validate datetime format
    try:
        datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format. Use YYYY-MM-DD HH:MM")
    
    # Call Electricity Maps API
    try:
        response = requests.get(
            "https://api.electricitymaps.com/v3/carbon-intensity/past",
            params={
                "zone": zone,
                "datetime": datetime_str
            },
            headers={
                "auth-token": api_key
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "zone": zone,
                "datetime": datetime_str,
                "carbon_intensity": data.get("carbonIntensity"),
                "carbon_intensity_lifecycle": data.get("carbonIntensityLifecycle"),
                "zone_name": data.get("zone"),
                "timestamp": data.get("datetime"),
                "raw_response": data
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Electricity Maps API error: {response.text}"
            )
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")


@router.get("/electricity/zones")
async def get_zones():
    """Get all available Electricity Maps zones"""
    return ELECTRICITY_MAPS_ZONES
