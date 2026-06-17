import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import connect_db, close_db, watchlist_col

async def main():
    await connect_db()
    res = await watchlist_col().delete_many({})
    print(f"🧹 Cleared {res.deleted_count} items from watchlists collection.")
    await close_db()

if __name__ == "__main__":
    asyncio.run(main())
