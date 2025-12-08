"""
Check database schema.
"""

import asyncio
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.models import DatabaseManager

async def check_schema():
    test_db_path = tempfile.mktemp(suffix='.db')
    db_manager = DatabaseManager(test_db_path)
    await db_manager.initialize()
    conn = await db_manager.get_connection()
    
    cursor = await conn.execute('PRAGMA table_info(user_xp)')
    columns = await cursor.fetchall()
    print('user_xp columns:')
    for col in columns:
        print(f'  {col[1]} PK={col[5]} NOTNULL={col[3]} DEFAULT={col[4]}')
    
    cursor = await conn.execute('SELECT sql FROM sqlite_master WHERE type="table" AND name="user_xp"')
    create_sql = await cursor.fetchone()
    print(f'\nCreate SQL: {create_sql[0]}')
    
    await conn.close()
    await db_manager.close()
    os.remove(test_db_path)

if __name__ == "__main__":
    asyncio.run(check_schema())