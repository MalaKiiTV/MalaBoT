"""
Debug the schema test issue.
"""

import asyncio
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.models import DatabaseManager

async def debug_schema_test():
    test_db_path = tempfile.mktemp(suffix='.db')
    db_manager = DatabaseManager(test_db_path)
    
    try:
        await db_manager.initialize()
        conn = await db_manager.get_connection()
        
        # Reproduce the test logic
        table = 'user_xp'
        cursor = await conn.execute(f"PRAGMA table_info({table})")
        columns = await cursor.fetchall()
        
        print(f"Table {table} columns:")
        for col in columns:
            print(f"  {col[1]}: PK={col[5]}")
        
        has_user_id = any(col[1] == 'user_id' and col[5] == 1 for col in columns)
        has_guild_id = any(col[1] == 'guild_id' and col[5] == 1 for col in columns)
        
        print(f"\nHas user_id as PK: {has_user_id}")
        print(f"Has guild_id as PK: {has_guild_id}")
        print(f"Should pass: {has_user_id and has_guild_id}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db_manager.close()
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

if __name__ == "__main__":
    asyncio.run(debug_schema_test())