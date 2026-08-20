from fastapi import APIRouter
from models.schemas import RegionalTestRequest, RegionalTestResponse
from services.climatiq import test_regional_emission, REGIONAL_FACTORS

router = APIRouter()


@router.post("/test-regional-emission", response_model=RegionalTestResponse)
async def test_emission(request: RegionalTestRequest):
    """Test emission calculation for a specific region"""
    return await test_regional_emission(request)


@router.get("/available-regions")
async def get_available_regions():
    """Get list of all available regions"""
    regions = []
    for code, info in REGIONAL_FACTORS.items():
        regions.append({
            "code": code,
            "name": info["name"],
            "factor": info["factor"],
            "type": info["type"]
        })
    return {"regions": regions}
