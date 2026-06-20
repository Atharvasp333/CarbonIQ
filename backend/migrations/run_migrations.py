"""
Migration runner for Neon PostgreSQL database.
Safely applies schema migrations with rollback support.
"""
import os
import sys
import asyncio
import asyncpg
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger.info(f"Loaded environment from {env_path}")
else:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.warning(f"No .env file found at {env_path}")

MIGRATIONS_DIR = Path(__file__).parent


async def create_migrations_table(conn: asyncpg.Connection):
    """Create migrations tracking table if it doesn't exist."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id              SERIAL PRIMARY KEY,
            version         TEXT UNIQUE NOT NULL,
            name            TEXT NOT NULL,
            applied_at      TIMESTAMPTZ DEFAULT NOW(),
            execution_time  INTEGER, -- milliseconds
            status          TEXT DEFAULT 'completed', -- 'completed', 'failed', 'rolled_back'
            error_message   TEXT
        )
    """)
    logger.info("Migration tracking table ready")


async def get_applied_migrations(conn: asyncpg.Connection) -> set:
    """Get list of already applied migrations."""
    rows = await conn.fetch("""
        SELECT version FROM schema_migrations 
        WHERE status = 'completed'
        ORDER BY version
    """)
    return {row['version'] for row in rows}


async def apply_migration(conn: asyncpg.Connection, migration_file: Path) -> bool:
    """Apply a single migration file."""
    version = migration_file.stem
    name = migration_file.name
    
    logger.info(f"Applying migration: {name}")
    
    try:
        # Read migration SQL
        sql_content = migration_file.read_text()
        
        # Execute migration with timing
        start_time = datetime.now()
        await conn.execute(sql_content)
        end_time = datetime.now()
        execution_time = int((end_time - start_time).total_seconds() * 1000)
        
        # Record successful migration
        await conn.execute("""
            INSERT INTO schema_migrations (version, name, execution_time, status)
            VALUES ($1, $2, $3, 'completed')
            ON CONFLICT (version) DO UPDATE 
            SET status = 'completed', applied_at = NOW(), execution_time = $3
        """, version, name, execution_time)
        
        logger.info(f"✓ Migration {name} applied successfully ({execution_time}ms)")
        return True
        
    except Exception as e:
        logger.error(f"✗ Migration {name} failed: {str(e)}")
        
        # Record failed migration
        try:
            await conn.execute("""
                INSERT INTO schema_migrations (version, name, status, error_message)
                VALUES ($1, $2, 'failed', $3)
                ON CONFLICT (version) DO UPDATE 
                SET status = 'failed', error_message = $3, applied_at = NOW()
            """, version, name, str(e))
        except Exception as log_error:
            logger.error(f"Failed to log migration error: {log_error}")
        
        return False


async def run_migrations(database_url: str = None, dry_run: bool = False):
    """Run all pending migrations."""
    if database_url is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL not set in environment")
    
    logger.info("=" * 60)
    logger.info("Starting migration process")
    logger.info("=" * 60)
    
    if dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
    
    # Connect to database
    conn = await asyncpg.connect(database_url)
    
    try:
        # Create migrations tracking table
        await create_migrations_table(conn)
        
        # Get list of applied migrations
        applied = await get_applied_migrations(conn)
        logger.info(f"Already applied migrations: {len(applied)}")
        
        # Find all migration files
        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        if not migration_files:
            logger.info("No migration files found")
            return
        
        logger.info(f"Found {len(migration_files)} migration file(s)")
        
        # Apply pending migrations
        pending_count = 0
        success_count = 0
        
        for migration_file in migration_files:
            version = migration_file.stem
            
            if version in applied:
                logger.info(f"⊘ Skipping already applied: {migration_file.name}")
                continue
            
            pending_count += 1
            
            if dry_run:
                logger.info(f"→ Would apply: {migration_file.name}")
                success_count += 1
            else:
                success = await apply_migration(conn, migration_file)
                if success:
                    success_count += 1
                else:
                    logger.error(f"Migration failed, stopping at {migration_file.name}")
                    break
        
        # Summary
        logger.info("=" * 60)
        if pending_count == 0:
            logger.info("✓ All migrations already applied - database is up to date")
        else:
            logger.info(f"✓ Applied {success_count}/{pending_count} pending migration(s)")
        logger.info("=" * 60)
        
    finally:
        await conn.close()


async def list_migrations(database_url: str = None):
    """List all migrations and their status."""
    if database_url is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL not set in environment")
    
    conn = await asyncpg.connect(database_url)
    
    try:
        await create_migrations_table(conn)
        
        rows = await conn.fetch("""
            SELECT version, name, status, applied_at, execution_time 
            FROM schema_migrations 
            ORDER BY version
        """)
        
        print("\n" + "=" * 80)
        print("Applied Migrations")
        print("=" * 80)
        
        if not rows:
            print("No migrations applied yet")
        else:
            for row in rows:
                status_icon = "✓" if row['status'] == 'completed' else "✗"
                print(f"{status_icon} {row['version']}: {row['name']}")
                print(f"  Status: {row['status']}")
                print(f"  Applied: {row['applied_at']}")
                if row['execution_time']:
                    print(f"  Time: {row['execution_time']}ms")
                print()
        
        print("=" * 80 + "\n")
        
    finally:
        await conn.close()


async def rollback_migration(database_url: str = None, version: str = None):
    """Mark a migration as rolled back (manual rollback required)."""
    if database_url is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL not set in environment")
    
    if not version:
        logger.error("Version required for rollback")
        return
    
    conn = await asyncpg.connect(database_url)
    
    try:
        await conn.execute("""
            UPDATE schema_migrations 
            SET status = 'rolled_back' 
            WHERE version = $1
        """, version)
        
        logger.info(f"✓ Marked migration {version} as rolled back")
        logger.warning("Note: You must manually revert database changes")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration runner")
    parser.add_argument("command", choices=["migrate", "list", "rollback"], 
                       help="Command to execute")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be done without applying changes")
    parser.add_argument("--version", type=str, 
                       help="Migration version for rollback")
    parser.add_argument("--database-url", type=str, 
                       help="Database URL (overrides DATABASE_URL env var)")
    
    args = parser.parse_args()
    
    try:
        if args.command == "migrate":
            asyncio.run(run_migrations(args.database_url, args.dry_run))
        elif args.command == "list":
            asyncio.run(list_migrations(args.database_url))
        elif args.command == "rollback":
            if not args.version:
                print("Error: --version required for rollback")
                sys.exit(1)
            asyncio.run(rollback_migration(args.database_url, args.version))
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)
