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

        # Organization Profile Table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS organization_profile (
                id                      SERIAL PRIMARY KEY,
                user_id                 INTEGER REFERENCES users(id) ON DELETE CASCADE,
                organization_name       TEXT NOT NULL,
                primary_user_region     TEXT NOT NULL,
                workload_type           TEXT NOT NULL,
                latency_sensitivity     TEXT NOT NULL,
                migration_flexibility   TEXT NOT NULL,
                optimization_priority   TEXT NOT NULL,
                created_at              TIMESTAMPTZ DEFAULT NOW(),
                updated_at              TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(user_id)
            );
        """)

        # Analysis Summary Table (precomputed for fast dashboard loading)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_summary (
                id                  SERIAL PRIMARY KEY,
                user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                analysis_id         INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
                service_breakdown   JSONB NOT NULL,
                region_breakdown    JSONB NOT NULL,
                daily_breakdown     JSONB,
                time_breakdown      JSONB,
                top_hotspots        JSONB,
                metadata            JSONB,
                created_at          TIMESTAMPTZ DEFAULT NOW(),
                updated_at          TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(analysis_id)
            );
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_analysis_summary_user ON analysis_summary(user_id);
            CREATE INDEX IF NOT EXISTS idx_analysis_summary_analysis ON analysis_summary(analysis_id);
        """)

        # Recommendation Runs Table (stores intelligence engine outputs)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS recommendation_runs (
                id                      SERIAL PRIMARY KEY,
                user_id                 INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                analysis_id             INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
                run_type                TEXT NOT NULL,
                generated_at            TIMESTAMPTZ DEFAULT NOW(),
                findings                JSONB NOT NULL,
                recommendations         JSONB NOT NULL,
                hotspots                JSONB,
                region_opportunities    JSONB,
                time_opportunities      JSONB,
                confidence_score        NUMERIC(3,2),
                metadata                JSONB,
                status                  TEXT DEFAULT 'completed'
            );
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_recommendation_runs_user ON recommendation_runs(user_id);
            CREATE INDEX IF NOT EXISTS idx_recommendation_runs_analysis ON recommendation_runs(analysis_id);
            CREATE INDEX IF NOT EXISTS idx_recommendation_runs_type ON recommendation_runs(run_type);
            CREATE INDEX IF NOT EXISTS idx_recommendation_runs_generated ON recommendation_runs(generated_at DESC);
        """)

        # User Insights Table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_insights (
                id                  SERIAL PRIMARY KEY,
                user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                insight_type        TEXT NOT NULL,
                time_period         TEXT,
                period_start        DATE,
                period_end          DATE,
                total_emissions_kg  NUMERIC(12,6),
                total_cost          NUMERIC(12,4),
                total_energy_kwh    NUMERIC(12,6),
                analysis_count      INTEGER,
                top_services        JSONB,
                top_regions         JSONB,
                trends              JSONB,
                alerts              JSONB,
                created_at          TIMESTAMPTZ DEFAULT NOW(),
                updated_at          TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_insights_user ON user_insights(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_insights_type ON user_insights(insight_type);
            CREATE INDEX IF NOT EXISTS idx_user_insights_period ON user_insights(period_start, period_end);
        """)

        # Audit Log Table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id              SERIAL PRIMARY KEY,
                user_id         INTEGER REFERENCES users(id) ON DELETE SET NULL,
                action          TEXT NOT NULL,
                entity_type     TEXT NOT NULL,
                entity_id       INTEGER,
                ip_address      TEXT,
                user_agent      TEXT,
                details         JSONB,
                created_at      TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log(user_id);
            CREATE INDEX IF NOT EXISTS idx_audit_log_entity ON audit_log(entity_type, entity_id);
            CREATE INDEX IF NOT EXISTS idx_audit_log_created ON audit_log(created_at DESC);
        """)

        # Add user_id to organization_profile if not present
        await conn.execute("""
            ALTER TABLE organization_profile ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
        """)

    logger.info("NeonDB tables ready")


async def save_analysis(filename: str, result: dict, user_id: int) -> int:
    """
    Persist a completed multi-agent analysis to NeonDB.
    Returns the new analysis id.
    
    Args:
        filename: Name of the uploaded file
        result: Analysis result dictionary from orchestrator
        user_id: ID of the user who owns this analysis
    """
    pool = await get_pool()
    summary = result.get("summary", {})
    pipeline = result.get("pipeline_stats", {})
    ingestion = pipeline.get("ingestion", {})
    ci = pipeline.get("carbon_intensity", {})

    async with pool.acquire() as conn:
        async with conn.transaction():
            # Insert analysis summary with user_id
            analysis_id = await conn.fetchval("""
                INSERT INTO analyses
                    (user_id, filename, total_emissions, total_cost, total_energy,
                     top_service, top_region, original_rows, compressed_rows, api_calls)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
                RETURNING id
            """,
                user_id,
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

            # Insert emission records with user_id
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
                        user_id,
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
                        (user_id, analysis_id, service, region, zone, usage_type, record_date,
                         usage_amount, cost, energy_kwh, carbon_intensity,
                         emissions_kg, resource_id, intensity_source)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14)
                """, rows)

            # Insert API call logs with user_id
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
                        user_id,
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
                        (user_id, analysis_id, zone, record_date, called_at, endpoint,
                         response_ms, carbon_intensity, source, status, error_msg)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
                """, log_rows)

    logger.info(f"Saved analysis id={analysis_id} with {len(records)} records")
    return analysis_id


async def get_analysis_history(user_id: int = None, limit: int = 20) -> list:
    """
    Fetch recent analyses for history view.
    
    Args:
        user_id: Optional user ID to filter analyses (None = all users)
        limit: Maximum number of records to return
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        if user_id is not None:
            rows = await conn.fetch("""
                SELECT id, user_id, filename, uploaded_at, total_emissions, total_cost,
                       total_energy, top_service, top_region, original_rows,
                       compressed_rows, api_calls
                FROM analyses
                WHERE user_id = $1
                ORDER BY uploaded_at DESC
                LIMIT $2
            """, user_id, limit)
        else:
            rows = await conn.fetch("""
                SELECT id, user_id, filename, uploaded_at, total_emissions, total_cost,
                       total_energy, top_service, top_region, original_rows,
                       compressed_rows, api_calls
                FROM analyses
                ORDER BY uploaded_at DESC
                LIMIT $1
            """, limit)
    return [dict(r) for r in rows]


async def get_analysis_records(analysis_id: int, user_id: int = None) -> list:
    """
    Fetch all emission records for a given analysis.
    
    Args:
        analysis_id: Analysis ID to fetch records for
        user_id: Optional user ID for ownership validation
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        if user_id is not None:
            # Validate user owns this analysis
            owner = await conn.fetchval("""
                SELECT user_id FROM analyses WHERE id = $1
            """, analysis_id)
            
            if owner != user_id:
                logger.warning(f"User {user_id} attempted to access analysis {analysis_id} owned by {owner}")
                return []
        
        rows = await conn.fetch("""
            SELECT * FROM emission_records
            WHERE analysis_id = $1
            ORDER BY record_date, service
        """, analysis_id)
    return [dict(r) for r in rows]


# ============================================================
# New User-Aware Database Functions
# ============================================================

async def save_analysis_summary(
    user_id: int,
    analysis_id: int,
    service_breakdown: dict,
    region_breakdown: dict,
    daily_breakdown: dict = None,
    time_breakdown: dict = None,
    top_hotspots: list = None,
    metadata: dict = None
) -> int:
    """
    Save precomputed analysis summary for fast dashboard loading.
    
    Args:
        user_id: Owner of the analysis
        analysis_id: Analysis to summarize
        service_breakdown: Service-level aggregation
        region_breakdown: Region-level aggregation
        daily_breakdown: Daily time-series data
        time_breakdown: Hourly time-series data
        top_hotspots: List of carbon hotspots
        metadata: Additional metadata
    
    Returns:
        Summary ID
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        summary_id = await conn.fetchval("""
            INSERT INTO analysis_summary
                (user_id, analysis_id, service_breakdown, region_breakdown,
                 daily_breakdown, time_breakdown, top_hotspots, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (analysis_id) 
            DO UPDATE SET
                service_breakdown = EXCLUDED.service_breakdown,
                region_breakdown = EXCLUDED.region_breakdown,
                daily_breakdown = EXCLUDED.daily_breakdown,
                time_breakdown = EXCLUDED.time_breakdown,
                top_hotspots = EXCLUDED.top_hotspots,
                metadata = EXCLUDED.metadata,
                updated_at = NOW()
            RETURNING id
        """,
            user_id,
            analysis_id,
            service_breakdown,
            region_breakdown,
            daily_breakdown,
            time_breakdown,
            top_hotspots,
            metadata
        )
    
    logger.info(f"Saved analysis summary {summary_id} for analysis {analysis_id}")
    return summary_id


async def get_analysis_summary(analysis_id: int, user_id: int = None) -> dict:
    """
    Get precomputed analysis summary.
    
    Args:
        analysis_id: Analysis ID
        user_id: Optional user ID for ownership validation
    
    Returns:
        Summary dictionary or None if not found
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        if user_id is not None:
            row = await conn.fetchrow("""
                SELECT * FROM analysis_summary
                WHERE analysis_id = $1 AND user_id = $2
            """, analysis_id, user_id)
        else:
            row = await conn.fetchrow("""
                SELECT * FROM analysis_summary
                WHERE analysis_id = $1
            """, analysis_id)
    
    return dict(row) if row else None


async def save_recommendation_run(
    user_id: int,
    analysis_id: int,
    run_type: str,
    findings: dict,
    recommendations: list,
    hotspots: list = None,
    region_opportunities: list = None,
    time_opportunities: list = None,
    confidence_score: float = None,
    metadata: dict = None
) -> int:
    """
    Save AI-generated recommendations to avoid regenerating every time.
    
    Args:
        user_id: Owner of the analysis
        analysis_id: Analysis these recommendations are for
        run_type: Type of recommendation ('sustainability', 'cost', 'performance', 'explainable')
        findings: Key findings from analysis
        recommendations: List of recommendations
        hotspots: Carbon hotspots
        region_opportunities: Region migration opportunities
        time_opportunities: Time-shifting opportunities
        confidence_score: Confidence in recommendations (0.00-1.00)
        metadata: Additional metadata
    
    Returns:
        Recommendation run ID
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        run_id = await conn.fetchval("""
            INSERT INTO recommendation_runs
                (user_id, analysis_id, run_type, findings, recommendations,
                 hotspots, region_opportunities, time_opportunities,
                 confidence_score, metadata, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 'completed')
            RETURNING id
        """,
            user_id,
            analysis_id,
            run_type,
            findings,
            recommendations,
            hotspots,
            region_opportunities,
            time_opportunities,
            confidence_score,
            metadata
        )
    
    logger.info(f"Saved recommendation run {run_id} ({run_type}) for analysis {analysis_id}")
    return run_id


async def get_recommendation_runs(
    analysis_id: int = None,
    user_id: int = None,
    run_type: str = None,
    limit: int = 10
) -> list:
    """
    Get recommendation runs with optional filtering.
    
    Args:
        analysis_id: Filter by analysis
        user_id: Filter by user
        run_type: Filter by run type
        limit: Maximum results
    
    Returns:
        List of recommendation runs
    """
    pool = await get_pool()
    
    conditions = []
    params = []
    param_idx = 1
    
    if user_id is not None:
        conditions.append(f"user_id = ${param_idx}")
        params.append(user_id)
        param_idx += 1
    
    if analysis_id is not None:
        conditions.append(f"analysis_id = ${param_idx}")
        params.append(analysis_id)
        param_idx += 1
    
    if run_type is not None:
        conditions.append(f"run_type = ${param_idx}")
        params.append(run_type)
        param_idx += 1
    
    params.append(limit)
    
    where_clause = " AND ".join(conditions) if conditions else "TRUE"
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(f"""
            SELECT * FROM recommendation_runs
            WHERE {where_clause}
            ORDER BY generated_at DESC
            LIMIT ${param_idx}
        """, *params)
    
    return [dict(r) for r in rows]


async def save_user_insight(
    user_id: int,
    insight_type: str,
    time_period: str = None,
    period_start: str = None,
    period_end: str = None,
    total_emissions_kg: float = None,
    total_cost: float = None,
    total_energy_kwh: float = None,
    analysis_count: int = None,
    top_services: dict = None,
    top_regions: dict = None,
    trends: dict = None,
    alerts: dict = None
) -> int:
    """
    Save aggregated user insights for personalized dashboards.
    
    Args:
        user_id: User to save insights for
        insight_type: Type of insight ('monthly_trend', 'cost_alert', 'carbon_goal', 'service_pattern')
        time_period: Period granularity ('daily', 'weekly', 'monthly', 'yearly')
        period_start: Start of time period
        period_end: End of time period
        total_emissions_kg: Total emissions in period
        total_cost: Total cost in period
        total_energy_kwh: Total energy in period
        analysis_count: Number of analyses in period
        top_services: Top services by emissions
        top_regions: Top regions by emissions
        trends: Trend data
        alerts: Alert data
    
    Returns:
        Insight ID
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        insight_id = await conn.fetchval("""
            INSERT INTO user_insights
                (user_id, insight_type, time_period, period_start, period_end,
                 total_emissions_kg, total_cost, total_energy_kwh, analysis_count,
                 top_services, top_regions, trends, alerts)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            ON CONFLICT (user_id, insight_type, period_start)
            WHERE period_start IS NOT NULL
            DO UPDATE SET
                total_emissions_kg = EXCLUDED.total_emissions_kg,
                total_cost = EXCLUDED.total_cost,
                total_energy_kwh = EXCLUDED.total_energy_kwh,
                analysis_count = EXCLUDED.analysis_count,
                top_services = EXCLUDED.top_services,
                top_regions = EXCLUDED.top_regions,
                trends = EXCLUDED.trends,
                alerts = EXCLUDED.alerts,
                updated_at = NOW()
            RETURNING id
        """,
            user_id,
            insight_type,
            time_period,
            period_start,
            period_end,
            total_emissions_kg,
            total_cost,
            total_energy_kwh,
            analysis_count,
            top_services,
            top_regions,
            trends,
            alerts
        )
    
    logger.info(f"Saved user insight {insight_id} for user {user_id}")
    return insight_id


async def get_user_insights(
    user_id: int,
    insight_type: str = None,
    time_period: str = None,
    limit: int = 10
) -> list:
    """
    Get user insights with optional filtering.
    
    Args:
        user_id: User to get insights for
        insight_type: Optional insight type filter
        time_period: Optional time period filter
        limit: Maximum results
    
    Returns:
        List of user insights
    """
    pool = await get_pool()
    
    conditions = [f"user_id = $1"]
    params = [user_id]
    param_idx = 2
    
    if insight_type is not None:
        conditions.append(f"insight_type = ${param_idx}")
        params.append(insight_type)
        param_idx += 1
    
    if time_period is not None:
        conditions.append(f"time_period = ${param_idx}")
        params.append(time_period)
        param_idx += 1
    
    params.append(limit)
    
    where_clause = " AND ".join(conditions)
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(f"""
            SELECT * FROM user_insights
            WHERE {where_clause}
            ORDER BY period_start DESC NULLS LAST, created_at DESC
            LIMIT ${param_idx}
        """, *params)
    
    return [dict(r) for r in rows]


async def log_audit_event(
    user_id: int,
    action: str,
    entity_type: str,
    entity_id: int = None,
    ip_address: str = None,
    user_agent: str = None,
    details: dict = None
):
    """
    Log an audit event for compliance and debugging.
    
    Args:
        user_id: User performing the action
        action: Action type ('create', 'read', 'update', 'delete')
        entity_type: Entity type ('analysis', 'emission_record', 'recommendation', etc.)
        entity_id: ID of the entity
        ip_address: User's IP address
        user_agent: User's browser/client
        details: Additional details
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO audit_log
                (user_id, action, entity_type, entity_id, ip_address, user_agent, details)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
            user_id,
            action,
            entity_type,
            entity_id,
            ip_address,
            user_agent,
            details
        )


async def verify_user_ownership(user_id: int, entity_type: str, entity_id: int) -> bool:
    """
    Verify that a user owns a specific entity.
    
    Args:
        user_id: User ID to check
        entity_type: Type of entity ('analysis', 'emission_record', etc.)
        entity_id: Entity ID to check
    
    Returns:
        True if user owns the entity, False otherwise
    """
    pool = await get_pool()
    
    table_map = {
        'analysis': 'analyses',
        'emission_record': 'emission_records',
        'api_call_log': 'api_call_logs',
        'organization_profile': 'organization_profile',
        'recommendation_run': 'recommendation_runs',
        'analysis_summary': 'analysis_summary',
        'user_insight': 'user_insights'
    }
    
    table = table_map.get(entity_type)
    if not table:
        logger.warning(f"Unknown entity type: {entity_type}")
        return False
    
    async with pool.acquire() as conn:
        owner_id = await conn.fetchval(f"""
            SELECT user_id FROM {table} WHERE id = $1
        """, entity_id)
    
    return owner_id == user_id if owner_id else False
