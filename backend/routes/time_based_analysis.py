from fastapi import APIRouter, HTTPException, UploadFile, File
import logging

from services.time_based_analyzer import analyze_csv_with_timestamps, generate_demo_csv

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/time-based/upload")
async def upload_csv_for_time_based_analysis(file: UploadFile = File(...)):
    """
    Upload CSV file and analyze with time-based carbon intensity.
    
    This endpoint processes AWS-style CSV data and calculates emissions
    using historical carbon intensity from Electricity Maps API.
    """
    logger.info(f"Received file upload: {file.filename}")
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        logger.info(f"File size: {len(csv_content)} bytes")
        
        # Analyze with time-based logic
        result = await analyze_csv_with_timestamps(csv_content)
        
        return result
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File encoding error. Please ensure the file is UTF-8 encoded."
        )
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


@router.post("/time-based/demo")
async def load_demo_data_for_time_based_analysis():
    """
    Load demo data and analyze with time-based carbon intensity.
    
    This endpoint uses pre-configured demo data with timestamps
    to demonstrate the time-based emission calculation feature.
    """
    logger.info("Loading demo data for time-based analysis")
    
    try:
        # Generate demo CSV
        csv_content = generate_demo_csv()
        
        # Analyze with time-based logic
        result = await analyze_csv_with_timestamps(csv_content)
        
        return result
        
    except Exception as e:
        logger.error(f"Error loading demo data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading demo data: {str(e)}"
        )
