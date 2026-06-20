"""
INTEGRATION EXAMPLE: How to use the new separated architecture

This file shows how to update route handlers to use:
1. Carbon Accounting Engine (for dashboard)
2. Sustainability Intelligence Engine (for insights page)
3. Both engines together (complete pipeline)
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Optional
from ..agents.carbon_iq_orchestrator import CarbonIQOrchestrator
from ..database import (
    save_analysis, 
    save_analysis_summary,
    save_recommendation_run,
    get_analysis_summary,
    get_analysis_records,
    get_recommendation_runs
)
from ..models.schemas import (
    OrganizationProfileResponse,
    RecommendationRunResponse
)

router = APIRouter(prefix="/api/v2", tags=["CarbonIQ V2"])


# ============================================================================
# PATTERN 1: DASHBOARD (ACCOUNTING ONLY)
# ============================================================================

@router.post("/analyze/dashboard")
async def analyze_for_dashboard(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    max_rows: int = 1000
):
    """
    Upload CUR and get dashboard data (accounting only)
    
    Use case: User uploads CSV, wants to see emissions dashboard
    """
    # Read CSV
    csv_content = await file.read()
    csv_string = csv_content.decode('utf-8')
    
    # Run accounting engine only
    orchestrator = CarbonIQOrchestrator()
    result = await orchestrator.process_cur_only(
        csv_content=csv_string,
        max_rows=max_rows
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Processing failed'))
    
    # Extract results
    accounting = result['accounting']
    
    # Store to database
    analysis_id = await save_analysis(
        filename=file.filename,
        result=accounting,
        user_id=user_id
    )
    
    # Store precomputed summary
    await save_analysis_summary(
        user_id=user_id,
        analysis_id=analysis_id,
        service_breakdown=accounting['analysis_summary']['service_breakdown'],
        region_breakdown=accounting['analysis_summary']['region_breakdown'],
        daily_breakdown=accounting['analysis_summary'].get('daily_breakdown'),
        time_breakdown=accounting['analysis_summary'].get('time_series'),
        top_hotspots=accounting['analysis_summary'].get('top_hotspots'),
        metadata={
            'pipeline_stats': accounting['pipeline_stats'],
            'record_count': accounting['analysis_summary']['record_count']
        }
    )
    
    # Return dashboard data
    return {
        'success': True,
        'analysis_id': analysis_id,
        'summary': accounting['analysis_summary'],
        'emission_records': accounting['emission_records'][:100],  # First 100 for UI
        'pipeline_stats': accounting['pipeline_stats']
    }


# ============================================================================
# PATTERN 2: INSIGHTS PAGE (INTELLIGENCE ONLY)
# ============================================================================

@router.post("/insights/generate/{analysis_id}")
async def generate_insights(
    analysis_id: int,
    user_id: int = Depends(get_current_user_id),
    use_gemini: bool = False,
    force_regenerate: bool = False
):
    """
    Generate insights from existing analysis (intelligence only)
    
    Use case: User clicks "Generate Insights" button on dashboard
    """
    # Check if recent recommendations exist
    if not force_regenerate:
        existing_runs = await get_recommendation_runs(
            analysis_id=analysis_id,
            user_id=user_id,
            run_type='sustainability',
            limit=1
        )
        
        if existing_runs:
            # Return cached recommendations
            return {
                'success': True,
                'cached': True,
                'recommendations': existing_runs[0]['recommendations'],
                'summary': existing_runs[0]['findings'],
                'generated_at': existing_runs[0]['generated_at']
            }
    
    # Fetch stored accounting data from database
    analysis_summary = await get_analysis_summary(analysis_id, user_id)
    if not analysis_summary:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    emission_records = await get_analysis_records(analysis_id, user_id)
    
    # Fetch organization profile (optional)
    org_profile = await get_organization_profile(user_id)
    
    # Run intelligence engine
    orchestrator = CarbonIQOrchestrator()
    result = await orchestrator.generate_insights_only(
        analysis_summary=analysis_summary,
        emission_records=emission_records,
        org_profile=org_profile,
        use_gemini=use_gemini
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Intelligence generation failed'))
    
    # Extract results
    intelligence = result['intelligence']
    
    # Store recommendations to database
    await save_recommendation_run(
        user_id=user_id,
        analysis_id=analysis_id,
        run_type='sustainability',
        findings=intelligence['summary'],
        recommendations=intelligence['recommendations'],
        hotspots=intelligence['workload_analysis'].get('hotspots'),
        region_opportunities=intelligence['workload_analysis'].get('region_opportunities'),
        time_opportunities=intelligence['workload_analysis'].get('time_opportunities'),
        confidence_score=None,  # Can calculate average confidence
        metadata={
            'intelligence_stats': intelligence['intelligence_stats'],
            'patterns_detected': len(intelligence['patterns']),
            'opportunities_found': len(intelligence['opportunities'])
        }
    )
    
    # Return insights
    return {
        'success': True,
        'cached': False,
        'recommendations': intelligence['recommendations'],
        'summary': intelligence['summary'],
        'patterns': intelligence['patterns'],
        'opportunities': intelligence['opportunities'],
        'stats': intelligence['intelligence_stats']
    }


@router.get("/insights/{analysis_id}")
async def get_insights(
    analysis_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """
    Get cached insights for an analysis
    
    Use case: User navigates to insights page, wants to see existing recommendations
    """
    # Get latest recommendation run
    runs = await get_recommendation_runs(
        analysis_id=analysis_id,
        user_id=user_id,
        run_type='sustainability',
        limit=1
    )
    
    if not runs:
        return {
            'success': True,
            'has_insights': False,
            'message': 'No insights generated yet. Click "Generate Insights" to create recommendations.'
        }
    
    latest_run = runs[0]
    
    return {
        'success': True,
        'has_insights': True,
        'recommendations': latest_run['recommendations'],
        'summary': latest_run['findings'],
        'generated_at': latest_run['generated_at'],
        'metadata': latest_run['metadata']
    }


# ============================================================================
# PATTERN 3: COMPLETE PIPELINE (BOTH ENGINES)
# ============================================================================

@router.post("/analyze/complete")
async def complete_analysis(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    max_rows: int = 1000,
    use_gemini: bool = False
):
    """
    Run complete pipeline: accounting + intelligence
    
    Use case: Power user wants full analysis in one request
    """
    # Read CSV
    csv_content = await file.read()
    csv_string = csv_content.decode('utf-8')
    
    # Fetch organization profile
    org_profile = await get_organization_profile(user_id)
    
    # Run both engines
    orchestrator = CarbonIQOrchestrator()
    result = await orchestrator.process_cur_with_insights(
        csv_content=csv_string,
        max_rows=max_rows,
        org_profile=org_profile,
        use_gemini=use_gemini
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Processing failed'))
    
    # Store accounting results
    accounting = result['accounting']
    analysis_id = await save_analysis(
        filename=file.filename,
        result=accounting,
        user_id=user_id
    )
    
    await save_analysis_summary(
        user_id=user_id,
        analysis_id=analysis_id,
        service_breakdown=accounting['analysis_summary']['service_breakdown'],
        region_breakdown=accounting['analysis_summary']['region_breakdown'],
        daily_breakdown=accounting['analysis_summary'].get('daily_breakdown'),
        time_breakdown=accounting['analysis_summary'].get('time_series'),
        top_hotspots=accounting['analysis_summary'].get('top_hotspots'),
        metadata={'pipeline_stats': accounting['pipeline_stats']}
    )
    
    # Store intelligence results
    intelligence = result['intelligence']
    await save_recommendation_run(
        user_id=user_id,
        analysis_id=analysis_id,
        run_type='sustainability',
        findings=intelligence['summary'],
        recommendations=intelligence['recommendations'],
        hotspots=intelligence['workload_analysis'].get('hotspots'),
        region_opportunities=intelligence['workload_analysis'].get('region_opportunities'),
        time_opportunities=intelligence['workload_analysis'].get('time_opportunities'),
        metadata={'intelligence_stats': intelligence['intelligence_stats']}
    )
    
    # Return complete results
    return {
        'success': True,
        'analysis_id': analysis_id,
        'accounting': {
            'summary': accounting['analysis_summary'],
            'stats': accounting['pipeline_stats']
        },
        'intelligence': {
            'recommendations': intelligence['recommendations'],
            'summary': intelligence['summary'],
            'stats': intelligence['intelligence_stats']
        },
        'combined_summary': result['summary']
    }


# ============================================================================
# HELPER ENDPOINTS
# ============================================================================

@router.get("/status")
async def get_system_status():
    """Get system status"""
    orchestrator = CarbonIQOrchestrator()
    return orchestrator.get_status()


@router.get("/analyses/{analysis_id}/summary")
async def get_analysis_summary_endpoint(
    analysis_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """Get precomputed analysis summary"""
    summary = await get_analysis_summary(analysis_id, user_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Analysis summary not found")
    return summary


# ============================================================================
# ORGANIZATION PROFILE ENDPOINTS
# ============================================================================

async def get_organization_profile(user_id: int) -> Optional[dict]:
    """Fetch organization profile for user"""
    # Implement database query
    # Returns dict or None
    pass


async def get_current_user_id() -> int:
    """Get current authenticated user ID"""
    # Implement auth logic
    pass


# ============================================================================
# USAGE NOTES
# ============================================================================

"""
FRONTEND INTEGRATION:

Dashboard Page:
--------------
// Upload CSV and get dashboard
const uploadCUR = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await fetch('/api/v2/analyze/dashboard', {
    method: 'POST',
    body: formData,
    headers: { 'Authorization': `Bearer ${token}` }
  })
  
  const data = await response.json()
  
  // Display dashboard
  displayDashboard(data.summary, data.emission_records)
  
  // Store analysis_id for later
  setAnalysisId(data.analysis_id)
}

Insights Page:
-------------
// Generate insights from existing analysis
const generateInsights = async (analysisId) => {
  const response = await fetch(`/api/v2/insights/generate/${analysisId}`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  })
  
  const data = await response.json()
  
  if (data.cached) {
    console.log('Using cached recommendations')
  }
  
  // Display recommendations
  displayRecommendations(data.recommendations)
}

// Get existing insights
const getInsights = async (analysisId) => {
  const response = await fetch(`/api/v2/insights/${analysisId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  
  const data = await response.json()
  
  if (!data.has_insights) {
    // Show "Generate Insights" button
    showGenerateButton()
  } else {
    // Display existing recommendations
    displayRecommendations(data.recommendations)
  }
}

BENEFITS:
---------
1. Dashboard loads fast (only accounting, no AI)
2. Insights can be regenerated without re-uploading CUR
3. Insights are cached for instant retrieval
4. Organization profile affects recommendations
5. Clear separation of concerns
"""
