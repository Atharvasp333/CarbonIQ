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
    logger.info(f"Fetching AWS data from bucket: {request.bucket_name}")
    
    # Fetch CSV from S3
    csv_content, error = await fetch_csv_from_s3(
        access_key=request.access_key,
        secret_key=request.secret_key,
        region=request.region,
        bucket_name=request.bucket_name,
        file_key=request.file_key
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    # Parse and analyze
    try:
        result = await parse_aws_csv(csv_content)
        return result
    except Exception as e:
        logger.error(f"Error parsing CSV: {e}")
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
