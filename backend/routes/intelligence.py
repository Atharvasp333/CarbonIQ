"""
Intelligence Engine API Routes
Handles sustainability intelligence generation and recommendations
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
import logging

from database import get_pool
from models.schemas import RecommendationRunResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])


@router.post("/generate-insights")
async def generate_insights():
    """
    Generate sustainability insights from stored analysis data
    
    This endpoint:
    1. Loads latest analysis_summary from database
    2. Loads emission_records from database
    3. Loads organization_profile
    4. Runs Intelligence Engine pipeline
    5. Stores results in recommendation_runs table
    6. Returns recommendations
    
    NOTE: Currently returns placeholder response
    TODO: Implement full intelligence engine integration
    """
    logger.info("=" * 80)
    logger.info("POST /api/intelligence/generate-insights - Request received")
    logger.info("=" * 80)
    
    try:
        pool = await get_pool()
        logger.info("✓ Database pool acquired")
        
        async with pool.acquire() as conn:
            logger.info("✓ Database connection acquired")
            
            # Check if analysis_history table exists
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'analysis_history'
                )
            """)
            
            logger.info(f"✓ Table 'analysis_history' exists: {table_exists}")
            
            if not table_exists:
                logger.warning("✗ Table 'analysis_history' does not exist")
                return {
                    'success': False,
                    'message': 'Database tables not initialized. Please run migrations.',
                    'analysis_id': None,
                    'profile_configured': False
                }
            
            # Get latest analysis
            analysis = await conn.fetchrow("""
                SELECT id, user_id, total_emissions, total_cost
                FROM analysis_history
                ORDER BY uploaded_at DESC
                LIMIT 1
            """)
            
            if not analysis:
                logger.warning("✗ No analysis data found in database")
                raise HTTPException(
                    status_code=404, 
                    detail="No analysis data found. Please upload CUR data first."
                )
            
            logger.info(f"✓ Found analysis: ID={analysis['id']}")
            
            # Get organization profile
            profile = await conn.fetchrow("""
                SELECT * FROM organization_profile
                ORDER BY created_at DESC
                LIMIT 1
            """)
            
            logger.info(f"✓ Organization profile: {'Found' if profile else 'Not found'}")
            
            # TODO: Implement intelligence engine integration
            # For now, return success message
            response = {
                'success': True,
                'message': 'Intelligence generation triggered',
                'analysis_id': analysis['id'],
                'profile_configured': profile is not None
            }
            
            logger.info(f"✓ Response: {response}")
            logger.info("=" * 80)
            return response
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"✗ ERROR in generate_insights: {e}", exc_info=True)
        logger.error("=" * 80)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations")
async def get_recommendations():
    """
    Get latest recommendation run
    
    Returns the most recent recommendation_run from the database
    """
    logger.info("=" * 80)
    logger.info("GET /api/intelligence/recommendations - Request received")
    logger.info("=" * 80)
    
    try:
        pool = await get_pool()
        logger.info("✓ Database pool acquired")
        
        async with pool.acquire() as conn:
            logger.info("✓ Database connection acquired")
            
            # Check if recommendation_runs table exists
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'recommendation_runs'
                )
            """)
            
            logger.info(f"✓ Table 'recommendation_runs' exists: {table_exists}")
            
            if not table_exists:
                logger.warning("✗ Table 'recommendation_runs' does not exist")
                raise HTTPException(
                    status_code=404,
                    detail="Database tables not initialized. Please run migrations."
                )
            
            # Get latest recommendation run
            row = await conn.fetchrow("""
                SELECT 
                    id,
                    user_id,
                    analysis_id,
                    run_type,
                    generated_at,
                    findings,
                    recommendations,
                    hotspots,
                    region_opportunities,
                    time_opportunities,
                    confidence_score,
                    metadata,
                    status
                FROM recommendation_runs
                ORDER BY generated_at DESC
                LIMIT 1
            """)
            
            if not row:
                logger.info("✗ No recommendation runs found in database")
                # Return empty response instead of 404
                response = {
                    'id': None,
                    'generated_at': None,
                    'recommendations': [],
                    'patterns': [],
                    'opportunities': [],
                    'summary': {},
                    'workload_analysis': {},
                    'hotspots': [],
                    'region_opportunities': [],
                    'time_opportunities': [],
                    'confidence_score': None,
                    'status': 'no_data'
                }
            else:
                logger.info(f"✓ Found recommendation run: ID={row['id']}")
                
                # Convert row to dict and extract intelligence data
                rec_data = dict(row)
                
                # Return structured response
                response = {
                    'id': rec_data['id'],
                    'generated_at': rec_data['generated_at'].isoformat() if rec_data['generated_at'] else None,
                    'recommendations': rec_data['recommendations'] or [],
                    'patterns': rec_data['metadata'].get('patterns', []) if rec_data['metadata'] else [],
                    'opportunities': rec_data['metadata'].get('opportunities', []) if rec_data['metadata'] else [],
                    'summary': rec_data['findings'] or {},
                    'workload_analysis': rec_data['metadata'].get('workload_analysis', {}) if rec_data['metadata'] else {},
                    'hotspots': rec_data['hotspots'] or [],
                    'region_opportunities': rec_data['region_opportunities'] or [],
                    'time_opportunities': rec_data['time_opportunities'] or [],
                    'confidence_score': rec_data['confidence_score'],
                    'status': rec_data['status']
                }
            
            logger.info(f"✓ Returning {len(response['recommendations'])} recommendations")
            logger.info("=" * 80)
            return response
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"✗ ERROR in get_recommendations: {e}", exc_info=True)
        logger.error("=" * 80)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/history")
async def get_recommendation_history():
    """
    Get all recommendation runs ordered by date
    
    Returns list of past recommendation runs
    """
    try:
        pool = await get_pool()
        
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    id,
                    generated_at,
                    run_type,
                    status,
                    confidence_score,
                    jsonb_array_length(recommendations) as recommendation_count
                FROM recommendation_runs
                ORDER BY generated_at DESC
                LIMIT 50
            """)
            
            history = []
            for row in rows:
                history.append({
                    'id': row['id'],
                    'generated_at': row['generated_at'].isoformat() if row['generated_at'] else None,
                    'run_type': row['run_type'],
                    'status': row['status'],
                    'confidence_score': row['confidence_score'],
                    'recommendation_count': row['recommendation_count']
                })
            
            return {
                'history': history,
                'total': len(history)
            }
            
    except Exception as e:
        logger.error(f"Failed to fetch recommendation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/{recommendation_id}")
async def get_recommendation_by_id(recommendation_id: int):
    """
    Get specific recommendation run by ID
    """
    try:
        pool = await get_pool()
        
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    id,
                    user_id,
                    analysis_id,
                    run_type,
                    generated_at,
                    findings,
                    recommendations,
                    hotspots,
                    region_opportunities,
                    time_opportunities,
                    confidence_score,
                    metadata,
                    status
                FROM recommendation_runs
                WHERE id = $1
            """, recommendation_id)
            
            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"Recommendation run {recommendation_id} not found"
                )
            
            rec_data = dict(row)
            
            return {
                'id': rec_data['id'],
                'generated_at': rec_data['generated_at'].isoformat() if rec_data['generated_at'] else None,
                'recommendations': rec_data['recommendations'] or [],
                'patterns': rec_data['metadata'].get('patterns', []) if rec_data['metadata'] else [],
                'opportunities': rec_data['metadata'].get('opportunities', []) if rec_data['metadata'] else [],
                'summary': rec_data['findings'] or {},
                'workload_analysis': rec_data['metadata'].get('workload_analysis', {}) if rec_data['metadata'] else {},
                'hotspots': rec_data['hotspots'] or [],
                'region_opportunities': rec_data['region_opportunities'] or [],
                'time_opportunities': rec_data['time_opportunities'] or [],
                'confidence_score': rec_data['confidence_score'],
                'status': rec_data['status']
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
