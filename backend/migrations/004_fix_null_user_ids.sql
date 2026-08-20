-- ============================================================
-- Migration: Fix NULL user_id in existing analyses
-- Version: 004
-- Date: 2026-08-20
-- Purpose: Identify and report analyses with NULL user_id
-- ============================================================

-- IMPORTANT: This migration is READ-ONLY for investigation
-- It does NOT modify data - only reports issues

-- ============================================================
-- STEP 1: Report analyses with NULL user_id
-- ============================================================
DO $$
DECLARE
    null_count INTEGER;
    total_count INTEGER;
BEGIN
    -- Count analyses with NULL user_id
    SELECT COUNT(*) INTO null_count 
    FROM analyses 
    WHERE user_id IS NULL;
    
    -- Count total analyses
    SELECT COUNT(*) INTO total_count 
    FROM analyses;
    
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'DATA INTEGRITY CHECK: analyses.user_id';
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'Total analyses: %', total_count;
    RAISE NOTICE 'Analyses with NULL user_id: %', null_count;
    
    IF null_count > 0 THEN
        RAISE NOTICE '';
        RAISE NOTICE 'WARNING: Found % analyses with NULL user_id', null_count;
        RAISE NOTICE 'These analyses cannot be accessed by the intelligence engine.';
        RAISE NOTICE '';
        RAISE NOTICE 'Analysis IDs with NULL user_id:';
        
        -- List the problematic analysis IDs
        FOR i IN (SELECT id, filename, uploaded_at 
                  FROM analyses 
                  WHERE user_id IS NULL 
                  ORDER BY uploaded_at DESC 
                  LIMIT 10)
        LOOP
            RAISE NOTICE '  - ID: %, Filename: %, Uploaded: %', i.id, i.filename, i.uploaded_at;
        END LOOP;
        
        IF null_count > 10 THEN
            RAISE NOTICE '  ... and % more', null_count - 10;
        END IF;
        
        RAISE NOTICE '';
        RAISE NOTICE 'RECOMMENDED ACTION:';
        RAISE NOTICE '1. Verify if these analyses belong to a specific user';
        RAISE NOTICE '2. If yes, manually assign user_id:';
        RAISE NOTICE '   UPDATE analyses SET user_id = <correct_user_id> WHERE id IN (<analysis_ids>);';
        RAISE NOTICE '3. If no valid user exists, these records are orphaned and should be cleaned up';
        RAISE NOTICE '';
    ELSE
        RAISE NOTICE 'GOOD: All analyses have valid user_id';
    END IF;
    
    RAISE NOTICE '==========================================================';
END $$;

-- ============================================================
-- STEP 2: Report emission_records with NULL user_id
-- ============================================================
DO $$
DECLARE
    null_count INTEGER;
    total_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO null_count 
    FROM emission_records 
    WHERE user_id IS NULL;
    
    SELECT COUNT(*) INTO total_count 
    FROM emission_records;
    
    RAISE NOTICE '';
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'DATA INTEGRITY CHECK: emission_records.user_id';
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'Total emission records: %', total_count;
    RAISE NOTICE 'Records with NULL user_id: %', null_count;
    
    IF null_count > 0 THEN
        RAISE NOTICE '';
        RAISE NOTICE 'WARNING: Found % emission records with NULL user_id', null_count;
        RAISE NOTICE 'Attempting to backfill from analyses table...';
        
        -- Attempt automatic backfill
        UPDATE emission_records er
        SET user_id = a.user_id
        FROM analyses a
        WHERE er.analysis_id = a.id
          AND er.user_id IS NULL
          AND a.user_id IS NOT NULL;
        
        GET DIAGNOSTICS null_count = ROW_COUNT;
        RAISE NOTICE 'Backfilled % emission records', null_count;
    ELSE
        RAISE NOTICE 'GOOD: All emission records have valid user_id';
    END IF;
    
    RAISE NOTICE '==========================================================';
END $$;

-- ============================================================
-- STEP 3: Report organization_profile with NULL user_id
-- ============================================================
DO $$
DECLARE
    null_count INTEGER;
    total_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO null_count 
    FROM organization_profile 
    WHERE user_id IS NULL;
    
    SELECT COUNT(*) INTO total_count 
    FROM organization_profile;
    
    RAISE NOTICE '';
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'DATA INTEGRITY CHECK: organization_profile.user_id';
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'Total profiles: %', total_count;
    RAISE NOTICE 'Profiles with NULL user_id: %', null_count;
    
    IF null_count > 0 THEN
        RAISE NOTICE '';
        RAISE NOTICE 'WARNING: Found % organization profiles with NULL user_id', null_count;
        RAISE NOTICE 'Manual assignment required - cannot determine correct user automatically.';
    ELSE
        RAISE NOTICE 'GOOD: All profiles have valid user_id';
    END IF;
    
    RAISE NOTICE '==========================================================';
END $$;

-- ============================================================
-- Summary
-- ============================================================
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'Migration 004 Complete - Data Integrity Check';
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Review the warnings above';
    RAISE NOTICE '2. Assign correct user_id to orphaned records if needed';
    RAISE NOTICE '3. Re-run this migration to verify all issues are resolved';
    RAISE NOTICE '==========================================================';
END $$;
