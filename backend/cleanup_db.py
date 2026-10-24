"""
Database cleanup and stats script
Run this to see what's in your database and clean up waste data
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_database_stats():
    """Check all tables and their row counts"""
    url = os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(url)
    
    print("=" * 80)
    print("DATABASE STATISTICS")
    print("=" * 80)
    
    # Get all table names
    tables = await conn.fetch("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    
    print(f"\nFound {len(tables)} tables:\n")
    
    total_rows = 0
    for table in tables:
        table_name = table['table_name']
        count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
        total_rows += count
        
        # Get table size
        size = await conn.fetchval(f"""
            SELECT pg_size_pretty(pg_total_relation_size('{table_name}'))
        """)
        
        print(f"  {table_name:30s} | Rows: {count:8d} | Size: {size}")
    
    print(f"\n{'Total rows across all tables':30s} | {total_rows:8d}")
    print("=" * 80)
    
    # Show users
    print("\n" + "=" * 80)
    print("USERS")
    print("=" * 80)
    users = await conn.fetch("SELECT id, email, created_at FROM users ORDER BY id")
    for user in users:
        print(f"  ID: {user['id']:3d} | Email: {user['email']:40s} | Created: {user['created_at']}")
    
    # Show analyses count per user
    print("\n" + "=" * 80)
    print("ANALYSES PER USER")
    print("=" * 80)
    
    # Check if analyses has user_id column
    has_user_id = await conn.fetchval("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'analyses' 
            AND column_name = 'user_id'
        )
    """)
    
    if has_user_id:
        analyses_per_user = await conn.fetch("""
            SELECT user_id, COUNT(*) as count 
            FROM analyses 
            WHERE user_id IS NOT NULL
            GROUP BY user_id
            ORDER BY count DESC
        """)
        for row in analyses_per_user:
            print(f"  User ID: {row['user_id']:3d} | Analyses: {row['count']}")
    else:
        print("  ⚠️  'analyses' table does not have user_id column yet")
        total = await conn.fetchval("SELECT COUNT(*) FROM analyses")
        print(f"  Total analyses (no user tracking): {total}")
    
    # Show emission_records count
    print("\n" + "=" * 80)
    print("EMISSION RECORDS")
    print("=" * 80)
    emission_count = await conn.fetchval("SELECT COUNT(*) FROM emission_records")
    print(f"  Total emission records: {emission_count:,}")
    
    if emission_count > 0:
        # Sample some records
        sample = await conn.fetch("""
            SELECT service, region, COUNT(*) as count
            FROM emission_records
            GROUP BY service, region
            ORDER BY count DESC
            LIMIT 10
        """)
        print("\n  Top 10 service/region combinations:")
        for row in sample:
            print(f"    {row['service']:20s} | {row['region']:15s} | Count: {row['count']:,}")
    
    # Show recommendation_runs
    print("\n" + "=" * 80)
    print("RECOMMENDATION RUNS")
    print("=" * 80)
    rec_count = await conn.fetchval("SELECT COUNT(*) FROM recommendation_runs")
    print(f"  Total recommendation runs: {rec_count}")
    
    if rec_count > 0:
        recs = await conn.fetch("""
            SELECT id, user_id, run_type, generated_at, status
            FROM recommendation_runs
            ORDER BY generated_at DESC
            LIMIT 5
        """)
        print("\n  Latest 5 recommendation runs:")
        for rec in recs:
            print(f"    ID: {rec['id']:3d} | User: {rec['user_id']:3d} | Type: {rec['run_type']:20s} | Status: {rec['status']}")
    
    await conn.close()


async def cleanup_options():
    """Show cleanup options"""
    print("\n" + "=" * 80)
    print("CLEANUP OPTIONS")
    print("=" * 80)
    print("""
Available cleanup operations:
  1. Delete all test users (emails containing 'test', 'example.com', 'testlocal')
  2. Delete old emission_records (keep only last 30 days)
  3. Delete orphaned emission_records (no matching analysis_id)
  4. Delete old recommendation_runs (keep only last 10 per user)
  5. Delete duplicate analyses (same filename, keep latest)
  6. DANGER: Delete ALL data except your user (user_id=109)
  
Run specific cleanup by modifying this script.
""")


async def cleanup_test_users():
    """Delete test users and their data"""
    url = os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(url)
    
    # Find test users
    test_users = await conn.fetch("""
        SELECT id, email FROM users
        WHERE email ILIKE '%test%' 
        OR email LIKE '%example.com%'
        OR email LIKE '%testlocal%'
    """)
    
    print(f"\nFound {len(test_users)} test users:")
    for user in test_users:
        print(f"  ID: {user['id']} | Email: {user['email']}")
    
    if len(test_users) > 0:
        confirm = input("\nDelete these users and all their data? (yes/no): ")
        if confirm.lower() == 'yes':
            for user in test_users:
                await conn.execute("DELETE FROM users WHERE id = $1", user['id'])
                print(f"  ✓ Deleted user {user['email']}")
            print(f"\n✓ Deleted {len(test_users)} test users")
    
    await conn.close()


if __name__ == "__main__":
    print("CarbonIQ Database Cleanup Tool")
    print("=" * 80)
    
    asyncio.run(check_database_stats())
    asyncio.run(cleanup_options())
    
    # Uncomment to run specific cleanups:
    # asyncio.run(cleanup_test_users())
