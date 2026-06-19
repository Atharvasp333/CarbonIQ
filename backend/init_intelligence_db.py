"""
Initialize database with intelligence layer tables
Run this script to set up the organization_profile table
"""
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from database import init_db

async def main():
    print("Initializing database with intelligence layer tables...")
    try:
        await init_db()
        print("✅ Database initialized successfully!")
        print("✅ organization_profile table created")
        print("\nYou can now:")
        print("1. Start the backend: python -m uvicorn main:app --reload --port 8000")
        print("2. Configure organization profile in Settings page")
        print("3. Upload AWS CUR to see personalized recommendations")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print("\nPlease check:")
        print("1. DATABASE_URL is set in .env file")
        print("2. NeonDB is accessible")
        print("3. Connection string is valid")

if __name__ == "__main__":
    asyncio.run(main())
