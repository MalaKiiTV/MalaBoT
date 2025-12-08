"""
Quick debug script to check database state.
"""

import asyncio
import aiosqlite
import tempfile
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.models import DatabaseManager

async def debug_db():
    """Debug database state."""
    test_db_path = tempfile.mktemp(suffix='.db')
    db_manager = DatabaseManager(test_db_path)
    
    try:
        await db_manager.initialize()
        conn = await db_manager.get_connection()
        
        print("🔍 Database Schema Debug:")
        
        # Check user_xp table
        cursor = await conn.execute("PRAGMA table_info(user_xp)")
        columns = await cursor.fetchall()
        print("\n📋 user_xp table schema:")
        for col in columns:
            print(f"  {col[1]} {col[2]} {'PK' if col[5] else ''}")
        
        # Test XP operations
        user_id = 123456789
        guild1_id = 111111111
        guild2_id = 222222222
        
        print(f"\n🧪 Testing XP operations:")
        print(f"  User: {user_id}, Guild1: {guild1_id}, Guild2: {guild2_id}")
        
        # Set XP in guild 1
        await db_manager.set_user_xp(user_id, guild1_id, 1000)
        xp1 = await db_manager.get_user_xp(user_id, guild1_id)
        xp2 = await db_manager.get_user_xp(user_id, guild2_id)
        
        print(f"  XP in Guild 1 after setting 1000: {xp1}")
        print(f"  XP in Guild 2 before setting: {xp2}")
        
        # Set XP in guild 2
        await db_manager.set_user_xp(user_id, guild2_id, 500)
        xp1_updated = await db_manager.get_user_xp(user_id, guild1_id)
        xp2_updated = await db_manager.get_user_xp(user_id, guild2_id)
        
        print(f"  XP in Guild 1 after setting Guild 2: {xp1_updated}")
        print(f"  XP in Guild 2 after setting 500: {xp2_updated}")
        
        # Check what's actually in the database
        cursor = await conn.execute("SELECT user_id, guild_id, xp FROM user_xp ORDER BY guild_id")
        rows = await cursor.fetchall()
        print(f"\n📊 Raw data in user_xp table:")
        for row in rows:
            print(f"  User: {row[0]}, Guild: {row[1]}, XP: {row[2]}")
        
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
    asyncio.run(debug_db())