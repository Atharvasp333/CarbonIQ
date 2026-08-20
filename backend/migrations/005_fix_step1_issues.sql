-- ============================================================
-- Migration: Fix Step 1 Issues - User Ownership & Data Integrity
-- Version: 005
-- Date: 2026-08-20
-- Purpose: Fix NULL user_id in analyses and ensure data integrity
-- ============================================================

-- STEP 1: Diagnose current state
DO $$
DECLARE
    null_analyses_count INTEGER;
    total_analyses_count INTEGER;
    total_users_count INTEGER;
    null_emission_records_count INTEGER;
    null_profile_count INTEGER;
BEGIN
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'STEP 1 DIAGNOSTIC: Current Database State';
    RAISE NOTICE '==========================================================';
    
    -- Check users
    SELECT COUNT(*) INTO total_users_count FROM users;
    RAISE NOTICE 'Total users in system: %', total_users_count;
    
    -- Check analyses
    SELECT COUNT(*) INTO total_analyses_count FROM analyses;
    SELECT COUNT(*) INTO null_analyses_count FROM analyses WHERE user_id IS NULL;
    RAISE NOTICE 'Total analyses: %', total_analyses_count;
    RAISE NOTICE 'Analyses with NULL user_id: %', null_analyses_count;
    
    -- Check emission_records
    SELECT COUNT(*) INTO null_emission_records_count FROM emission_records WHERE user_id IS NULL;
    RAISE NOTICE 'Emission records with NULL user_id: %', null_emission_records_count;
    
    -- Check organization profiles
    SELECT COUNT(*) INTO null_profile_count FROM organization_profile WHERE user_id IS NULL;
    RAISE NOTICE 'Organization profiles with NULL user_id: %', null_profile_count;
    
    RAISE NOTICE '==========================================================';
END $$;

-- STEP 2: Fix analyses with NULL user_id
-- Strategy: If only one user exists, assign all orphaned analyses to that user
-- If multiple users exist, assign to the first user (oldest account)
DO $$
DECLARE
    target_user_id INTEGER;
    updated_count INTEGER;
    user_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'STEP 2: Fix NULL user_id in analyses';
    RAISE NOTICE '==========================================================';
    
    -- Count users
    SELECT COUNT(*) INTO user_count FROM users;
    
    IF user_count = 0 THEN
        RAISE NOTICE 'WARNING: No users found - cannot fix analyses';
    ELSIF user_count = 1 THEN
        -- Single user - assign all orphaned analyses to them
        SELECT id INTO target_user_id FROM users LIMIT 1;
        
        UPDATE analyses SET user_id = target_user_id WHERE user_id IS NULL;
        GET DIAGNOSTICS updated_count = ROW_COUNT;
        
        RAISE NOTICE 'Single user system detected';
        RAISE NOTICE 'Assigned % orphaned analyses to user_id=%', updated_count, target_user_id;
    ELSE
        -- Multiple users - assign to oldest user (most likely to be the original owner)
        SELECT id INTO target_user_id FROM users ORDER BY created_at ASC LIMIT 1;
        
        UPDATE analyses SET user_id = target_user_id WHERE user_id IS NULL;
        GET DIAGNOSTICS updated_count = ROW_COUNT;
        
        RAISE NOTICE 'Multiple users detected';
        RAISE NOTICE 'Assigned % orphaned analyses to oldest user (user_id=%)', updated_count, target_user_id;
        RAISE NOTICE 'WARNING: Manual verification recommended for multi-user systems';
    END IF;
    
    RAISE NOTICE '==========================================================';
END $$;

-- STEP 3: Backfill emission_records.user_id from analyses
DO $$
DECLARE
    backfilled_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'STEP 3: Backfill emission_records.user_id';
    RAISE NOTICE '==========================================================';
    
    UPDATE emission_records er
    SET user_id = a.user_id
    FROM analyses a
    WHERE er.analysis_id = a.id
      AND er.user_id IS NULL
      AND a.user_id IS NOT NULL;
    
    GET DIAGNOSTICS backfilled_count = ROW_COUNT;
    RAISE NOTICE 'Backfilled % emission records from analyses', backfilled_count;
    RAISE NOTICE '==========================================================';
END $$;

-- STEP 4: Backfill api_call_logs.user_id from analyses
DO $$
DECLARE
    backfilled_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'STEP 4: Backfill api_call_logs.user_id';
    RAISE NOTICE '==========================================================';
    
    UPDATE api_call_logs acl
    SET user_id = a.user_id
    FROM analyses a
    WHERE acl.analysis_id = a.id
      AND acl.user_id IS NULL
      AND a.user_id IS NOT NULL;
    
    GET DIAGNOSTICS backfilled_count = ROW_COUNT;
    RAISE NOTICE 'Backfilled % api call logs from analyses', backfilled_count;
    RAISE NOTICE '==========================================================';
END $$;

-- STEP 5: Fix organization_profile with NULL user_id
DO $$
DECLARE
    target_user_id INTEGER;
    updated_count INTEGER;
    user_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'STEP 5: Fix NULL user_id in organization_profile';
    RAISE NOTICE '==========================================================';
    
    SELECT COUNT(*) INTO user_count FROM users;
    
    IF user_count = 0 THEN
        RAISE NOTICE 'WARNING: No users found - cannot fix profiles';
    ELSIF user_count = 1 THEN
        SELECT id INTO target_user_id FROM users LIMIT 1;
        
        UPDATE organization_profile SET user_id = target_user_id WHERE user_id IS NULL;
        GET DIAGNOSTICS updated_count = ROW_COUNT;
        
        RAISE NOTICE 'Assigned % orphaned profiles to user_id=%', updated_count, target_user_id;
    ELSE
        SELECT id INTO target_user_id FROM users ORDER BY created_at ASC LIMIT 1;
        
        UPDATE organization_profile SET user_id = target_user_id WHERE user_id IS NULL;
        GET DIAGNOSTICS updated_count = ROW_COUNT;
        
        RAISE NOTICE 'Assigned % orphaned profiles to oldest user (user_id=%)', updated_count, target_user_id;
        RAISE NOTICE 'WARNING: Manual verification recommended';
    END IF;
    
    RAISE NOTICE '==========================================================';
END $$;

-- STEP 6: Verify all fixes
DO $$
DECLARE
    remaining_null_analyses INTEGER;
    remaining_null_emissions INTEGER;
    remaining_null_logs INTEGER;
    remaining_null_profiles INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'STEP 6: Verification';
    RAISE NOTICE '==========================================================';
    
    SELECT COUNT(*) INTO remaining_null_analyses FROM analyses WHERE user_id IS NULL;
    SELECT COUNT(*) INTO remaining_null_emissions FROM emission_records WHERE user_id IS NULL;
    SELECT COUNT(*) INTO remaining_null_logs FROM api_call_logs WHERE user_id IS NULL;
    SELECT COUNT(*) INTO remaining_null_profiles FROM organization_profile WHERE user_id IS NULL;
    
    IF remaining_null_analyses = 0 THEN
        RAISE NOTICE '✓ All analyses have valid user_id';
    ELSE
        RAISE WARNING '✗ Still have % analyses with NULL user_id', remaining_null_analyses;
    END IF;
    
    IF remaining_null_emissions = 0 THEN
        RAISE NOTICE '✓ All emission_records have valid user_id';
    ELSE
        RAISE WARNING '✗ Still have % emission_records with NULL user_id', remaining_null_emissions;
    END IF;
    
    IF remaining_null_logs = 0 THEN
        RAISE NOTICE '✓ All api_call_logs have valid user_id';
    ELSE
        RAISE WARNING '✗ Still have % api_call_logs with NULL user_id', remaining_null_logs;
    END IF;
    
    IF remaining_null_profiles = 0 THEN
        RAISE NOTICE '✓ All organization_profiles have valid user_id';
    ELSE
        RAISE WARNING '✗ Still have % organization_profiles with NULL user_id', remaining_null_profiles;
    END IF;
    
    RAISE NOTICE '==========================================================';
END $$;

-- STEP 7: Display current state for logging
DO $$
DECLARE
    rec RECORD;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'STEP 7: Current User-Analysis Mapping';
    RAISE NOTICE '==========================================================';
    
    FOR rec IN 
        SELECT u.id as user_id, u.email, COUNT(a.id) as analysis_count
        FROM users u
        LEFT JOIN analyses a ON a.user_id = u.id
        GROUP BY u.id, u.email
        ORDER BY u.created_at ASC
    LOOP
        RAISE NOTICE 'User ID=% (%) has % analyses', rec.user_id, rec.email, rec.analysis_count;
    END LOOP;
    
    RAISE NOTICE '==========================================================';
END $$;

-- STEP 8: Summary
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'Migration 005 Complete';
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'Changes applied:';
    RAISE NOTICE '  ✓ Fixed NULL user_id in analyses';
    RAISE NOTICE '  ✓ Backfilled emission_records.user_id from analyses';
    RAISE NOTICE '  ✓ Backfilled api_call_logs.user_id from analyses';
    RAISE NOTICE '  ✓ Fixed NULL user_id in organization_profile';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Verify intelligence engine can now find analyses';
    RAISE NOTICE '  2. Test recommendation generation';
    RAISE NOTICE '  3. Verify user isolation (each user sees only their data)';
    RAISE NOTICE '==========================================================';
END $$;
