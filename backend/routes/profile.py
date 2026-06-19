"""
Organization Profile API Routes
Manages organization sustainability profiles and questionnaires
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
import logging

from models.schemas import (
    OrganizationProfileCreate,
    OrganizationProfileUpdate,
    OrganizationProfileResponse
)
from database import get_pool

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.post("/", response_model=OrganizationProfileResponse)
async def create_profile(profile: OrganizationProfileCreate):
    """Create or update organization profile"""
    try:
        pool = await get_pool()
        
        async with pool.acquire() as conn:
            # Check if profile already exists
            existing = await conn.fetchrow("""
                SELECT id FROM organization_profile LIMIT 1
            """)
            
            if existing:
                # Update existing profile
                row = await conn.fetchrow("""
                    UPDATE organization_profile
                    SET organization_name = $1,
                        primary_user_region = $2,
                        workload_type = $3,
                        latency_sensitivity = $4,
                        migration_flexibility = $5,
                        optimization_priority = $6,
                        updated_at = NOW()
                    WHERE id = $7
                    RETURNING *
                """,
                    profile.organization_name,
                    profile.primary_user_region,
                    profile.workload_type,
                    profile.latency_sensitivity,
                    profile.migration_flexibility,
                    profile.optimization_priority,
                    existing['id']
                )
            else:
                # Create new profile
                row = await conn.fetchrow("""
                    INSERT INTO organization_profile
                        (organization_name, primary_user_region, workload_type,
                         latency_sensitivity, migration_flexibility, optimization_priority)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING *
                """,
                    profile.organization_name,
                    profile.primary_user_region,
                    profile.workload_type,
                    profile.latency_sensitivity,
                    profile.migration_flexibility,
                    profile.optimization_priority
                )
        
        return dict(row)
        
    except Exception as e:
        logger.error(f"Failed to create/update profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=Optional[OrganizationProfileResponse])
async def get_profile():
    """Get current organization profile"""
    try:
        pool = await get_pool()
        
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM organization_profile
                ORDER BY created_at DESC
                LIMIT 1
            """)
        
        return dict(row) if row else None
        
    except Exception as e:
        logger.error(f"Failed to fetch profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/", response_model=OrganizationProfileResponse)
async def update_profile(updates: OrganizationProfileUpdate):
    """Partially update organization profile"""
    try:
        pool = await get_pool()
        
        async with pool.acquire() as conn:
            # Get current profile
            current = await conn.fetchrow("""
                SELECT * FROM organization_profile
                ORDER BY created_at DESC
                LIMIT 1
            """)
            
            if not current:
                raise HTTPException(status_code=404, detail="No profile found")
            
            # Build update query
            update_fields = []
            values = []
            param_count = 1
            
            if updates.organization_name is not None:
                update_fields.append(f"organization_name = ${param_count}")
                values.append(updates.organization_name)
                param_count += 1
            
            if updates.primary_user_region is not None:
                update_fields.append(f"primary_user_region = ${param_count}")
                values.append(updates.primary_user_region)
                param_count += 1
            
            if updates.workload_type is not None:
                update_fields.append(f"workload_type = ${param_count}")
                values.append(updates.workload_type)
                param_count += 1
            
            if updates.latency_sensitivity is not None:
                update_fields.append(f"latency_sensitivity = ${param_count}")
                values.append(updates.latency_sensitivity)
                param_count += 1
            
            if updates.migration_flexibility is not None:
                update_fields.append(f"migration_flexibility = ${param_count}")
                values.append(updates.migration_flexibility)
                param_count += 1
            
            if updates.optimization_priority is not None:
                update_fields.append(f"optimization_priority = ${param_count}")
                values.append(updates.optimization_priority)
                param_count += 1
            
            if not update_fields:
                return dict(current)
            
            update_fields.append("updated_at = NOW()")
            values.append(current['id'])
            
            query = f"""
                UPDATE organization_profile
                SET {', '.join(update_fields)}
                WHERE id = ${param_count}
                RETURNING *
            """
            
            row = await conn.fetchrow(query, *values)
        
        return dict(row)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/")
async def delete_profile():
    """Delete organization profile"""
    try:
        pool = await get_pool()
        
        async with pool.acquire() as conn:
            await conn.execute("""
                DELETE FROM organization_profile
            """)
        
        return {"message": "Profile deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/options")
async def get_profile_options():
    """Get available options for profile questionnaire"""
    return {
        "primary_user_region": [
            "India",
            "North America",
            "Europe",
            "Asia Pacific",
            "Global"
        ],
        "workload_type": [
            "Production",
            "Development",
            "Testing",
            "Analytics",
            "Machine Learning",
            "Mixed"
        ],
        "latency_sensitivity": [
            "High",
            "Medium",
            "Low"
        ],
        "migration_flexibility": [
            "Yes",
            "Some Workloads",
            "No"
        ],
        "optimization_priority": [
            "Reduce Carbon",
            "Reduce Cost",
            "Balance Both"
        ]
    }
