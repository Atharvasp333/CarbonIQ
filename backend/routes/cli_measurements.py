"""
CLI Measurements Route
Handles workload measurement data from the CarbonIQ CLI.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class MeasurementData(BaseModel):
    """Schema for workload measurement data from CLI."""
    workload_name: str = Field(..., description="Name of the measured workload")
    workload_type: str = Field(default="general", description="Type of workload")
    measurement: Dict[str, Any] = Field(..., description="CodeCarbon measurement results")
    carbon_aware_data: Optional[Dict[str, Any]] = Field(None, description="Carbon Aware SDK data")
    deadline: Optional[str] = Field(None, description="Workload deadline (ISO 8601)")
    measured_at: str = Field(..., description="Measurement timestamp (ISO 8601)")


class MeasurementResponse(BaseModel):
    """Response after receiving a measurement."""
    success: bool
    measurement_id: str
    message: str
    recommendations_available: bool = False


class RecommendationRequest(BaseModel):
    """Request for deployment recommendations."""
    workload_id: str
    constraints: Optional[Dict[str, Any]] = Field(default_factory=dict)


# In-memory storage for demo (replace with database in production)
measurements_store = {}
measurement_counter = 0


@router.post("/cli/measurements", response_model=MeasurementResponse)
async def receive_measurement(data: MeasurementData):
    """
    Receive workload measurement data from CLI.
    
    This endpoint stores the measurement and prepares it for analysis.
    """
    global measurement_counter
    
    try:
        measurement_counter += 1
        measurement_id = f"meas_{measurement_counter}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Store the measurement
        measurements_store[measurement_id] = {
            "id": measurement_id,
            "workload_name": data.workload_name,
            "workload_type": data.workload_type,
            "measurement": data.measurement,
            "carbon_aware_data": data.carbon_aware_data,
            "deadline": data.deadline,
            "measured_at": data.measured_at,
            "received_at": datetime.utcnow().isoformat(),
            "status": "received"
        }
        
        logger.info(f"Received measurement: {measurement_id} for workload '{data.workload_name}'")
        logger.info(f"Emissions: {data.measurement.get('emissions_gco2e', 'N/A')} gCO2e")
        logger.info(f"Duration: {data.measurement.get('duration_seconds', 'N/A')}s")
        
        return MeasurementResponse(
            success=True,
            measurement_id=measurement_id,
            message=f"Measurement received successfully for '{data.workload_name}'",
            recommendations_available=False  # Will be True once recommendation engine is implemented
        )
    
    except Exception as e:
        logger.error(f"Error receiving measurement: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store measurement: {str(e)}")


@router.get("/cli/measurements")
async def list_measurements():
    """
    List all stored measurements.
    """
    measurements = list(measurements_store.values())
    
    # Sort by received_at (most recent first)
    measurements.sort(key=lambda x: x.get('received_at', ''), reverse=True)
    
    return {
        "count": len(measurements),
        "measurements": measurements
    }


@router.get("/cli/measurements/{measurement_id}")
async def get_measurement(measurement_id: str):
    """
    Get a specific measurement by ID.
    """
    if measurement_id not in measurements_store:
        raise HTTPException(status_code=404, detail=f"Measurement {measurement_id} not found")
    
    return measurements_store[measurement_id]


@router.delete("/cli/measurements/{measurement_id}")
async def delete_measurement(measurement_id: str):
    """
    Delete a measurement.
    """
    if measurement_id not in measurements_store:
        raise HTTPException(status_code=404, detail=f"Measurement {measurement_id} not found")
    
    deleted = measurements_store.pop(measurement_id)
    
    return {
        "success": True,
        "message": f"Measurement {measurement_id} deleted",
        "deleted_measurement": deleted
    }


@router.post("/cli/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """
    Get deployment recommendations for a measured workload.
    
    This is a placeholder for the future recommendation engine.
    """
    # Check if measurement exists
    if request.workload_id not in measurements_store:
        raise HTTPException(status_code=404, detail=f"Workload {request.workload_id} not found")
    
    measurement = measurements_store[request.workload_id]
    
    # TODO: Implement actual recommendation engine
    # For now, return a placeholder response
    
    return {
        "workload_id": request.workload_id,
        "workload_name": measurement["workload_name"],
        "recommendations": [
            {
                "rank": 1,
                "region": "us-east-1",
                "estimated_emissions_gco2e": measurement["measurement"].get("emissions_gco2e", 0) * 0.8,
                "estimated_cost_usd": 10.50,
                "estimated_latency_ms": 45,
                "reason": "Lower carbon intensity expected in this region during the specified window",
                "confidence": "medium"
            },
            {
                "rank": 2,
                "region": "eu-west-1",
                "estimated_emissions_gco2e": measurement["measurement"].get("emissions_gco2e", 0) * 0.9,
                "estimated_cost_usd": 12.00,
                "estimated_latency_ms": 120,
                "reason": "Good renewable energy mix, but higher latency from your location",
                "confidence": "medium"
            }
        ],
        "constraints_applied": request.constraints,
        "generated_at": datetime.utcnow().isoformat(),
        "note": "This is a placeholder response. Full recommendation engine coming soon."
    }


@router.get("/cli/stats")
async def get_cli_stats():
    """
    Get statistics about CLI measurements.
    """
    if not measurements_store:
        return {
            "total_measurements": 0,
            "total_emissions_gco2e": 0,
            "total_energy_kwh": 0,
            "workload_types": {}
        }
    
    total_emissions = 0
    total_energy = 0
    workload_types = {}
    
    for measurement in measurements_store.values():
        # Sum emissions
        emissions = measurement["measurement"].get("emissions_gco2e", 0)
        total_emissions += emissions
        
        # Sum energy
        energy = measurement["measurement"].get("energy_kwh", 0)
        total_energy += energy
        
        # Count workload types
        wtype = measurement.get("workload_type", "unknown")
        workload_types[wtype] = workload_types.get(wtype, 0) + 1
    
    return {
        "total_measurements": len(measurements_store),
        "total_emissions_gco2e": round(total_emissions, 2),
        "total_energy_kwh": round(total_energy, 6),
        "average_emissions_gco2e": round(total_emissions / len(measurements_store), 2),
        "workload_types": workload_types,
        "latest_measurement": max(
            measurements_store.values(),
            key=lambda x: x.get('received_at', '')
        ) if measurements_store else None
    }
