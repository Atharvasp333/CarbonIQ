"""
CLI Measurements API Routes
Handles workload measurements from CarbonIQ CLI
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import logging

from database import get_pool
from routes.auth import get_current_user
from routes.api_keys import get_current_user_or_api_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cli", tags=["cli"])


class MeasurementData(BaseModel):
    """Measurement data from CodeCarbon"""
    duration_seconds: float
    emissions_gco2e: float
    energy_kwh: float
    cpu_energy: Optional[float] = None
    ram_energy: Optional[float] = None
    carbon_intensity: Optional[float] = None
    country_name: Optional[str] = None


class WorkloadMeasurementCreate(BaseModel):
    """Request to create a workload measurement"""
    workload_name: str
    workload_type: Optional[str] = "general"
    measurement: MeasurementData
    carbon_aware_data: Optional[dict] = None
    deadline: Optional[str] = None
    measured_at: Optional[str] = None


@router.post("/measurements")
async def create_measurement(
    data: WorkloadMeasurementCreate,
    current_user: Optional[dict] = Depends(get_current_user_or_api_key)
):
    """
    Store a CLI workload measurement.
    Personalized to user if API key or JWT token is provided.
    Falls back to user_id=1 for legacy / unauthenticated CLI runs.
    """
    user_id = current_user['id'] if current_user else 1
    user_label = f"User #{user_id} ({current_user.get('email', 'anonymous')})" if current_user else "Default CLI User (ID: 1)"
    
    print("=" * 80)
    print(f"POST /api/cli/measurements - {user_label}")
    print(f"Workload: {data.workload_name} ({data.workload_type})")
    print("=" * 80)
    
    try:
        pool = await get_pool()
        
        # Parse measured_at timestamp
        measured_at = None
        if data.measured_at:
            try:
                measured_at = datetime.fromisoformat(data.measured_at.replace('Z', '+00:00'))
            except Exception as e:
                logger.warning(f"Could not parse measured_at: {e}")
        
        # Build metadata
        import json as _json
        metadata = _json.dumps({
            "carbon_aware_data": data.carbon_aware_data,
            "deadline": data.deadline,
            "source": "cli"
        })
        
        async with pool.acquire() as conn:
            measurement_id = await conn.fetchval("""
                INSERT INTO workload_measurements
                    (user_id, workload_name, workload_type, duration_seconds,
                     emissions_gco2e, energy_kwh, cpu_energy_kwh, ram_energy_kwh,
                     carbon_intensity, country_name, measured_at, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING id
            """,
                user_id,
                data.workload_name,
                data.workload_type,
                float(data.measurement.duration_seconds),
                float(data.measurement.emissions_gco2e),
                float(data.measurement.energy_kwh),
                float(data.measurement.cpu_energy or 0),
                float(data.measurement.ram_energy or 0),
                float(data.measurement.carbon_intensity or 0),
                data.measurement.country_name,
                measured_at,
                metadata
            )
        
        print(f"✓ Measurement saved with ID: {measurement_id} for user_id={user_id}")
        print("=" * 80)
        
        return {
            "success": True,
            "measurement_id": measurement_id,
            "user_id": user_id,
            "message": "Measurement stored successfully"
        }
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Failed to store measurement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/measurements/history")
async def get_measurement_history(
    limit: int = 50,
    workload_type: Optional[str] = None,
    current_user: Optional[dict] = Depends(get_current_user_or_api_key)
):
    """
    Get measurement history.
    Returns measurements for authenticated user, or user_id=1 as default.
    """
    user_id = current_user['id'] if current_user else 1
    print(f"GET /api/cli/measurements/history - user_id={user_id}, limit={limit}")
    
    try:
        pool = await get_pool()
        
        async with pool.acquire() as conn:
            if workload_type:
                rows = await conn.fetch("""
                    SELECT 
                        id, workload_name, workload_type, duration_seconds,
                        emissions_gco2e, energy_kwh, carbon_intensity,
                        country_name, measured_at, created_at
                    FROM workload_measurements
                    WHERE user_id = $1 AND workload_type = $2
                    ORDER BY measured_at DESC
                    LIMIT $3
                """, user_id, workload_type, limit)
            else:
                rows = await conn.fetch("""
                    SELECT 
                        id, workload_name, workload_type, duration_seconds,
                        emissions_gco2e, energy_kwh, carbon_intensity,
                        country_name, measured_at, created_at
                    FROM workload_measurements
                    WHERE user_id = $1
                    ORDER BY measured_at DESC
                    LIMIT $2
                """, user_id, limit)
        
        measurements = []
        for row in rows:
            measurements.append({
                'id': row['id'],
                'workload_name': row['workload_name'],
                'workload_type': row['workload_type'],
                'duration_seconds': float(row['duration_seconds']) if row['duration_seconds'] else 0,
                'emissions_gco2e': float(row['emissions_gco2e']) if row['emissions_gco2e'] else 0,
                'energy_kwh': float(row['energy_kwh']) if row['energy_kwh'] else 0,
                'carbon_intensity': float(row['carbon_intensity']) if row['carbon_intensity'] else 0,
                'country_name': row['country_name'],
                'measured_at': row['measured_at'].isoformat() if row['measured_at'] else None,
                'created_at': row['created_at'].isoformat() if row['created_at'] else None
            })
        
        return {
            'measurements': measurements,
            'total': len(measurements),
            'user_id': user_id
        }
        
    except Exception as e:
        print(f"ERROR: {e}")
        logger.error(f"Failed to fetch history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/measurements/stats")
async def get_measurement_stats(
    current_user: Optional[dict] = Depends(get_current_user_or_api_key)
):
    """
    Get aggregate statistics for measurements for current user.
    """
    user_id = current_user['id'] if current_user else 1
    print(f"GET /api/cli/measurements/stats - user_id={user_id}")
    
    try:
        pool = await get_pool()
        
        async with pool.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_measurements,
                    SUM(emissions_gco2e) as total_emissions,
                    SUM(energy_kwh) as total_energy,
                    AVG(emissions_gco2e) as avg_emissions,
                    AVG(duration_seconds) as avg_duration
                FROM workload_measurements
                WHERE user_id = $1
            """, user_id)
            
            # Get workload type breakdown
            type_breakdown = await conn.fetch("""
                SELECT 
                    workload_type,
                    COUNT(*) as count,
                    SUM(emissions_gco2e) as total_emissions
                FROM workload_measurements
                WHERE user_id = $1
                GROUP BY workload_type
                ORDER BY total_emissions DESC
            """, user_id)
        
        types = []
        for row in type_breakdown:
            types.append({
                'workload_type': row['workload_type'],
                'count': row['count'],
                'total_emissions': float(row['total_emissions']) if row['total_emissions'] else 0
            })
        
        return {
            'user_id': user_id,
            'total_measurements': stats['total_measurements'] if stats else 0,
            'total_emissions_gco2e': float(stats['total_emissions']) if stats and stats['total_emissions'] else 0,
            'total_energy_kwh': float(stats['total_energy']) if stats and stats['total_energy'] else 0,
            'avg_emissions_gco2e': float(stats['avg_emissions']) if stats and stats['avg_emissions'] else 0,
            'avg_duration_seconds': float(stats['avg_duration']) if stats and stats['avg_duration'] else 0,
            'workload_types': types
        }
        
    except Exception as e:
        print(f"ERROR: {e}")
        logger.error(f"Failed to fetch stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
