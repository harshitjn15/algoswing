import asyncio
import os
import sys

# Ensure we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import connect_db, close_db, watchlist_col
from app.core.scheduler import run_scanner_job

async def main():
    await connect_db()
    
    # 1. Clear existing 499 items
    res = await watchlist_col().delete_many({})
    print(f"🧹 Cleared {res.deleted_count} items from watchlists collection.")
    
    # 2. Force the scanner to run instantly
    print("🚀 Forcing scanner run now...")
    await run_scanner_job(force=True)
    
    await close_db()
    print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(main())
