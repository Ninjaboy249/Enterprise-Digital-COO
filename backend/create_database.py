"""
Script to create the PostgreSQL database
"""
import asyncio
import asyncpg
from config import settings

async def create_database():
    """Create the enterprise_coo database if it doesn't exist"""
    try:
        # Connect to the default 'postgres' database
        conn = await asyncpg.connect(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database='postgres'  # Connect to default database
        )
        
        # Check if database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            settings.POSTGRES_DB
        )
        
        if exists:
            print(f"[OK] Database '{settings.POSTGRES_DB}' already exists")
        else:
            # Create the database
            await conn.execute(f'CREATE DATABASE {settings.POSTGRES_DB}')
            print(f"[OK] Database '{settings.POSTGRES_DB}' created successfully")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        print(f"\nConnection details:")
        print(f"  Host: {settings.POSTGRES_HOST}")
        print(f"  Port: {settings.POSTGRES_PORT}")
        print(f"  User: {settings.POSTGRES_USER}")
        print(f"  Database: {settings.POSTGRES_DB}")
        return False

if __name__ == "__main__":
    success = asyncio.run(create_database())
    if success:
        print("\n[OK] You can now run: python main.py")
    else:
        print("\n[ERROR] Please check your PostgreSQL configuration")

# Made with Codex
