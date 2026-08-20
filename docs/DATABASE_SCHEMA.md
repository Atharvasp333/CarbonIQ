# Database Schema

## Database: NeonDB (PostgreSQL)
Connection: asyncpg with connection pooling (min: 1, max: 5)

**Migration Status:** Enhanced with user ownership (Migration 001)

---

## Core Tables

### 1. **users**
User account management
```sql
id          SERIAL PRIMARY KEY
name        TEXT NOT NULL
email       TEXT UNIQUE NOT NULL
password    TEXT NOT NULL
created_at  TIMESTAMPTZ DEFAULT NOW()
```

### 2. **aws_credentials**
Encrypted AWS credentials per user (1:1 relationship)
```sql
id          SERIAL PRIMARY KEY
user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE
access_key  TEXT NOT NULL          -- Fernet-encrypted (enc:...)
secret_key  TEXT NOT NULL          -- Fernet-encrypted (enc:...)
region      TEXT NOT NULL DEFAULT 'ap-south-1'
bucket_name TEXT NOT NULL
file_key    TEXT                   -- Optional S3 key path
verified    BOOLEAN DEFAULT FALSE
verified_at TIMESTAMPTZ
created_at  TIMESTAMPTZ DEFAULT NOW()
updated_at  TIMESTAMPTZ DEFAULT NOW()
UNIQUE(user_id)
```

### 3. **analyses**
Analysis summary for each uploaded file (USER-AWARE)
```sql
id              SERIAL PRIMARY KEY
user_id         INTEGER REFERENCES users(id) ON DELETE CASCADE  -- NEW
filename        TEXT
uploaded_at     TIMESTAMPTZ DEFAULT NOW()
total_emissions NUMERIC(12,6)
total_cost      NUMERIC(12,4)
total_energy    NUMERIC(12,6)
top_service     TEXT
top_region      TEXT
original_rows   INTEGER
compressed_rows INTEGER
api_calls       INTEGER
```
**Indexes:**
- `idx_analyses_user` on (user_id)
- `idx_analyses_uploaded` on (uploaded_at)

### 4. **emission_records**
Detailed emission data per analysis (USER-AWARE)
```sql
id               SERIAL PRIMARY KEY
user_id          INTEGER REFERENCES users(id) ON DELETE CASCADE  -- NEW
analysis_id      INTEGER REFERENCES analyses(id) ON DELETE CASCADE
service          TEXT
region           TEXT
zone             TEXT
usage_type       TEXT
record_date      DATE
usage_amount     NUMERIC(20,8)
cost             NUMERIC(12,6)
energy_kwh       NUMERIC(16,8)
carbon_intensity NUMERIC(10,4)
emissions_kg     NUMERIC(16,8)
resource_id      TEXT
intensity_source TEXT
```
**Indexes:**
- `idx_emission_records_user` on (user_id)
- `idx_emission_records_user_date` on (user_id, record_date)
- `idx_emission_records_analysis` on (analysis_id)
- `idx_emission_records_service` on (service)
- `idx_emission_records_date` on (record_date)

### 5. **api_call_logs**
Carbon intensity API call tracking (USER-AWARE)
```sql
id               SERIAL PRIMARY KEY
user_id          INTEGER REFERENCES users(id) ON DELETE CASCADE  -- NEW
analysis_id      INTEGER REFERENCES analyses(id) ON DELETE CASCADE
zone             TEXT
record_date      DATE
called_at        TIMESTAMPTZ
endpoint         TEXT
response_ms      INTEGER
carbon_intensity NUMERIC(10,4)
source           TEXT
status           TEXT
error_msg        TEXT
```
**Indexes:**
- `idx_api_logs_user` on (user_id)
- `idx_api_logs_user_date` on (user_id, called_at)

### 6. **organization_profile**
Organization preferences for AI recommendations (USER-AWARE, 1:1 relationship)
```sql
id                      SERIAL PRIMARY KEY
user_id                 INTEGER REFERENCES users(id) ON DELETE CASCADE  -- NEW
organization_name       TEXT NOT NULL
primary_user_region     TEXT NOT NULL
workload_type           TEXT NOT NULL
latency_sensitivity     TEXT NOT NULL
migration_flexibility   TEXT NOT NULL
optimization_priority   TEXT NOT NULL
created_at              TIMESTAMPTZ DEFAULT NOW()
updated_at              TIMESTAMPTZ DEFAULT NOW()
UNIQUE(user_id)
```
**Indexes:**
- `idx_organization_profile_user` on (user_id)

---

## Intelligence Tables (NEW)

### 7. **analysis_summary**
Precomputed dashboard summaries for fast loading
```sql
id                  SERIAL PRIMARY KEY
user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
analysis_id         INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE
service_breakdown   JSONB
region_breakdown    JSONB
daily_breakdown     JSONB
time_breakdown      JSONB
top_hotspots        JSONB
metadata            JSONB
created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
UNIQUE(analysis_id)
```
**Indexes:**
- `idx_analysis_summary_user` on (user_id)
- `idx_analysis_summary_analysis` on (analysis_id)
- `idx_analysis_summary_unique` on (analysis_id)

**Purpose:** Store precomputed aggregations to avoid recalculating on every dashboard load.

### 8. **recommendation_runs**
AI-generated insights and recommendations storage
```sql
id                    SERIAL PRIMARY KEY
user_id               INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
analysis_id           INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE
run_type              TEXT NOT NULL  -- 'sustainability', 'cost', 'performance', 'explainable'
generated_at          TIMESTAMPTZ DEFAULT NOW()
findings              JSONB
recommendations       JSONB
hotspots              JSONB
region_opportunities  JSONB
time_opportunities    JSONB
confidence_score      NUMERIC(3,2)  -- 0.00 to 1.00
metadata              JSONB
status                TEXT DEFAULT 'completed'  -- 'pending', 'processing', 'completed', 'failed'
```
**Indexes:**
- `idx_recommendation_runs_user` on (user_id)
- `idx_recommendation_runs_analysis` on (analysis_id)
- `idx_recommendation_runs_type` on (run_type)
- `idx_recommendation_runs_generated` on (generated_at DESC)

**Purpose:** Cache AI recommendations to avoid regenerating on every page load. Supports multiple run types.

### 9. **user_insights**
Aggregated user intelligence over time periods
```sql
id                   SERIAL PRIMARY KEY
user_id              INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
insight_type         TEXT NOT NULL  -- 'monthly_trend', 'cost_alert', 'carbon_goal', 'service_pattern'
time_period          TEXT  -- 'daily', 'weekly', 'monthly', 'yearly'
period_start         TIMESTAMPTZ
period_end           TIMESTAMPTZ
total_emissions_kg   NUMERIC(16,8)
total_cost           NUMERIC(12,4)
total_energy_kwh     NUMERIC(16,8)
analysis_count       INTEGER
top_services         JSONB
top_regions          JSONB
trends               JSONB
alerts               JSONB
created_at           TIMESTAMPTZ DEFAULT NOW()
updated_at           TIMESTAMPTZ DEFAULT NOW()
UNIQUE(user_id, insight_type, period_start) WHERE period_start IS NOT NULL
```
**Indexes:**
- `idx_user_insights_user` on (user_id)
- `idx_user_insights_type` on (insight_type)
- `idx_user_insights_period` on (period_start, period_end)
- `idx_user_insights_unique` on (user_id, insight_type, period_start)

**Purpose:** Power personalized dashboards with historical trends and patterns.

### 10. **audit_log**
Security and compliance audit trail
```sql
id              SERIAL PRIMARY KEY
user_id         INTEGER REFERENCES users(id) ON DELETE SET NULL
action          TEXT NOT NULL  -- 'create', 'read', 'update', 'delete'
entity_type     TEXT NOT NULL  -- 'analysis', 'emission_record', 'recommendation', etc.
entity_id       INTEGER
ip_address      TEXT
user_agent      TEXT
details         JSONB
created_at      TIMESTAMPTZ DEFAULT NOW()
```
**Indexes:**
- `idx_audit_log_user` on (user_id)
- `idx_audit_log_entity` on (entity_type, entity_id)
- `idx_audit_log_created` on (created_at DESC)

**Purpose:** Track all data operations for security auditing, debugging, and compliance.

---

## Relationships

```
users
├── aws_credentials (1:1)
├── organization_profile (1:1)
├── analyses (1:many)
│   ├── emission_records (1:many)
│   ├── api_call_logs (1:many)
│   ├── analysis_summary (1:1)
│   └── recommendation_runs (1:many)
├── user_insights (1:many)
└── audit_log (1:many)
```

**Every business record is now traceable to a specific user.**

---

## Key Features

- ✓ **User Ownership**: All business data linked to users via `user_id`
- ✓ **Encryption**: AWS credentials encrypted using Fernet
- ✓ **Cascading Deletes**: Deleting a user removes all associated data
- ✓ **Indexing**: Optimized queries on user_id, service, date, and analysis_id
- ✓ **Timestamps**: Automatic tracking of creation and update times
- ✓ **Performance**: Precomputed summaries for fast dashboard loading
- ✓ **Intelligence**: Cached AI recommendations and insights
- ✓ **Audit Trail**: Complete logging of data operations
- ✓ **Multi-User**: Full support for multi-user scenarios

---

## Migration History

### Migration 001: Add User Ownership (2026-06-20)
- Added `user_id` to `analyses`, `emission_records`, `api_call_logs`, `organization_profile`
- Created `analysis_summary`, `recommendation_runs`, `user_insights`, `audit_log` tables
- Added indexes for efficient user-based queries
- Maintained backward compatibility with existing data

---

## Usage Examples

### Filter analyses by user
```python
analyses = await get_analysis_history(user_id=123, limit=20)
```

### Verify ownership before accessing data
```python
if await verify_user_ownership(user_id, 'analysis', analysis_id):
    records = await get_analysis_records(analysis_id, user_id)
```

### Save precomputed summary
```python
await save_analysis_summary(
    user_id=123,
    analysis_id=456,
    service_breakdown={...},
    region_breakdown={...}
)
```

### Cache AI recommendations
```python
await save_recommendation_run(
    user_id=123,
    analysis_id=456,
    run_type='sustainability',
    findings={...},
    recommendations=[...]
)
```

### Log audit events
```python
await log_audit_event(
    user_id=123,
    action='create',
    entity_type='analysis',
    entity_id=456,
    ip_address='192.168.1.1'
)
```
