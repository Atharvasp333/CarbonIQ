from fastapi import APIRouter
from models.schemas import AWSInsightRequest, AWSInsightResponse
from services.gemini import get_aws_insights

router = APIRouter()


@router.post("/insights", response_model=AWSInsightResponse)
async def get_ai_insights(request: AWSInsightRequest):
    return await get_aws_insights(request)
