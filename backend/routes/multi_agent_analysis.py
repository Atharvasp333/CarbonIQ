"""
Multi-Agent CUR Analysis API Routes
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import logging
import os

from agents.orchestrator import CarbonIQOrchestrator

router = APIRouter()
logger = logging.getLogger(__name__)


class DemoRequest(BaseModel):
    load_demo: bool = True


def load_demo_cur_data():
    """
    Load demo CUR data from actual CSV files in the project
    
    Priority order:
    1. CUR_report-00001.csv (real AWS CUR data from project root)
    2. backend/data/mock_csv.csv (smaller sample data)
    3. Minimal fallback data (if both files fail)
    """
    import os
    
    # Get the directory where this file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Option 1: Try to load the real CUR report from project root
    cur_path = os.path.normpath(os.path.join(current_dir, '..', '..', 'CUR_report-00001.csv'))
    
    if os.path.exists(cur_path):
        logger.info(f"Loading real CUR data from: {cur_path}")
        try:
            with open(cur_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()
            logger.info(f"✓ Successfully loaded CUR file ({len(csv_content)} bytes, ~{csv_content.count(chr(10))} lines)")
            return csv_content
        except Exception as e:
            logger.error(f"Error reading CUR file: {str(e)}")
    else:
        logger.warning(f"CUR file not found at: {cur_path}")
    
    # Option 2: Try to load mock CSV from backend/data
    mock_path = os.path.normpath(os.path.join(current_dir, '..', 'data', 'mock_csv.csv'))
    
    if os.path.exists(mock_path):
        logger.info(f"Loading mock CUR data from: {mock_path}")
        try:
            with open(mock_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()
            logger.info(f"✓ Successfully loaded mock CSV ({len(csv_content)} bytes)")
            return csv_content
        except Exception as e:
            logger.error(f"Error reading mock CSV: {str(e)}")
    else:
        logger.warning(f"Mock CSV not found at: {mock_path}")
    
    # Option 3: Use minimal fallback data
    logger.warning("Using minimal fallback demo data")
    return _get_fallback_demo_data()


def _get_fallback_demo_data():
    """Minimal fallback demo data in case all CSV files fail to load"""
    logger.info("Generating minimal fallback demo data")
    return """identity/LineItemId,bill/BillingPeriodStartDate,lineItem/UsageStartDate,lineItem/UsageEndDate,product/ProductName,product/region,lineItem/UsageType,lineItem/UsageAmount,product/instanceType,lineItem/ResourceId,lineItem/UnblendedCost,product/location,product/productFamily,lineItem/Operation
1,2026-05-01,2026-05-15T14:00:00Z,2026-05-15T15:00:00Z,Amazon Elastic Compute Cloud,ap-south-1,BoxUsage:m5.large,24,m5.large,i-mumbai-001,12.50,Asia Pacific (Mumbai),Compute Instance,RunInstances
2,2026-05-01,2026-05-18T10:00:00Z,2026-05-18T11:00:00Z,Amazon Elastic Compute Cloud,us-west-2,BoxUsage:t3.medium,48,t3.medium,i-oregon-001,8.75,US West (Oregon),Compute Instance,RunInstances
3,2026-05-01,2026-05-10T08:00:00Z,2026-05-10T09:00:00Z,Amazon Relational Database Service,us-east-1,InstanceUsage:db.t3.small,24,db.t3.small,db-virginia-001,15.20,US East (N. Virginia),Database Instance,CreateDBInstance
4,2026-05-01,2026-05-20T12:00:00Z,2026-05-20T13:00:00Z,Amazon Simple Storage Service,us-east-1,TimedStorage-ByteHrs,1500000,,,2.30,US East (N. Virginia),Storage,
5,2026-05-01,2026-05-22T16:00:00Z,2026-05-22T17:00:00Z,AWS Lambda,us-west-2,Lambda-GB-Second,50000,,,0.85,US West (Oregon),Serverless,Invoke"""


@router.post("/multi-agent/analyze")
async def analyze_cur_multiagent(file: UploadFile = File(...)):
    """
    Analyze AWS CUR using multi-agent architecture
    
    DEBUG MODE: Processes ONLY first 1000 rows, SKIPS API calls for fast testing
    """
    import time
    request_start = time.time()
    
    logger.info("="*70)
    logger.info("[1] REQUEST RECEIVED - /multi-agent/analyze")
    logger.info("="*70)
    
    try:
        # Read CSV content
        logger.info("[2] CSV LOADED - Reading file content")
        csv_content = (await file.read()).decode('utf-8')
        
        logger.info(f"File: {file.filename}")
        logger.info(f"Size: {len(csv_content):,} bytes")
        
        # Initialize orchestrator
        orchestrator = CarbonIQOrchestrator()
        
        # Process through pipeline (HARD LIMIT: 1000 rows, TRY REAL API)
        logger.info("Starting pipeline with max_rows=1000, fast API timeout mode")
        result = await orchestrator.process_cur_data(
            csv_content, 
            max_rows=1000,  # HARD LIMIT for debugging
            debug_skip_api=False  # TRY REAL API with fast timeout
        )
        
        request_duration = time.time() - request_start
        logger.info(f"[10] RESPONSE SENT - Total time: {request_duration:.2f}s")
        
        return result
        
    except Exception as e:
        request_duration = time.time() - request_start
        logger.error(f"Multi-agent analysis failed after {request_duration:.2f}s: {str(e)}", exc_info=True)
        
        # ALWAYS return a response, never leave hanging
        return {
            'success': False,
            'message': f'Analysis failed: {str(e)}',
            'error_details': {
                'error_type': type(e).__name__,
                'duration': request_duration
            },
            'summary': {
                'total_emissions_kg': 0,
                'total_cost': 0,
                'total_energy_kwh': 0,
                'top_service': 'Error',
                'top_region': 'Error',
            },
            'analytics': {},
            'optimization': {
                'opportunities': [],
                'reduction_estimates': {
                    'total_potential_reduction_kg': 0,
                    'total_potential_cost_savings': 0,
                    'percentage_reduction': 0
                }
            },
            'detailed_records': []
        }


@router.post("/multi-agent/analyze-demo")
async def analyze_demo_multiagent(request: DemoRequest):
    """
    Analyze demo CUR data using multi-agent architecture
    
    DEBUG MODE: Processes ONLY first 1000 rows, SKIPS API calls for fast testing
    """
    import time
    request_start = time.time()
    
    logger.info("="*70)
    logger.info("[1] REQUEST RECEIVED - /multi-agent/analyze-demo")
    logger.info("="*70)
    
    try:
        # Load demo data
        logger.info("[2] CSV LOADED - Loading demo data")
        csv_content = load_demo_cur_data()
        
        logger.info(f"Demo CSV size: {len(csv_content):,} bytes")
        logger.info(f"Demo CSV rows: ~{csv_content.count(chr(10)):,}")
        
        # Initialize orchestrator
        orchestrator = CarbonIQOrchestrator()
        
        # Process through pipeline (HARD LIMIT: 1000 rows, TRY REAL API)
        logger.info("Starting pipeline with max_rows=1000, fast API timeout mode")
        result = await orchestrator.process_cur_data(
            csv_content,
            max_rows=1000,  # HARD LIMIT for debugging
            debug_skip_api=False  # TRY REAL API with fast timeout
        )
        
        # Add demo flag
        result['is_demo'] = True
        
        request_duration = time.time() - request_start
        logger.info(f"[10] RESPONSE SENT - Total time: {request_duration:.2f}s")
        
        return result
        
    except Exception as e:
        request_duration = time.time() - request_start
        logger.error(f"Demo analysis failed after {request_duration:.2f}s: {str(e)}", exc_info=True)
        
        # ALWAYS return a response, never leave hanging
        return {
            'success': False,
            'message': f'Demo analysis failed: {str(e)}',
            'is_demo': True,
            'error_details': {
                'error_type': type(e).__name__,
                'duration': request_duration
            },
            'summary': {
                'total_emissions_kg': 0,
                'total_cost': 0,
                'total_energy_kwh': 0,
                'top_service': 'Error',
                'top_region': 'Error',
            },
            'analytics': {},
            'optimization': {
                'opportunities': [],
                'reduction_estimates': {
                    'total_potential_reduction_kg': 0,
                    'total_potential_cost_savings': 0,
                    'percentage_reduction': 0
                }
            },
            'detailed_records': []
        }


@router.get("/multi-agent/status")
async def get_multiagent_status():
    """
    Get status of multi-agent system
    
    Returns agent health, cache stats, supported regions, etc.
    """
    try:
        orchestrator = CarbonIQOrchestrator()
        status = orchestrator.get_pipeline_status()
        
        return {
            'status': 'operational',
            'pipeline': status,
            'version': '1.0.0'
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
