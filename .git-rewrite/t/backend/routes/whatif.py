from fastapi import APIRouter
from models.schemas import WhatIfAWSRequest, WhatIfAWSResponse

router = APIRouter()


@router.post("/whatif", response_model=WhatIfAWSResponse)
async def simulate_whatif(request: WhatIfAWSRequest):
    # Mock baseline data
    current_co2 = 450.0
    current_cost = 150.0
    
    if request.scenario == "move_region":
        # Moving from high-carbon to low-carbon region
        projected_co2 = current_co2 * 0.65  # 35% reduction
        projected_cost = current_cost * 0.98
        description = f"Moving workloads to {request.target_region} reduces emissions by 35%"
    
    elif request.scenario == "downsize_instance":
        # Downsizing instances
        projected_co2 = current_co2 * 0.75  # 25% reduction
        projected_cost = current_cost * 0.70
        description = f"Downsizing to {request.target_instance} reduces emissions by 25%"
    
    elif request.scenario == "remove_idle":
        # Removing idle resources
        projected_co2 = current_co2 * 0.85  # 15% reduction
        projected_cost = current_cost * 0.80
        description = "Removing idle resources reduces emissions by 15%"
    
    else:
        projected_co2 = current_co2
        projected_cost = current_cost
        description = "No changes"
    
    return WhatIfAWSResponse(
        scenario_name=request.scenario,
        current_co2_kg=round(current_co2, 2),
        projected_co2_kg=round(projected_co2, 2),
        savings_kg=round(current_co2 - projected_co2, 2),
        savings_cost=round(current_cost - projected_cost, 2),
        description=description
    )
