"""
Intelligence Engine API Routes
Handles sustainability intelligence generation and recommendations
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
import logging
import os
import json

from database import get_pool, get_analysis_summary, get_analysis_records, save_recommendation_run
from models.schemas import RecommendationRunResponse
from routes.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])


@router.post("/generate-insights")
async def generate_insights(current_user=Depends(get_current_user)):
    """
    Generate sustainability insights from stored analysis data
    
    This endpoint:
    1. Loads latest analysis_summary from database
    2. Loads emission_records from database
    3. Loads organization_profile
    4. Runs Intelligence Engine pipeline
    5. Stores results in recommendation_runs table
    6. Returns recommendations
    """
    logger.info("=" * 80)
    logger.info("POST /api/intelligence/generate-insights - Request received")
    logger.info("=" * 80)
    
    # Extract authenticated user ID
    user_id = current_user['id']
    logger.info(f"✓ Authenticated user: ID={user_id}, Email={current_user['email']}")
    
    try:
        pool = await get_pool()
        logger.info("✓ Database pool acquired")
        
        async with pool.acquire() as conn:
            logger.info("✓ Database connection acquired")
            
            # Check if analyses table exists
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'analyses'
                )
            """)
            
            logger.info(f"✓ Table 'analyses' exists: {table_exists}")
            
            if not table_exists:
                logger.warning("✗ Table 'analyses' does not exist")
                return {
                    'success': False,
                    'message': 'Database tables not initialized. Please run migrations.',
                    'analysis_id': None,
                    'profile_configured': False
                }
            
            # Get latest analysis for this user
            analysis = await conn.fetchrow("""
                SELECT id, user_id, filename, total_emissions, total_cost, uploaded_at
                FROM analyses
                WHERE user_id = $1
                ORDER BY uploaded_at DESC
                LIMIT 1
            """, user_id)
            
            if not analysis:
                logger.warning(f"✗ No analysis data found for user {user_id}")
                
                # Diagnostic: Check if any analyses exist at all
                total_analyses = await conn.fetchval("SELECT COUNT(*) FROM analyses")
                analyses_with_user = await conn.fetchval("SELECT COUNT(*) FROM analyses WHERE user_id IS NOT NULL")
                
                logger.info(f"[DIAGNOSTIC] Total analyses in DB: {total_analyses}")
                logger.info(f"[DIAGNOSTIC] Analyses with user_id: {analyses_with_user}")
                logger.info(f"[DIAGNOSTIC] User {user_id} needs to upload CUR data")
                
                raise HTTPException(
                    status_code=404, 
                    detail="No analysis data found. Please upload your AWS Cost and Usage Report (CUR) data first before generating insights."
                )
            
            analysis_id = analysis['id']
            logger.info(f"✓ Found analysis: ID={analysis_id}, User={user_id}, File={analysis['filename']}")
            logger.info(f"  Uploaded: {analysis['uploaded_at']}")
            logger.info(f"  Emissions: {analysis['total_emissions']} kg, Cost: ${analysis['total_cost']}")
            
            # Get organization profile for this user
            profile = await conn.fetchrow("""
                SELECT * FROM organization_profile
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT 1
            """, user_id)
            org_profile_dict = dict(profile) if profile else None
            
            if org_profile_dict:
                logger.info(f"✓ Organization profile: Found (Name: {org_profile_dict.get('organization_name')})")
            else:
                logger.info(f"✓ Organization profile: Not found for user {user_id} - will continue with default constraints")
            
            # Get stored accounting records
            analysis_summary = await get_analysis_summary(analysis_id, user_id)
            emission_records = await get_analysis_records(analysis_id, user_id)
            
            logger.info(f"✓ Emission records found: {len(emission_records)}")
            
            if not emission_records:
                raise HTTPException(
                    status_code=404,
                    detail="No emission records found for the latest analysis."
                )
            
            # If summary is missing, generate it on the fly
            if not analysis_summary:
                logger.info("Summary not found in DB. Regenerating on-the-fly via AnalyticsAgent")
                from agents.analytics_agent import AnalyticsAgent
                analytics_agent = AnalyticsAgent()
                analysis_summary = analytics_agent.generate_analytics(emission_records)
            
            # Run Sustainability Intelligence Engine
            from agents.carbon_iq_orchestrator import CarbonIQOrchestrator
            orchestrator = CarbonIQOrchestrator()
            
            use_gemini = False
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key and gemini_key != "your_gemini_api_key_here":
                use_gemini = True
            
            logger.info(f"Running intelligence engine (Gemini: {use_gemini})...")
            result = await orchestrator.generate_insights_only(
                analysis_summary=analysis_summary,
                emission_records=emission_records,
                org_profile=org_profile_dict,
                use_gemini=use_gemini
            )
            
            if not result or not result.get('success'):
                raise HTTPException(
                    status_code=500,
                    detail=result.get('error', 'Intelligence generation failed')
                )
            
            intelligence = result['intelligence']
            
            # Save the recommendation run to NeonDB
            # Note: save_recommendation_run handles JSON serialization internally
            # Pass Python objects directly - the function will serialize them
            run_id = await save_recommendation_run(
                user_id=user_id,
                analysis_id=analysis_id,
                run_type='sustainability',
                findings=intelligence['summary'],
                recommendations=intelligence['recommendations'],
                hotspots=intelligence['workload_analysis'].get('hotspots'),
                region_opportunities=intelligence['workload_analysis'].get('region_opportunities'),
                time_opportunities=intelligence['workload_analysis'].get('time_opportunities'),
                confidence_score=None,
                metadata={
                    'intelligence_stats': intelligence['intelligence_stats'],
                    'patterns_detected': len(intelligence['patterns']),
                    'opportunities_found': len(intelligence['opportunities']),
                    'patterns': intelligence['patterns'],
                    'opportunities': intelligence['opportunities'],
                    'workload_analysis': intelligence['workload_analysis']
                }
            )
            
            response = {
                'success': True,
                'message': 'Intelligence generation complete',
                'analysis_id': analysis_id,
                'run_id': run_id,
                'profile_configured': org_profile_dict is not None
            }
            
            logger.info(f"✓ Saved recommendation run: ID={run_id}")
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
async def get_recommendations(current_user=Depends(get_current_user)):
    """
    Get latest recommendation run for authenticated user
    
    Returns the most recent recommendation_run from the database for this user
    """
    logger.info("=" * 80)
    logger.info("GET /api/intelligence/recommendations - Request received")
    logger.info("=" * 80)
    
    # Extract authenticated user ID
    user_id = current_user['id']
    logger.info(f"✓ Authenticated user: ID={user_id}, Email={current_user['email']}")
    
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
            
            # Get latest recommendation run for this user
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
                WHERE user_id = $1
                ORDER BY generated_at DESC
                LIMIT 1
            """, user_id)
            
            if not row:
                logger.info(f"✗ No recommendation runs found for user {user_id}")
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
                logger.info(f"✓ Found recommendation run: ID={row['id']} for user {user_id}")
                
                # Convert row to dict and extract intelligence data
                rec_data = dict(row)
                
                # Parse JSON fields (they're already deserialized by asyncpg for JSONB columns)
                # But we need to handle the case where they might be strings
                def safe_json_parse(value):
                    if value is None:
                        return None
                    if isinstance(value, str):
                        try:
                            return json.loads(value)
                        except:
                            return value
                    return value
                
                findings = safe_json_parse(rec_data['findings']) or {}
                recommendations = safe_json_parse(rec_data['recommendations']) or []
                hotspots = safe_json_parse(rec_data['hotspots']) or []
                region_opportunities = safe_json_parse(rec_data['region_opportunities']) or []
                time_opportunities = safe_json_parse(rec_data['time_opportunities']) or []
                metadata = safe_json_parse(rec_data['metadata']) or {}
                
                # Return structured response
                response = {
                    'id': rec_data['id'],
                    'generated_at': rec_data['generated_at'].isoformat() if rec_data['generated_at'] else None,
                    'recommendations': recommendations,
                    'patterns': metadata.get('patterns', []),
                    'opportunities': metadata.get('opportunities', []),
                    'summary': findings,
                    'workload_analysis': metadata.get('workload_analysis', {}),
                    'hotspots': hotspots,
                    'region_opportunities': region_opportunities,
                    'time_opportunities': time_opportunities,
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
async def get_recommendation_history(current_user=Depends(get_current_user)):
    """
    Get all recommendation runs for authenticated user ordered by date
    
    Returns list of past recommendation runs for this user
    """
    user_id = current_user['id']
    
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
                    jsonb_array_length(recommendations::jsonb) as recommendation_count
                FROM recommendation_runs
                WHERE user_id = $1
                ORDER BY generated_at DESC
                LIMIT 50
            """, user_id)
            
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
async def get_recommendation_by_id(recommendation_id: int, current_user=Depends(get_current_user)):
    """
    Get specific recommendation run by ID for authenticated user
    """
    user_id = current_user['id']
    
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
                WHERE id = $1 AND user_id = $2
            """, recommendation_id, user_id)
            
            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"Recommendation run {recommendation_id} not found or not owned by user"
                )
            
            rec_data = dict(row)
            
            # Parse JSON fields safely
            def safe_json_parse(value):
                if value is None:
                    return None
                if isinstance(value, str):
                    try:
                        return json.loads(value)
                    except:
                        return value
                return value
            
            findings = safe_json_parse(rec_data['findings']) or {}
            recommendations = safe_json_parse(rec_data['recommendations']) or []
            hotspots = safe_json_parse(rec_data['hotspots']) or []
            region_opportunities = safe_json_parse(rec_data['region_opportunities']) or []
            time_opportunities = safe_json_parse(rec_data['time_opportunities']) or []
            metadata = safe_json_parse(rec_data['metadata']) or {}
            
            return {
                'id': rec_data['id'],
                'generated_at': rec_data['generated_at'].isoformat() if rec_data['generated_at'] else None,
                'recommendations': recommendations,
                'patterns': metadata.get('patterns', []),
                'opportunities': metadata.get('opportunities', []),
                'summary': findings,
                'workload_analysis': metadata.get('workload_analysis', {}),
                'hotspots': hotspots,
                'region_opportunities': region_opportunities,
                'time_opportunities': time_opportunities,
                'confidence_score': rec_data['confidence_score'],
                'status': rec_data['status']
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
