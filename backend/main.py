import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import emissions, insights, whatif, chat, regional_test, electricity_test, aws_integration, time_based_analysis, multi_agent_analysis, service_analytics

load_dotenv()

app = FastAPI(title="CarbonIQ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(emissions.router, prefix="/api")
app.include_router(insights.router, prefix="/api")
app.include_router(whatif.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(regional_test.router, prefix="/api")
app.include_router(electricity_test.router, prefix="/api")
app.include_router(aws_integration.router, prefix="/api")
app.include_router(time_based_analysis.router, prefix="/api")
app.include_router(multi_agent_analysis.router, prefix="/api")
app.include_router(service_analytics.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    climatiq_key = os.getenv("CLIMATIQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    electricity_maps_key = os.getenv("ELECTRICITY_MAPS_API_KEY")
    
    return {
        "status": "ok",
        "keys_loaded": {
            "climatiq": bool(climatiq_key and climatiq_key != "your_climatiq_api_key_here"),
            "gemini": bool(gemini_key and gemini_key != "your_gemini_api_key_here"),
            "electricity_maps": bool(electricity_maps_key)
        }
    }
