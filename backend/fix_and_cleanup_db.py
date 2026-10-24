"""
Fix database schema and cleanup waste data
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def add_user_id_to_analyses():
    """Add user_id column to analyses table"""
    url = os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(url)
    
    print("=" * 80)
    print("STEP 1: Add user_id to analyses table")
    print("=" * 80)
    
    # Check if column exists
    has_column = await conn.fetchval("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'analyses' 
            AND column_name = 'user_id'
        )
    """)
    
    if has_column:
        print("✓ user_id column already exists in analyses table")
    else:
        print("Adding user_id column to analyses table...")
        await conn.execute("""
            ALTER TABLE analyses 
            ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
        """)
        print("✓ Added user_id column")
        
        # Set default user_id for existing records (use first user)
        await conn.execute("""
            UPDATE analyses SET user_id = 1 WHERE user_id IS NULL
        """)
        print("✓ Set user_id=1 for existing analyses")
    
    # Add user_id to emission_records if missing
    has_emission_user_id = await conn.fetchval("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'emission_records' 
            AND column_name = 'user_id'
        )
    """)
    
    if not has_emission_user_id:
        print("\nAdding user_id column to emission_records table...")
        await conn.execute("""
            ALTER TABLE emission_records 
            ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
        """)
        
        # Set user_id based on analysis_id
        await conn.execute("""
            UPDATE emission_records er
            SET user_id = a.user_id
            FROM analyses a
            WHERE er.analysis_id = a.id AND er.user_id IS NULL
        """)
        print("✓ Added user_id to emission_records and populated from analyses")
    
    await conn.close()


async def cleanup_test_data():
    """Delete test users and orphaned data"""
    url = os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(url)
    
    print("\n" + "=" * 80)
    print("STEP 2: Delete test/demo users")
    print("=" * 80)
    
    # Delete test user
    test_emails = ['testlocal@example.com', 'test@example.com']
    for email in test_emails:
        result = await conn.execute("DELETE FROM users WHERE email = $1", email)
        if result != "DELETE 0":
            print(f"✓ Deleted user: {email}")
    
    await conn.close()


async def cleanup_old_data():
    """Delete old/unnecessary data"""
    url = os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(url)
    
    print("\n" + "=" * 80)
    print("STEP 3: Clean up old/unnecessary data")
    print("=" * 80)
    
    # Delete orphaned emission_records (no matching analysis)
    orphaned_count = await conn.fetchval("""
        SELECT COUNT(*) FROM emission_records
        WHERE analysis_id NOT IN (SELECT id FROM analyses)
    """)
    if orphaned_count > 0:
        await conn.execute("""
            DELETE FROM emission_records
            WHERE analysis_id NOT IN (SELECT id FROM analyses)
        """)
        print(f"✓ Deleted {orphaned_count} orphaned emission records")
    
    # Delete orphaned api_call_logs
    orphaned_api_count = await conn.fetchval("""
        SELECT COUNT(*) FROM api_call_logs
        WHERE analysis_id NOT IN (SELECT id FROM analyses)
    """)
    if orphaned_api_count > 0:
        await conn.execute("""
            DELETE FROM api_call_logs
            WHERE analysis_id NOT IN (SELECT id FROM analyses)
        """)
        print(f"✓ Deleted {orphaned_api_count} orphaned API call logs")
    
    # Keep only latest 20 analyses per user
    await conn.execute("""
        DELETE FROM analyses
        WHERE id NOT IN (
            SELECT id FROM (
                SELECT id, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY uploaded_at DESC) as rn
                FROM analyses
            ) sub WHERE rn <= 20
        )
    """)
    print("✓ Kept only latest 20 analyses per user")
    
    await conn.close()


async def show_final_stats():
    """Show database stats after cleanup"""
    url = os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(url)
    
    print("\n" + "=" * 80)
    print("FINAL DATABASE STATISTICS")
    print("=" * 80)
    
    users = await conn.fetchval("SELECT COUNT(*) FROM users")
    analyses = await conn.fetchval("SELECT COUNT(*) FROM analyses")
    emissions = await conn.fetchval("SELECT COUNT(*) FROM emission_records")
    api_logs = await conn.fetchval("SELECT COUNT(*) FROM api_call_logs")
    
    print(f"\n  Users:            {users:6d}")
    print(f"  Analyses:         {analyses:6d}")
    print(f"  Emission Records: {emissions:6d}")
    print(f"  API Call Logs:    {api_logs:6d}")
    print("\n" + "=" * 80)
    
    await conn.close()


async def main():
    print("CarbonIQ Database Fix & Cleanup")
    print("=" * 80)
    print("\nThis will:")
    print("  1. Add user_id to analyses and emission_records tables")
    print("  2. Delete test users")
    print("  3. Delete orphaned records")
    print("  4. Keep only latest 20 analyses per user")
    print()
    
    confirm = input("Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Cancelled.")
        return
    
    await add_user_id_to_analyses()
    await cleanup_test_data()
    await cleanup_old_data()
    await show_final_stats()
    
    print("\n✓ Database cleanup complete!")


if __name__ == "__main__":
    asyncio.run(main())
