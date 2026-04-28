import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import emissions, insights, whatif, chat

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


@app.get("/api/health")
async def health_check():
    climatiq_key = os.getenv("CLIMATIQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    return {
        "status": "ok",
        "keys_loaded": {
            "climatiq": bool(climatiq_key and climatiq_key != "your_climatiq_api_key_here"),
            "gemini": bool(gemini_key and gemini_key != "your_gemini_api_key_here")
        }
    }
