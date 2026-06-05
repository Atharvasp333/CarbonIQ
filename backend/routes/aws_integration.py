from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from services.s3_fetcher import fetch_csv_from_s3
from services.aws_analyzer import parse_aws_csv, load_mock_data

logger = logging.getLogger(__name__)
router = APIRouter()


class AWSFetchRequest(BaseModel):
    access_key: str
    secret_key: str
    region: str
    bucket_name: str
    file_key: Optional[str] = None


@router.post("/aws/fetch")
async def fetch_aws_data(request: AWSFetchRequest):
    """
    Fetch AWS CUR data from S3 and calculate emissions
    """
    logger.info("\n" + "="*80)
    logger.info("🚀 AWS CUR FETCH REQUEST STARTED")
    logger.info("="*80)
    logger.info(f"📍 Bucket: {request.bucket_name}")
    logger.info(f"🌍 Region: {request.region}")
    logger.info(f"📂 File Key: {request.file_key if request.file_key else '(auto-discover latest)'}")
    logger.info("="*80 + "\n")
    
    # Fetch CSV from S3
    csv_content, error = await fetch_csv_from_s3(
        access_key=request.access_key,
        secret_key=request.secret_key,
        region=request.region,
        bucket_name=request.bucket_name,
        file_key=request.file_key
    )
    
    if error:
        logger.error(f"❌ S3 FETCH FAILED: {error}")
        raise HTTPException(status_code=400, detail=error)
    
    # Parse and analyze
    try:
        logger.info("\n" + "="*80)
        logger.info("🔬 PARSING CSV AND CALCULATING EMISSIONS")
        logger.info("="*80)
        
        result = await parse_aws_csv(csv_content)
        
        logger.info(f"✅ Parsing complete!")
        logger.info(f"   📊 Total CO₂: {result.total_co2_kg:.2f} kg")
        logger.info(f"   💰 Total Cost: ${result.total_cost:.2f}")
        logger.info(f"   📈 Line Items: {len(result.line_items)}")
        logger.info(f"   🏆 Top Service: {result.top_service}")
        logger.info(f"   🌍 Top Region: {result.top_region}")
        logger.info("="*80 + "\n")
        
        # Check if result has any meaningful data
        if result.total_co2_kg == 0 and result.total_cost == 0 and len(result.line_items) == 0:
            logger.warning("⚠️  CSV parsed but contains no usage data (only tax/credit lines)")
            return {
                **result.dict(),
                "message": "No usage data found in CSV. This file contains only tax/credit lines with zero usage. Please ensure you're using a CUR file with actual AWS resource usage."
            }
        
        return result
    except Exception as e:
        logger.error(f"❌ CSV PARSING FAILED: {e}")
        logger.exception(e)
        raise HTTPException(
            status_code=400,
            detail=f"CSV format not supported: {str(e)}"
        )


@router.post("/aws/demo")
async def load_demo_data():
    """
    Load demo AWS data for testing
    """
    logger.info("Loading demo AWS data")
    
    try:
        csv_content = load_mock_data()
        result = await parse_aws_csv(csv_content)
        return result
    except Exception as e:
        logger.error(f"Error loading demo data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading demo data: {str(e)}"
        )
