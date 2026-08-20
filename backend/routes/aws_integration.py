from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import logging
import time

from services.s3_fetcher import fetch_csv_from_s3
from routes.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


class AWSFetchRequest(BaseModel):
    access_key: str
    secret_key: str
    region: str
    bucket_name: str
    file_key: Optional[str] = None


@router.post("/aws/fetch")
async def fetch_aws_data(request: AWSFetchRequest, current_user=Depends(get_current_user)):
    """
    Fetch AWS CUR CSV from S3, then run it through the full 6-agent
    orchestrator pipeline (same as /multi-agent/analyze).
    Returns rich analytics: service/region breakdown, time-series, optimization.
    
    Requires authentication.
    """
    request_start = time.time()
    user_id = current_user['id']
    
    logger.info(f"✓ Authenticated user: ID={user_id}, Email={current_user['email']}")
    logger.info(f"Fetching AWS data from bucket: {request.bucket_name}")

    # 1. Pull CSV from S3
    csv_content, error = await fetch_csv_from_s3(
        access_key=request.access_key,
        secret_key=request.secret_key,
        region=request.region,
        bucket_name=request.bucket_name,
        file_key=request.file_key,
    )

    if error:
        raise HTTPException(status_code=400, detail=error)

    # 2. Run through full multi-agent orchestrator pipeline
    try:
        from agents.orchestrator import CarbonIQOrchestrator
        orchestrator = CarbonIQOrchestrator()

        filename = request.file_key or f"s3://{request.bucket_name}/latest"
        result = await orchestrator.process_cur_data(
            csv_content,
            max_rows=10000,
            debug_skip_api=False,
        )

        duration = time.time() - request_start
        logger.info(f"S3 pipeline complete in {duration:.2f}s — success={result.get('success')}")

        # Save to NeonDB with user ownership
        if result.get("success"):
            try:
                from database import save_analysis
                analysis_id = await save_analysis(
                    filename=filename,
                    result=result,
                    user_id=user_id
                )
                result["analysis_id"] = analysis_id
                logger.info(f"✓ Saved S3 analysis to NeonDB: analysis_id={analysis_id}, user_id={user_id}")
            except Exception as db_err:
                logger.error(f"✗ DB save failed: {db_err}", exc_info=True)
                # Don't fail the whole request
                pass

        return result

    except Exception as e:
        duration = time.time() - request_start
        logger.error(f"S3 pipeline error after {duration:.2f}s: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@router.post("/aws/demo")
async def load_demo_data():
    """Load demo AWS data through the full pipeline."""
    try:
        from routes.multi_agent_analysis import load_demo_cur_data
        from agents.orchestrator import CarbonIQOrchestrator

        csv_content = load_demo_cur_data()
        orchestrator = CarbonIQOrchestrator()
        result = await orchestrator.process_cur_data(csv_content, max_rows=1000, debug_skip_api=False)
        result["is_demo"] = True
        return result
    except Exception as e:
        logger.error(f"Demo error: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading demo: {str(e)}")
