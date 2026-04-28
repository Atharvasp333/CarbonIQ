from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from services.energy_calculator import calculate_energy
from services.climatiq_service import estimate_emissions
from data.results_store import save_result
from datetime import datetime

router = APIRouter()

class SimulationRequest(BaseModel):
    runtime: float
    cpu_utilization: float
    region: Optional[str] = "IN"

class SimulationResponse(BaseModel):
    runtime: float
    cpu_utilization: float
    energy_kwh: float
    emissions_kg_co2e: float
    timestamp: str

@router.post("/simulate", response_model=SimulationResponse)
async def simulate_cloud_usage(req: SimulationRequest):
    """
    Simulates cloud usage and returns energy consumption and carbon emissions.
    
    ### AWS Integration (Demo Purpose Explanation)
    This endpoint simulates how we would process cloud metrics. In a real-world scenario, 
    this system can connect to AWS using the following approaches:
    
    1. AWS Cost Explorer API
       - Fetch actual usage data (e.g., EC2 hours, Lambda execution time).
       - Convert this usage data into energy estimates based on server capacities.
       
    2. Amazon CloudWatch
       - Fetch real-time `CPUUtilization` metrics for instances.
       - Use these metrics to precisely calculate dynamic energy usage instead of static averages.
       
    3. AWS Credentials Integration (Future Pipeline)
       - User provides secure IAM credentials (e.g., Role ARN or Access Keys).
       - Backend periodically fetches usage data and Cost & Usage Reports (CUR).
       - The system processes the data automatically and populates the dashboard dynamically.
       
    For demo purposes, we have a "Mock AWS Mode" via the `GET /api/mock-data` endpoint 
    which uses pre-defined sample data to show how it flows through the system (Frontend -> Backend -> Climatiq -> Dashboard).
    """
    energy_kwh = calculate_energy(req.runtime, req.cpu_utilization)
    emissions = await estimate_emissions(energy_kwh, req.region)
    
    result = {
        "type": "simulation",
        "runtime": req.runtime,
        "cpu_utilization": req.cpu_utilization,
        "energy_kwh": round(energy_kwh, 4),
        "emissions_kg_co2e": round(emissions, 4),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    save_result(result)
    return result

@router.get("/results")
async def get_all_results():
    """
    Returns previous simulation and upload results.
    """
    from data.results_store import get_results
    return get_results()
