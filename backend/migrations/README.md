# Database Migrations

This directory contains PostgreSQL migration scripts for the Neon database.

## Prerequisites

1. Python 3.8+ installed
2. Dependencies installed: `pip install -r ../requirements.txt`
3. `.env` file configured in `backend/.env` with `DATABASE_URL`

## Setup & Verification

### Step 1: Verify Environment Setup

```bash
cd backend
python migrations/setup.py
```

This will check:
- ✓ `.env` file exists
- ✓ `DATABASE_URL` is set
- ✓ Database connection works
- ✓ Required tables exist
- ✓ Users exist in database

**If setup.py reports issues, fix them before proceeding.**

## Quick Start

### Run all pending migrations
```bash
cd backend
python migrations/run_migrations.py migrate
```

### Preview migrations (dry run)
```bash
python migrations/run_migrations.py migrate --dry-run
```

### List applied migrations
```bash
python migrations/run_migrations.py list
```

### Backfill existing data
```bash
python migrations/backfill_user_data.py
```

## Setting up DATABASE_URL

If you get "DATABASE_URL not set" error:

1. Create or edit `backend/.env` file
2. Add your database connection string:

```env
DATABASE_URL=postgresql://user:password@host:port/database
```

**Example for Neon:**
```env
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Example for local PostgreSQL:**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/carboniq
```

## Migration 001: Add User Ownership

**Purpose:** Make all business data user-specific while preserving existing records.

**What it does:**
1. Adds `user_id` column to `analyses` table
2. Adds `user_id` column to `emission_records` table (backfilled from analyses)
3. Adds `user_id` column to `api_call_logs` table (backfilled from analyses)
4. Adds `user_id` column to `organization_profile` table (unique per user)
5. Creates `analysis_summary` table for precomputed dashboard data
6. Creates `recommendation_runs` table for AI insights storage
7. Creates `user_insights` table for aggregated user intelligence
8. Creates `audit_log` table for tracking data ownership

**Safety:**
- ✓ Non-destructive (no table drops)
- ✓ No data deletion
- ✓ Adds columns as NULLABLE first
- ✓ Backfills where possible
- ✓ Idempotent (safe to run multiple times)

## Backfilling Data

After running the migration, you need to assign existing records to users. Options:

### Option 1: Assign all to first user
```sql
UPDATE analyses SET user_id = (SELECT id FROM users ORDER BY id LIMIT 1)
WHERE user_id IS NULL;
```

### Option 2: Assign based on AWS credentials
```sql
UPDATE analyses a
SET user_id = ac.user_id
FROM aws_credentials ac
WHERE a.user_id IS NULL
  AND ac.verified = true
LIMIT 1;
```

### Option 3: Assign to specific user
```sql
UPDATE analyses SET user_id = 1 WHERE user_id IS NULL;
UPDATE emission_records SET user_id = 1 WHERE user_id IS NULL;
UPDATE api_call_logs SET user_id = 1 WHERE user_id IS NULL;
UPDATE organization_profile SET user_id = 1 WHERE user_id IS NULL;
```

## Enforcing NOT NULL (After Backfill)

Once all data is backfilled, optionally enforce NOT NULL:

```sql
ALTER TABLE analyses ALTER COLUMN user_id SET NOT NULL;
ALTER TABLE emission_records ALTER COLUMN user_id SET NOT NULL;
ALTER TABLE api_call_logs ALTER COLUMN user_id SET NOT NULL;
ALTER TABLE organization_profile ALTER COLUMN user_id SET NOT NULL;
```

## New Tables

### analysis_summary
Stores precomputed dashboard summaries to improve performance:
- Service breakdown (JSONB)
- Region breakdown (JSONB)
- Daily breakdown (JSONB)
- Time breakdown (JSONB)
- Top hotspots (JSONB)

**Usage:** Generate once per analysis, query for fast dashboard loads.

### recommendation_runs
Stores AI-generated insights and recommendations:
- Run type (sustainability, cost, performance, explainable)
- Findings (JSONB)
- Recommendations (JSONB)
- Confidence score
- Region/time opportunities

**Usage:** Avoid regenerating recommendations on every page load.

### user_insights
Aggregated user intelligence over time periods:
- Monthly trends
- Cost alerts
- Carbon goals
- Service patterns

**Usage:** Power personalized dashboards and historical analytics.

### audit_log
Tracks all data operations for compliance and debugging:
- User actions (create, read, update, delete)
- Entity types and IDs
- IP address and user agent
- Timestamps

**Usage:** Security auditing, debugging, compliance reporting.

## Database Relationships After Migration

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

## Verification

After migration, verify user ownership:

```sql
-- Count analyses without user_id
SELECT COUNT(*) FROM analyses WHERE user_id IS NULL;

-- Count emission records without user_id
SELECT COUNT(*) FROM emission_records WHERE user_id IS NULL;

-- Check user data distribution
SELECT 
    u.email,
    COUNT(DISTINCT a.id) as analyses_count,
    COUNT(er.id) as emission_records_count
FROM users u
LEFT JOIN analyses a ON a.user_id = u.id
LEFT JOIN emission_records er ON er.user_id = u.id
GROUP BY u.id, u.email;
```

## Rollback

To mark a migration as rolled back (manual SQL required):

```bash
python migrations/run_migrations.py rollback --version 001_add_user_ownership
```

Note: This only marks the migration as rolled back. You must manually revert changes:

```sql
-- WARNING: Only use if you need to completely undo the migration
DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS user_insights;
DROP TABLE IF EXISTS recommendation_runs;
DROP TABLE IF EXISTS analysis_summary;

ALTER TABLE organization_profile DROP COLUMN IF EXISTS user_id;
ALTER TABLE api_call_logs DROP COLUMN IF EXISTS user_id;
ALTER TABLE emission_records DROP COLUMN IF EXISTS user_id;
ALTER TABLE analyses DROP COLUMN IF EXISTS user_id;
```

## Best Practices

1. **Always backup before migrations** - Create a database snapshot
2. **Test in development first** - Verify migrations work correctly
3. **Use dry run** - Preview changes before applying
4. **Monitor execution time** - Large tables may take time to backfill
5. **Validate data** - Check counts and relationships after migration
6. **Enforce constraints gradually** - Add NOT NULL only after validation

## Troubleshooting

### Migration fails with foreign key violation
- Ensure users table has records before running migration
- Check that analyses table exists and has valid data

### Backfill doesn't populate all records
- Some records may not have valid analysis_id relationships
- Manually assign these records to a default user

### Performance issues
- Large tables may take time to add indexes
- Consider running during low-traffic periods
- Monitor database CPU and memory usage
