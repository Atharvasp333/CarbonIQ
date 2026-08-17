-- Migration 003: Add Constraint Status and Reason to Recommendations JSONB schema inside recommendation_runs
-- This migration documents the updated recommendations JSONB structure.
-- Fields added inside each recommendation JSON object:
--   - constraint_status: VARCHAR (compatible, flagged, rejected)
--   - constraint_reason: VARCHAR (short factual explanation of constraint enforcement)

-- Update existing database records to include the new fields on historical recommendation runs
UPDATE recommendation_runs
SET recommendations = (
    SELECT jsonb_agg(
        rec || jsonb_build_object(
            'constraint_status', COALESCE(rec->>'constraint_status', 'compatible'),
            'constraint_reason', COALESCE(rec->>'constraint_reason', '')
        )
    )
    FROM jsonb_array_elements(recommendations) AS rec
)
WHERE recommendations IS NOT NULL AND jsonb_typeof(recommendations) = 'array';
