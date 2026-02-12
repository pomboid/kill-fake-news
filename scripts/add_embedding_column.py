import asyncio
import os
import sys

# Add parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.database import engine

async def add_column():
    try:
        async with engine.begin() as conn:
            print("Adding embedding column to article table...")
            # Use raw SQL to add the vector column
            await conn.execute(text("ALTER TABLE article ADD COLUMN IF NOT EXISTS embedding vector(768);"))
            print("Column added (or already exists).")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(add_column())
