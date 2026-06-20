-- Migration 002: Architectural Separation Tables
-- Adds tables to support Carbon Accounting + Sustainability Intelligence separation

-- Add user_id to existing tables (if not already present from migration 001)
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE emission_records ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE api_call_logs ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;

-- Analysis Summary Table (precomputed for fast dashboard loading)
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

CREATE INDEX IF NOT EXISTS idx_analysis_summary_user ON analysis_summary(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_summary_analysis ON analysis_summary(analysis_id);

-- Recommendation Runs Table (stores intelligence engine outputs)
CREATE TABLE IF NOT EXISTS recommendation_runs (
    id                      SERIAL PRIMARY KEY,
    user_id                 INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    analysis_id             INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    run_type                TEXT NOT NULL, -- 'sustainability', 'cost', 'performance', 'explainable'
    generated_at            TIMESTAMPTZ DEFAULT NOW(),
    findings                JSONB NOT NULL,
    recommendations         JSONB NOT NULL,
    hotspots                JSONB,
    region_opportunities    JSONB,
    time_opportunities      JSONB,
    confidence_score        NUMERIC(3,2),
    metadata                JSONB,
    status                  TEXT DEFAULT 'completed' -- 'pending', 'completed', 'failed'
);

CREATE INDEX IF NOT EXISTS idx_recommendation_runs_user ON recommendation_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_runs_analysis ON recommendation_runs(analysis_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_runs_type ON recommendation_runs(run_type);
CREATE INDEX IF NOT EXISTS idx_recommendation_runs_generated ON recommendation_runs(generated_at DESC);

-- User Insights Table (aggregated insights for personalized dashboards)
CREATE TABLE IF NOT EXISTS user_insights (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    insight_type        TEXT NOT NULL, -- 'monthly_trend', 'cost_alert', 'carbon_goal', 'service_pattern'
    time_period         TEXT, -- 'daily', 'weekly', 'monthly', 'yearly'
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
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, insight_type, period_start) WHERE period_start IS NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_user_insights_user ON user_insights(user_id);
CREATE INDEX IF NOT EXISTS idx_user_insights_type ON user_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_user_insights_period ON user_insights(period_start, period_end);

-- Audit Log Table (compliance and debugging)
CREATE TABLE IF NOT EXISTS audit_log (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action          TEXT NOT NULL, -- 'create', 'read', 'update', 'delete'
    entity_type     TEXT NOT NULL,
    entity_id       INTEGER,
    ip_address      TEXT,
    user_agent      TEXT,
    details         JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created ON audit_log(created_at DESC);

-- Add indexes for performance on existing tables
CREATE INDEX IF NOT EXISTS idx_analyses_user_uploaded ON analyses(user_id, uploaded_at DESC);
CREATE INDEX IF NOT EXISTS idx_emission_records_user_service ON emission_records(user_id, service);
CREATE INDEX IF NOT EXISTS idx_emission_records_user_date ON emission_records(user_id, record_date DESC);

COMMENT ON TABLE analysis_summary IS 'Precomputed analysis summaries for fast dashboard loading (Carbon Accounting Engine output)';
COMMENT ON TABLE recommendation_runs IS 'AI-generated recommendations cached for reuse (Sustainability Intelligence Engine output)';
COMMENT ON TABLE user_insights IS 'Aggregated user insights for personalized dashboards';
COMMENT ON TABLE audit_log IS 'Audit trail for compliance and debugging';
