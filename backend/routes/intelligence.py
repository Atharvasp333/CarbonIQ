"""
Intelligence Engine API Routes
Handles sustainability intelligence generation and recommendations
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
import logging
import os
from datetime import datetime

from database import get_pool, save_recommendation_run
from models.schemas import RecommendationRunResponse
from routes.api_keys import get_current_user_or_api_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])


@router.post("/generate-insights")
async def generate_insights(
    current_user: Optional[dict] = Depends(get_current_user_or_api_key)
):
    """
    Generate sustainability insights from stored analysis data
    
    This endpoint:
    1. Loads latest analysis from database (table: analyses)
    2. Loads emission_records from database for that analysis
    3. Loads organization_profile
    4. Runs Explainable Intelligence Engine pipeline
    5. Stores results in recommendation_runs table
    6. Returns generated recommendations
    """
    logger.info("=" * 80)
    logger.info("POST /api/intelligence/generate-insights - Request received")
    logger.info("=" * 80)
    
    try:
        pool = await get_pool()
        if pool is None:
            return {
                'success': False,
                'message': 'Database pool not available',
                'analysis_id': None,
                'profile_configured': False
            }
        logger.info("✓ Database pool acquired")
        
        async with pool.acquire() as conn:
            # Check if analyses table exists
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'analyses'
                )
            """)
            
            if not table_exists:
                logger.warning("✗ Table 'analyses' does not exist")
                return {
                    'success': False,
                    'message': 'Database tables not initialized. Please run migrations.',
                    'analysis_id': None,
                    'profile_configured': False
                }
            
            user_id = current_user.get('id') if current_user else None
            
            # Get latest analysis (for user if authenticated, else latest overall)
            if user_id:
                analysis = await conn.fetchrow("""
                    SELECT id, user_id, total_emissions, total_cost, total_energy, top_service, top_region
                    FROM analyses
                    WHERE user_id = $1
                    ORDER BY created_at DESC
                    LIMIT 1
                """, user_id)
            else:
                analysis = None
                
            if not analysis:
                analysis = await conn.fetchrow("""
                    SELECT id, user_id, total_emissions, total_cost, total_energy, top_service, top_region
                    FROM analyses
                    ORDER BY created_at DESC
                    LIMIT 1
                """)
            
            if not analysis:
                logger.warning("✗ No analysis data found in database")
                raise HTTPException(
                    status_code=404, 
                    detail="No analysis data found. Please upload or analyze CUR data first."
                )
            
            analysis_id = analysis['id']
            owner_id = analysis['user_id'] or (user_id if user_id else 1)
            logger.info(f"✓ Found analysis: ID={analysis_id} for user_id={owner_id}")
            
            # Get organization profile
            profile_row = None
            if user_id:
                profile_row = await conn.fetchrow("""
                    SELECT * FROM organization_profile
                    WHERE user_id = $1
                    ORDER BY created_at DESC
                    LIMIT 1
                """, user_id)
            if not profile_row:
                profile_row = await conn.fetchrow("""
                    SELECT * FROM organization_profile
                    ORDER BY created_at DESC
                    LIMIT 1
                """)
            
            org_profile = dict(profile_row) if profile_row else None
            
            # Fetch emission records for this analysis
            rec_rows = await conn.fetch("""
                SELECT 
                    service, region, zone, usage_type, usage_amount, 
                    cost, energy_kwh, carbon_intensity, emissions_kg, intensity_source
                FROM emission_records
                WHERE analysis_id = $1
            """, analysis_id)
            
            emission_records = [dict(r) for r in rec_rows]
            
            # If no emission records attached to analysis, generate synthetic/fallback set from demo data
            if not emission_records:
                from routes.multi_agent_analysis import load_demo_cur_data
                from agents.accounting.csv_agent import CURIngestionAgent
                from agents.accounting.region_mapping_agent import RegionMappingAgent
                from agents.accounting.carbon_intensity_agent import CarbonIntensityAgent
                from agents.accounting.emission_calculation_agent import EmissionCalculationAgent
                
                demo_csv = load_demo_cur_data()
                ing = CURIngestionAgent().process_csv(demo_csv, max_rows=500)
                reg = RegionMappingAgent().map_batch(ing)
                ci_records, _ = await CarbonIntensityAgent().fetch_batch_intensity(reg, fast_timeout=True)
                workloads = []
                for r in ci_records:
                    workloads.append({
                        'service': r['service'],
                        'region': r['region'],
                        'zone': r['zone'],
                        'usage_amount': r['usage_amount'],
                        'carbon_intensity': r['carbon_intensity'],
                        'usage_type': r['usage_type'],
                        'operation': r['operation'],
                        'timestamp': r['start_time'],
                        'cost': r['cost'],
                        'resource_id': r.get('resource_id', '')
                    })
                emission_records = EmissionCalculationAgent().calculate_batch(workloads)
            
            # Build analytics summary
            from agents.analytics_agent import AnalyticsAgent
            analytics = AnalyticsAgent().generate_analytics(emission_records)
            
            # Run Explainable Intelligence Orchestrator
            from agents.explainable_intelligence_orchestrator import ExplainableIntelligenceOrchestrator
            use_gemini = bool(os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY") != "your_gemini_api_key_here")
            intel_orchestrator = ExplainableIntelligenceOrchestrator()
            intel_result = await intel_orchestrator.generate_intelligence(
                emission_records=emission_records,
                analytics=analytics,
                org_profile=org_profile,
                use_ai=use_gemini
            )
            
            recommendations = intel_result.get('recommendations', [])
            findings = intel_result.get('summary', {})
            insights_list = intel_result.get('insights', [])
            opportunities = intel_result.get('opportunities', [])
            
            # Save to recommendation_runs table
            run_id = await save_recommendation_run(
                user_id=owner_id,
                analysis_id=analysis_id,
                run_type='sustainability',
                findings=findings,
                recommendations=recommendations,
                hotspots=intel_result.get('workload_analysis', {}).get('hotspots', []),
                region_opportunities=opportunities,
                time_opportunities=[],
                confidence_score=0.90,
                metadata={
                    'patterns': insights_list,
                    'opportunities': opportunities,
                    'workload_analysis': intel_result.get('workload_analysis', {})
                }
            )
            
            response = {
                'success': True,
                'message': 'Intelligence generated successfully',
                'run_id': run_id,
                'analysis_id': analysis_id,
                'generated_at': datetime.utcnow().isoformat(),
                'recommendations': recommendations,
                'patterns': insights_list,
                'opportunities': opportunities,
                'summary': findings,
                'workload_analysis': intel_result.get('workload_analysis', {}),
                'profile_configured': org_profile is not None
            }
            
            logger.info(f"✓ Response: Generated {len(recommendations)} recommendations (run_id={run_id})")
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
async def get_recommendations(
    current_user: Optional[dict] = Depends(get_current_user_or_api_key)
):
    """
    Get latest recommendation run
    Returns the most recent recommendation_run from the database.
    Supports authenticated users with fallback to latest run for demo mode.
    """
    user_id = current_user.get('id') if current_user else None
    logger.info(f"GET /api/intelligence/recommendations - user_id={user_id}")
    
    try:
        pool = await get_pool()
        if pool is None:
            raise HTTPException(status_code=500, detail="Database pool not available")
        
        async with pool.acquire() as conn:
            # Check if recommendation_runs table exists
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'recommendation_runs'
                )
            """)
            
            if not table_exists:
                logger.warning("✗ Table 'recommendation_runs' does not exist")
                return {
                    'id': None,
                    'generated_at': None,
                    'recommendations': [],
                    'patterns': [],
                    'opportunities': [],
                    'summary': {},
                    'status': 'no_tables'
                }
            
            # 1. Fetch latest recommendation run for this user if authenticated
            row = None
            if user_id:
                row = await conn.fetchrow("""
                    SELECT 
                        id, user_id, analysis_id, run_type, generated_at,
                        findings, recommendations, hotspots, region_opportunities,
                        time_opportunities, confidence_score, metadata, status
                    FROM recommendation_runs
                    WHERE user_id = $1
                    ORDER BY generated_at DESC
                    LIMIT 1
                """, user_id)
            
            # 2. Fall back to latest recommendation run overall
            if not row:
                row = await conn.fetchrow("""
                    SELECT 
                        id, user_id, analysis_id, run_type, generated_at,
                        findings, recommendations, hotspots, region_opportunities,
                        time_opportunities, confidence_score, metadata, status
                    FROM recommendation_runs
                    ORDER BY generated_at DESC
                    LIMIT 1
                """)
            
            if not row:
                # 3. Check if there is an analysis in analyses table to auto-generate
                analysis_exists = await conn.fetchval("""
                    SELECT id FROM analyses ORDER BY created_at DESC LIMIT 1
                """)
                if analysis_exists:
                    logger.info("Auto-triggering generate_insights since analysis exists but no recommendation run yet")
                    return await generate_insights(current_user=current_user)
                
                # Return empty structure gracefully
                return {
                    'id': None,
                    'generated_at': None,
                    'recommendations': [],
                    'patterns': [],
                    'opportunities': [],
                    'summary': {
                        'total_recommendations': 0,
                        'total_potential_reduction_kg': 0,
                        'total_potential_reduction_pct': 0,
                        'high_confidence_count': 0,
                        'top_category': 'None'
                    },
                    'workload_analysis': {},
                    'hotspots': [],
                    'region_opportunities': [],
                    'time_opportunities': [],
                    'confidence_score': None,
                    'status': 'no_data'
                }
            
            # Format row
            rec_data = dict(row)
            metadata = rec_data['metadata'] if isinstance(rec_data['metadata'], dict) else {}
            findings = rec_data['findings'] if isinstance(rec_data['findings'], dict) else {}
            recommendations = rec_data['recommendations'] if isinstance(rec_data['recommendations'], list) else []
            hotspots = rec_data['hotspots'] if isinstance(rec_data['hotspots'], list) else []
            region_opps = rec_data['region_opportunities'] if isinstance(rec_data['region_opportunities'], list) else []
            time_opps = rec_data['time_opportunities'] if isinstance(rec_data['time_opportunities'], list) else []
            
            response = {
                'id': rec_data['id'],
                'generated_at': rec_data['generated_at'].isoformat() if rec_data['generated_at'] else None,
                'recommendations': recommendations,
                'patterns': metadata.get('patterns', []),
                'opportunities': metadata.get('opportunities', []),
                'summary': findings,
                'workload_analysis': metadata.get('workload_analysis', {}),
                'hotspots': hotspots,
                'region_opportunities': region_opps,
                'time_opportunities': time_opps,
                'confidence_score': rec_data['confidence_score'],
                'status': rec_data['status']
            }
            return response
                    'workload_analysis': {},
                    'hotspots': [],
                    'region_opportunities': [],
                    'time_opportunities': [],
                    'confidence_score': None,
                    'status': 'no_data'
                }
            else:
                print(f"Step 8: Found recommendation run ID={row['id']}")
                logger.info(f"✓ Found recommendation run: ID={row['id']}")
                
                # Convert row to dict and extract intelligence data
                rec_data = dict(row)
                
                # Parse JSONB fields (they come as dicts from asyncpg, but check just in case)
                metadata = rec_data['metadata'] if isinstance(rec_data['metadata'], dict) else {}
                findings = rec_data['findings'] if isinstance(rec_data['findings'], dict) else {}
                recommendations = rec_data['recommendations'] if isinstance(rec_data['recommendations'], list) else []
                hotspots = rec_data['hotspots'] if isinstance(rec_data['hotspots'], list) else []
                region_opps = rec_data['region_opportunities'] if isinstance(rec_data['region_opportunities'], list) else []
                time_opps = rec_data['time_opportunities'] if isinstance(rec_data['time_opportunities'], list) else []
                
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
                    'region_opportunities': region_opps,
                    'time_opportunities': time_opps,
                    'confidence_score': rec_data['confidence_score'],
                    'status': rec_data['status']
                }
            
            rec_list = response.get('recommendations') or []
            print(f"Step 9: Returning {len(rec_list)} recommendations")
            print("=" * 80)
            logger.info(f"✓ Returning {len(rec_list)} recommendations")
            logger.info("=" * 80)
            return response
            
    except HTTPException as he:
        print(f"HTTP Exception: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        print("=" * 80)
        print(f"FATAL ERROR in get_recommendations: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        print("=" * 80)
        logger.error("=" * 80)
        logger.error(f"✗ ERROR in get_recommendations: {e}", exc_info=True)
        logger.error("=" * 80)
        raise HTTPException(status_code=500, detail=f"Intelligence error: {str(e)}")


@router.get("/recommendations/history")
async def get_recommendation_history():
    """
    Get all recommendation runs ordered by date
    
    Returns list of past recommendation runs
    """
    try:
        pool = await get_pool()
        if pool is None:
            raise HTTPException(status_code=500, detail="Database pool not available")
        
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
        if pool is None:
            raise HTTPException(status_code=500, detail="Database pool not available")

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
