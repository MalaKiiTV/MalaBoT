"""
Cleanup Old XP Keys
Removes old min_xp and max_xp keys from database
"""

import sqlite3

def cleanup_old_xp_keys(guild_id: int):
    """Remove old XP format keys"""
    
    try:
        conn = sqlite3.connect('data/bot.db')
        cursor = conn.cursor()
        
        print("=" * 80)
        print(f"CLEANING UP OLD XP KEYS FOR GUILD {guild_id}")
        print("=" * 80)
        print()
        
        # Keys to remove
        old_keys = [
            f"xp_min_{guild_id}",
            f"xp_max_{guild_id}",
            f"min_xp_{guild_id}",
            f"max_xp_{guild_id}"
        ]
        
        removed = []
        
        for key in old_keys:
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            result = cursor.fetchone()
            if result:
                cursor.execute("DELETE FROM settings WHERE key = ?", (key,))
                removed.append(f"{key} = {result[0]}")
                print(f"  ✅ Removed: {key} = {result[0]}")
        
        if not removed:
            print("  ℹ️ No old XP keys found")
        
        conn.commit()
        conn.close()
        
        print()
        print("=" * 80)
        print("✅ DONE! Old XP keys removed")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python cleanup_old_xp_keys.py <guild_id>")
        sys.exit(1)
    
    guild_id = int(sys.argv[1])
    cleanup_old_xp_keys(guild_id)