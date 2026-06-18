import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from database import init_db, close_pool
from routes import (
    emissions, insights, whatif, chat, regional_test,
    electricity_test, aws_integration, aws_credentials, time_based_analysis,
    multi_agent_analysis, service_analytics, auth
)

import logging
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await init_db()
    except Exception as e:
        logging.warning(f"DB init failed (continuing without DB): {e}")
    yield
    # Shutdown
    await close_pool()


app = FastAPI(title="CarbonIQ API", lifespan=lifespan)

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
app.include_router(aws_credentials.router, prefix="/api")
app.include_router(time_based_analysis.router, prefix="/api")
app.include_router(multi_agent_analysis.router, prefix="/api")
app.include_router(service_analytics.router, prefix="/api")
app.include_router(auth.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    climatiq_key = os.getenv("CLIMATIQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    electricity_maps_key = os.getenv("ELECTRICITY_MAPS_API_KEY")
    db_url = os.getenv("DATABASE_URL")

    db_ok = False
    if db_url:
        try:
            from database import get_pool
            pool = await get_pool()
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            db_ok = True
        except Exception:
            db_ok = False

    return {
        "status": "ok",
        "keys_loaded": {
            "climatiq": bool(climatiq_key and climatiq_key != "your_climatiq_api_key_here"),
            "gemini": bool(gemini_key and gemini_key != "your_gemini_api_key_here"),
            "electricity_maps": bool(electricity_maps_key),
            "database": db_ok,
        }
    }
