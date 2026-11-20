from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
import logging
from routes.api_keys import get_current_user_or_api_key

router = APIRouter()
logger = logging.getLogger(__name__)

# Store the latest analysis results in memory
# In production, use Redis or database
_analysis_cache = {}


@router.post("/service-analytics/store")
async def store_analysis_results(data: dict):
    """
    Store multi-agent analysis results for service drill-down
    Called after multi-agent analysis completes
    """
    try:
        # Store full records for service drill-down (prefer all_records over detailed_records)
        _analysis_cache['emission_records'] = (
            data.get('all_records') or data.get('detailed_records', [])
        )
        _analysis_cache['timestamp'] = data.get('generated_at', '')
        
        return {'status': 'success', 'records_stored': len(_analysis_cache['emission_records'])}
    except Exception as e:
        logger.error(f"Failed to store analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service-analytics/{service_name}")
async def get_service_analytics(service_name: str):
    """
    Get detailed analytics for a specific service
    
    Args:
        service_name: AWS service name (ec2, lambda, s3, etc.)
    
    Returns: Comprehensive service analytics with 8 sections
    """
    try:
        from services.service_analyzer import ServiceAnalyzer
        
        # Get cached emission records
        emission_records = _analysis_cache.get('emission_records', [])
        
        if not emission_records:
            try:
                from database import get_pool
                pool = await get_pool()
                if pool is not None:
                    async with pool.acquire() as conn:
                        rows = await conn.fetch("""
                            SELECT 
                                service, region, zone, usage_type, usage_amount,
                                cost, energy_kwh, carbon_intensity, emissions_kg,
                                resource_id, intensity_source
                            FROM emission_records
                            ORDER BY id DESC
                            LIMIT 1000
                        """)
                        if rows:
                            emission_records = [dict(r) for r in rows]
                            _analysis_cache['emission_records'] = emission_records
            except Exception as db_err:
                logger.warning(f"Failed to fetch fallback emission records from DB: {db_err}")
        
        if not emission_records:
            raise HTTPException(
                status_code=404, 
                detail="No analysis data found. Please run multi-agent analysis or load demo data first."
            )
        
        # Generate service analytics
        analyzer = ServiceAnalyzer()
        analytics = analyzer.analyze_service(service_name, emission_records)
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service analytics failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service-analytics/list/all")
async def list_available_services():
    """
    List all available services from cached analysis
    
    Returns: List of services with basic metrics
    """
    try:
        emission_records = _analysis_cache.get('emission_records', [])
        
        if not emission_records:
            return {'services': []}
        
        # Group by service
        from collections import defaultdict
        service_data = defaultdict(lambda: {
            'emissions_kg': 0,
            'cost': 0,
            'count': 0
        })
        
        for record in emission_records:
            service = record.get('service', 'Unknown')
            service_data[service]['emissions_kg'] += record['emissions_kg']
            service_data[service]['cost'] += record.get('cost', 0)
            service_data[service]['count'] += 1
        
        # Format response
        services = []
        for service, data in service_data.items():
            services.append({
                'name': service,
                'display_name': service,
                'total_emissions_kg': round(data['emissions_kg'], 2),
                'total_cost': round(data['cost'], 2),
                'execution_count': data['count']
            })
        
        # Sort by emissions descending
        services.sort(key=lambda x: x['total_emissions_kg'], reverse=True)
        
        return {'services': services}
        
    except Exception as e:
        logger.error(f"Failed to list services: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/latest")
async def get_latest_analysis(current_user: Optional[dict] = Depends(get_current_user_or_api_key)):
    """Return the most recent analysis summary for fast dashboard hydration."""
    try:
        from database import get_pool
        pool = await get_pool()
        if pool is None:
            raise HTTPException(status_code=500, detail="Database pool not available")
        user_id = current_user.get('id') if current_user else None
        async with pool.acquire() as conn:
            row = None
            if user_id:
                row = await conn.fetchrow("""
                    SELECT * FROM analyses WHERE user_id = $1 ORDER BY created_at DESC LIMIT 1
                """, user_id)
            if not row:
                row = await conn.fetchrow("""
                    SELECT * FROM analyses ORDER BY created_at DESC LIMIT 1
                """)
            if not row:
                return {"success": False, "message": "No analysis found"}
            r = dict(row)
            for k, v in r.items():
                if hasattr(v, 'isoformat'):
                    r[k] = v.isoformat()
            # Build standard summary structure
            return {
                "success": True,
                "analysis_id": r["id"],
                "summary": {
                    "total_emissions_kg": float(r.get("total_emissions", 0)),
                    "total_cost": float(r.get("total_cost", 0)),
                    "total_energy_kwh": float(r.get("total_energy", 0)),
                    "top_service": r.get("top_service", "Unknown"),
                    "top_region": r.get("top_region", "Unknown"),
                    "total_records": int(r.get("compressed_rows", 0))
                },
                "created_at": r.get("created_at")
            }
    except Exception as e:
        logger.error(f"Failed to fetch latest analysis: {e}")
        return {"success": False, "message": str(e)}


@router.get("/history")
async def get_analysis_history(current_user: Optional[dict] = Depends(get_current_user_or_api_key)):
    """Return list of past analyses from NeonDB."""
    try:
        from database import get_analysis_history
        user_id = current_user.get('id') if current_user else None
        rows = await get_analysis_history(user_id=user_id, limit=50)
        # Convert datetime objects for JSON serialisation
        for r in rows:
            for k, v in r.items():
                if hasattr(v, 'isoformat'):
                    r[k] = v.isoformat()
        return {"analyses": rows}
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{analysis_id}/records")
async def get_historical_records(
    analysis_id: int,
    current_user: Optional[dict] = Depends(get_current_user_or_api_key)
):
    """Return emission records for a specific past analysis."""
    try:
        from database import get_analysis_records
        user_id = current_user.get('id') if current_user else None
        rows = await get_analysis_records(analysis_id, user_id=user_id)
        for r in rows:
            for k, v in r.items():
                if hasattr(v, 'isoformat'):
                    r[k] = v.isoformat()
        return {"analysis_id": analysis_id, "records": rows}
    except Exception as e:
        logger.error(f"Failed to fetch records: {e}")
        raise HTTPException(status_code=500, detail=str(e))
