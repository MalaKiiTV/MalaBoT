"""
Debug the XP test issue.
"""

import asyncio
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.models import DatabaseManager

async def debug_xp_test():
    test_db_path = tempfile.mktemp(suffix='.db')
    db_manager = DatabaseManager(test_db_path)
    
    try:
        await db_manager.initialize()
        
        user_id = 123456789
        guild1_id = 111111111
        guild2_id = 222222222
        
        print("🧪 Replicating XP test logic...")
        
        # Step 1: Set XP for user in guild 1
        print(f"1. Setting {user_id} XP to 1000 in guild {guild1_id}")
        await db_manager.set_user_xp(user_id, guild1_id, 1000)
        xp_guild1 = await db_manager.get_user_xp(user_id, guild1_id)
        print(f"   XP in guild 1: {xp_guild1}")
        
        # Step 2: Check that user has no XP in guild 2
        print(f"2. Checking XP for {user_id} in guild {guild2_id}")
        xp_guild2 = await db_manager.get_user_xp(user_id, guild2_id)
        print(f"   XP in guild 2: {xp_guild2}")
        
        # This is where the test fails - it expects 0 but gets 500
        if xp_guild2 != 0:
            print(f"❌ TEST ISSUE: Expected 0 XP in guild 2, got {xp_guild2}")
        
        # Let's check what's in the database
        conn = await db_manager.get_connection()
        cursor = await conn.execute("SELECT user_id, guild_id, xp FROM user_xp WHERE user_id = ?", (user_id,))
        rows = await cursor.fetchall()
        print(f"   Database state: {rows}")
        
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
    asyncio.run(debug_xp_test())