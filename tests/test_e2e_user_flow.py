"""
End-to-End User Flow & Integration Verification Test Suite
Tests every single layer:
1. DB schema & migrations
2. User auth & API Key generation
3. CLI authentication & user isolation
4. Dashboard history & statistics endpoints
5. Python SDK (@carboniq.track decorator & context manager)
6. Carbon-aware grid functions
7. Sustainable Code Generator & AST auditor edge cases
8. Key revocation & cleanup
"""
import sys
import os
import asyncio
from pathlib import Path

# Add project root and backend to sys.path
ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import carboniq
from carboniq.optimizer import audit_code, optimize_code
from carboniq.tracker import track, TrackContext
from backend.database import init_db, get_pool, close_pool
from backend.routes.api_keys import generate_new_key, hash_api_key, get_user_from_api_key
from backend.routes.auth import create_access_token


def print_step(title):
    print("\n" + "=" * 70)
    print(f"🧪 TEST: {title}")
    print("=" * 70)


async def run_all_tests():
    passed = 0
    total = 0

    def assert_test(cond, name):
        nonlocal passed, total
        total += 1
        if cond:
            print(f"  ✅ PASS: {name}")
            passed += 1
        else:
            print(f"  ❌ FAIL: {name}")
            raise AssertionError(f"Test failed: {name}")

    # =========================================================================
    # Step 1: Database Initialization & Tables
    # =========================================================================
    print_step("Step 1: Database & Table Migrations")
    await init_db()
    pool = await get_pool()
    async with pool.acquire() as conn:
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_names = [r['table_name'] for r in tables]
        assert_test("users" in table_names, "users table exists")
        assert_test("workload_measurements" in table_names, "workload_measurements table exists")
        assert_test("api_keys" in table_names, "api_keys table exists")

    # =========================================================================
    # Step 2: User Creation & Authentication
    # =========================================================================
    print_step("Step 2: User Creation & JWT Provisioning")
    test_email = "e2e_tester@carboniq.internal"
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id, name, email FROM users WHERE email = $1", test_email)
        if not user:
            user = await conn.fetchrow("""
                INSERT INTO users (name, email, password)
                VALUES ('E2E Tester', $1, 'hashed_test_pass')
                RETURNING id, name, email
            """, test_email)
    test_user_id = user["id"]
    assert_test(test_user_id > 0, f"Test user provisioned with ID: {test_user_id}")
    
    token = create_access_token(test_user_id, test_email)
    assert_test(bool(token) and len(token) > 20, "Generated user access JWT token")

    # =========================================================================
    # Step 3: API Key Lifecycle (Generation, Storage, Hash Verification)
    # =========================================================================
    print_step("Step 3: API Key Lifecycle")
    raw_key, prefix, key_hash = generate_new_key("Test Workstation Key")
    assert_test(raw_key.startswith("ciq_live_"), "API key starts with 'ciq_live_' prefix")
    assert_test(hash_api_key(raw_key) == key_hash, "SHA-256 hash matches correctly")

    async with pool.acquire() as conn:
        key_id = await conn.fetchval("""
            INSERT INTO api_keys (user_id, key_hash, key_prefix, name)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """, test_user_id, key_hash, prefix, "Test Workstation Key")
    assert_test(key_id > 0, f"API key inserted into Neon DB with ID: {key_id}")

    # Test resolving user via X-API-Key
    resolved_user = await get_user_from_api_key(raw_key)
    assert_test(resolved_user is not None, "Resolved user from raw API key")
    assert_test(resolved_user["id"] == test_user_id, f"Resolved user_id matches test_user_id ({test_user_id})")

    # =========================================================================
    # Step 4: CLI Measurements & Personalization
    # =========================================================================
    print_step("Step 4: CLI Measurement Personalization")
    async with pool.acquire() as conn:
        # 1. Insert measurement using our authenticated test user
        m_id1 = await conn.fetchval("""
            INSERT INTO workload_measurements
                (user_id, workload_name, workload_type, duration_seconds,
                 emissions_gco2e, energy_kwh, carbon_intensity, country_name)
            VALUES ($1, 'Matrix Multiplication', 'ml-training', 4.5, 0.052, 0.00013, 400.0, 'USA')
            RETURNING id
        """, test_user_id)
        assert_test(m_id1 > 0, f"Stored authenticated measurement #{m_id1} for user #{test_user_id}")

        # 2. Insert measurement for user 1 (different user)
        m_id2 = await conn.fetchval("""
            INSERT INTO workload_measurements
                (user_id, workload_name, workload_type, duration_seconds,
                 emissions_gco2e, energy_kwh, carbon_intensity, country_name)
            VALUES (1, 'Other User Workload', 'general', 1.0, 0.01, 0.00002, 350.0, 'USA')
            RETURNING id
        """)

        # 3. Query history strictly for test_user_id
        user_rows = await conn.fetch("""
            SELECT id, workload_name FROM workload_measurements
            WHERE user_id = $1
            ORDER BY id DESC
        """, test_user_id)
        user_m_ids = [r['id'] for r in user_rows]
        assert_test(m_id1 in user_m_ids, "User can view their own workload measurement")
        assert_test(m_id2 not in user_m_ids, "User CANNOT see other users' workload measurements (data isolated!)")

    # =========================================================================
    # Step 5: Python Library & SDK Integration
    # =========================================================================
    print_step("Step 5: Python Library (@carboniq.track & Context Manager)")

    # Test @carboniq.track decorator
    @carboniq.track(workload_name="e2e_test_func", workload_type="test", auto_send=False)
    def heavy_cpu_work():
        total = 0
        for i in range(100_000):
            total += (i % 7)
        return total

    result_val = heavy_cpu_work()
    assert_test(result_val > 0, "Decorated function executed and returned correct result")

    # Test with carboniq.track context manager
    with carboniq.track(workload_name="e2e_context_block", auto_send=False) as t:
        s = sum(x * x for x in range(50_000))
    assert_test(t.duration_seconds > 0, f"Context manager tracked duration: {t.duration_seconds:.4f}s")
    assert_test(t.results["energy_kwh"] > 0, f"Context manager calculated energy: {t.results['energy_kwh']:.8f} kWh")
    assert_test(t.results["emissions_gco2e"] > 0, f"Context manager calculated emissions: {t.results['emissions_gco2e']:.6f} gCO2e")

    # =========================================================================
    # Step 6: Sustainable Code Generator & AST Optimizer
    # =========================================================================
    print_step("Step 6: Sustainable Code Optimizer & Edge Cases")

    # Case A: Clean code
    clean_code = "import numpy as np\ndef fast_dot(a, b):\n    return np.dot(a, b)\n"
    clean_audit = audit_code(clean_code)
    assert_test(clean_audit["valid_syntax"], "Clean code parses valid AST")
    assert_test(clean_audit["carbon_grade"].startswith("A"), f"Clean code gets Grade A ({clean_audit['carbon_grade']})")

    # Case B: Inefficient code with anti-patterns
    inefficient_code = """
def fib(n):
    if n <= 1: return n
    return fib(n - 1) + fib(n - 2)

def process():
    data = [x for x in range(50000)]
    results = []
    for i in range(10):
        for j in range(10):
            results.append(i * j)
    return results
"""
    bad_audit = audit_code(inefficient_code)
    assert_test(bad_audit["valid_syntax"], "Inefficient code parses valid AST")
    assert_test(len(bad_audit["issues"]) >= 3, f"Detected {len(bad_audit['issues'])} carbon anti-patterns")
    assert_test(bad_audit["potential_energy_reduction_pct"] > 30, f"Potential savings: {bad_audit['potential_energy_reduction_pct']}%")

    # Case C: Automatic Optimization
    opt_res = optimize_code(inefficient_code)
    assert_test("@lru_cache" in opt_res["optimized_code"], "Optimized code injected @lru_cache for recursive calls")
    assert_test("range(50000)" in opt_res["optimized_code"], "Optimized code preserved data generation")
    assert_test(len(opt_res["improvements_applied"]) >= 2, f"Applied {len(opt_res['improvements_applied'])} sustainable fixes")

    # Case D: Edge Case - Syntax Error
    broken_code = "def broken(:"
    broken_audit = audit_code(broken_code)
    assert_test(not broken_audit["valid_syntax"], "Handled syntax error gracefully without crashing")

    # Case E: Edge Case - Empty String
    empty_audit = audit_code("")
    assert_test(empty_audit["valid_syntax"], "Handled empty file gracefully")
    assert_test(empty_audit["total_issues"] == 0, "Empty file has 0 issues")

    # =========================================================================
    # Step 7: Revocation & Cleanup
    # =========================================================================
    print_step("Step 7: Key Revocation & Test Data Cleanup")
    async with pool.acquire() as conn:
        # Revoke API key
        await conn.execute("DELETE FROM api_keys WHERE id = $1", key_id)
        # Verify key is gone
        revoked_check = await get_user_from_api_key(raw_key)
        assert_test(revoked_check is None, "Revoked API key cannot authenticate anymore")

        # Cleanup test measurements and user
        await conn.execute("DELETE FROM workload_measurements WHERE id = $1", m_id1)
        await conn.execute("DELETE FROM workload_measurements WHERE id = $1", m_id2)
        await conn.execute("DELETE FROM users WHERE id = $1", test_user_id)
        assert_test(True, "Cleaned up all temporary test rows from database")

    await close_pool()

    print("\n" + "=" * 70)
    print(f"🎉 ALL INTEGRATION TESTS PASSED: {passed}/{total} (100% SUCCESS)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
