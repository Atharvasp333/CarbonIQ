from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import AWSAnalysisResponse
from services.aws_analyzer import parse_aws_csv, load_mock_data

router = APIRouter()


@router.post("/upload-csv", response_model=AWSAnalysisResponse)
async def upload_aws_csv(file: UploadFile = File(...)):
    """Upload and analyze AWS billing CSV"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        content = await file.read()
        csv_text = content.decode('utf-8')
        return await parse_aws_csv(csv_text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")


@router.get("/mock-data", response_model=AWSAnalysisResponse)
async def get_mock_data():
    """Load mock AWS billing data for demo"""
    mock_csv = load_mock_data()
    return await parse_aws_csv(mock_csv)
