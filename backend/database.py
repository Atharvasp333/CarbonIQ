"""
NeonDB PostgreSQL connection and table setup.
Uses asyncpg for async operations compatible with FastAPI.
"""
import os
import logging
import asyncpg
from typing import Optional

logger = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        url = os.getenv("DATABASE_URL")
        if not url:
            raise RuntimeError("DATABASE_URL not set in environment")
        _pool = await asyncpg.create_pool(url, min_size=1, max_size=5)
        logger.info("NeonDB connection pool created")
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def init_db():
    """Create all tables if they don't exist."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id          SERIAL PRIMARY KEY,
                name        TEXT NOT NULL,
                email       TEXT UNIQUE NOT NULL,
                password    TEXT NOT NULL,
                created_at  TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS aws_credentials (
                id          SERIAL PRIMARY KEY,
                user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE,
                access_key  TEXT NOT NULL,          -- Fernet-encrypted (enc:...)
                secret_key  TEXT NOT NULL,          -- Fernet-encrypted (enc:...)
                region      TEXT NOT NULL DEFAULT 'ap-south-1',
                bucket_name TEXT NOT NULL,
                file_key    TEXT,                   -- optional S3 key path
                verified    BOOLEAN DEFAULT FALSE,
                verified_at TIMESTAMPTZ,
                created_at  TIMESTAMPTZ DEFAULT NOW(),
                updated_at  TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(user_id)
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id              SERIAL PRIMARY KEY,
                filename        TEXT,
                uploaded_at     TIMESTAMPTZ DEFAULT NOW(),
                total_emissions NUMERIC(12,6),
                total_cost      NUMERIC(12,4),
                total_energy    NUMERIC(12,6),
                top_service     TEXT,
                top_region      TEXT,
                original_rows   INTEGER,
                compressed_rows INTEGER,
                api_calls       INTEGER
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS emission_records (
                id               SERIAL PRIMARY KEY,
                analysis_id      INTEGER REFERENCES analyses(id) ON DELETE CASCADE,
                service          TEXT,
                region           TEXT,
                zone             TEXT,
                usage_type       TEXT,
                record_date      DATE,
                usage_amount     NUMERIC(20,8),
                cost             NUMERIC(12,6),
                energy_kwh       NUMERIC(16,8),
                carbon_intensity NUMERIC(10,4),
                emissions_kg     NUMERIC(16,8),
                resource_id      TEXT,
                intensity_source TEXT
            );
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_emission_records_analysis
                ON emission_records(analysis_id);
            CREATE INDEX IF NOT EXISTS idx_emission_records_service
                ON emission_records(service);
            CREATE INDEX IF NOT EXISTS idx_emission_records_date
                ON emission_records(record_date);
        """)

        # ── Migrations for existing tables ──────────────────────────────────
        # Add file_key column if it doesn't exist yet (safe to run repeatedly)
        await conn.execute("""
            ALTER TABLE aws_credentials ADD COLUMN IF NOT EXISTS file_key TEXT;
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS api_call_logs (
                id               SERIAL PRIMARY KEY,
                analysis_id      INTEGER REFERENCES analyses(id) ON DELETE CASCADE,
                zone             TEXT,
                record_date      DATE,
                called_at        TIMESTAMPTZ,
                endpoint         TEXT,
                response_ms      INTEGER,
                carbon_intensity NUMERIC(10,4),
                source           TEXT,
                status           TEXT,
                error_msg        TEXT
            );
        """)

    logger.info("NeonDB tables ready")


async def save_analysis(filename: str, result: dict) -> int:
    """
    Persist a completed multi-agent analysis to NeonDB.
    Returns the new analysis id.
    """
    pool = await get_pool()
    summary = result.get("summary", {})
    pipeline = result.get("pipeline_stats", {})
    ingestion = pipeline.get("ingestion", {})
    ci = pipeline.get("carbon_intensity", {})

    async with pool.acquire() as conn:
        async with conn.transaction():
            # Insert analysis summary
            analysis_id = await conn.fetchval("""
                INSERT INTO analyses
                    (filename, total_emissions, total_cost, total_energy,
                     top_service, top_region, original_rows, compressed_rows, api_calls)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
                RETURNING id
            """,
                filename,
                float(summary.get("total_emissions_kg", 0)),
                float(summary.get("total_cost", 0)),
                float(summary.get("total_energy_kwh", 0)),
                summary.get("top_service"),
                summary.get("top_region"),
                int(ingestion.get("original_rows", 0)),
                int(ingestion.get("compressed_rows", 0)),
                int(ci.get("api_calls", 0)),
            )

            # Insert emission records
            records = result.get("all_records") or result.get("detailed_records", [])
            if records:
                rows = []
                for r in records:
                    ts = r.get("timestamp", "")
                    try:
                        from datetime import datetime
                        date = datetime.fromisoformat(
                            ts.replace("Z", "+00:00")
                        ).date()
                    except Exception:
                        date = None
                    rows.append((
                        analysis_id,
                        r.get("service"),
                        r.get("region"),
                        r.get("zone"),
                        r.get("usage_type"),
                        date,
                        float(r.get("usage_amount", 0)),
                        float(r.get("cost", 0)),
                        float(r.get("energy_kwh", 0)),
                        float(r.get("carbon_intensity", 0)),
                        float(r.get("emissions_kg", 0)),
                        r.get("resource_id", ""),
                        r.get("intensity_source", ""),
                    ))
                await conn.executemany("""
                    INSERT INTO emission_records
                        (analysis_id, service, region, zone, usage_type, record_date,
                         usage_amount, cost, energy_kwh, carbon_intensity,
                         emissions_kg, resource_id, intensity_source)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
                """, rows)

            # Insert API call logs
            call_log = ci.get("api_call_log", [])
            if call_log:
                from datetime import datetime
                log_rows = []
                for entry in call_log:
                    try:
                        called_at = datetime.fromisoformat(
                            entry.get("called_at", "").replace("Z", "+00:00")
                        )
                    except Exception:
                        called_at = None
                    try:
                        date = datetime.strptime(entry.get("date", ""), "%Y-%m-%d").date()
                    except Exception:
                        date = None
                    log_rows.append((
                        analysis_id,
                        entry.get("zone"),
                        date,
                        called_at,
                        entry.get("endpoint"),
                        entry.get("response_ms"),
                        float(entry.get("carbon_intensity", 0)),
                        entry.get("source"),
                        entry.get("status"),
                        entry.get("error"),
                    ))
                await conn.executemany("""
                    INSERT INTO api_call_logs
                        (analysis_id, zone, record_date, called_at, endpoint,
                         response_ms, carbon_intensity, source, status, error_msg)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
                """, log_rows)

    logger.info(f"Saved analysis id={analysis_id} with {len(records)} records")
    return analysis_id


async def get_analysis_history(limit: int = 20) -> list:
    """Fetch recent analyses for history view."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, filename, uploaded_at, total_emissions, total_cost,
                   total_energy, top_service, top_region, original_rows,
                   compressed_rows, api_calls
            FROM analyses
            ORDER BY uploaded_at DESC
            LIMIT $1
        """, limit)
    return [dict(r) for r in rows]


async def get_analysis_records(analysis_id: int) -> list:
    """Fetch all emission records for a given analysis."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM emission_records
            WHERE analysis_id = $1
            ORDER BY record_date, service
        """, analysis_id)
    return [dict(r) for r in rows]
