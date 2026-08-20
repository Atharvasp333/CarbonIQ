from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import google.generativeai as genai
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

SYSTEM_PROMPT = """You are CarbonIQ Assistant, an AI expert in AWS cloud carbon emissions and sustainability. 
Only answer questions related to:
- AWS cloud carbon footprint
- Cloud sustainability best practices
- AWS service optimization for emissions
- Region selection for lower carbon
- EC2, RDS, Lambda, S3 carbon impact
- Cloud cost vs emissions tradeoffs
- Green cloud computing
- Carbon-aware cloud architecture

If a question is unrelated to these topics, politely refuse and say:
"I'm designed to assist only with AWS cloud carbon emissions and sustainability topics."

Provide actionable suggestions and keep answers concise (2-3 sentences max).
Be friendly and helpful."""

CARBON_KEYWORDS = [
    'carbon', 'emission', 'co2', 'sustainability', 'aws', 'cloud', 'ec2', 'rds',
    'lambda', 's3', 'region', 'energy', 'green', 'environment', 'footprint',
    'renewable', 'cost', 'optimize', 'reduce', 'efficient', 'instance', 'server'
]

def is_carbon_related(message: str) -> bool:
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in CARBON_KEYWORDS)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        if not request.message or len(request.message.strip()) == 0:
            return ChatResponse(reply="Please ask me a question about carbon emissions or sustainability.")
        
        if not is_carbon_related(request.message):
            return ChatResponse(
                reply="I'm designed to assist only with carbon footprint, sustainability, and emission reduction topics. How can I help you with environmental matters?"
            )
        
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key or api_key == "your_gemini_api_key_here":
            return ChatResponse(
                reply="I'm currently in demo mode. For full AI responses, please configure the Gemini API key."
            )
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser question: {request.message}"
        response = model.generate_content(full_prompt)
        
        return ChatResponse(reply=response.text.strip())
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return ChatResponse(
            reply="I'm having trouble processing your request. Please try asking about carbon emissions or sustainability topics."
        )
