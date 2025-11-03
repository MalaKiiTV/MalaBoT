import sqlite3

def fix_settings():
    """Fix migrated settings by updating guild_id to the correct one."""
    db_path = 'data/bot.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Show current settings
        cursor.execute("SELECT guild_id, setting_key, value FROM settings ORDER BY guild_id")
        settings = cursor.fetchall()
        
        print("Current settings in database:")
        for guild_id, key, value in settings:
            print(f"  Guild {guild_id}: {key} = {value}")
        
        print(f"\nYour debug guild ID from logs: 542004156513255445")
        
        # Update all settings from guild_id=1 to the correct guild_id
        cursor.execute("""
            UPDATE settings 
            SET guild_id = ? 
            WHERE guild_id = 1
        """, (542004156513255445,))
        
        updated_count = cursor.rowcount
        conn.commit()
        
        print(f"\n✅ Updated {updated_count} settings to correct guild ID")
        
        # Show updated settings
        cursor.execute("SELECT guild_id, setting_key, value FROM settings ORDER BY guild_id")
        updated_settings = cursor.fetchall()
        
        print("\nUpdated settings:")
        for guild_id, key, value in updated_settings:
            print(f"  Guild {guild_id}: {key} = {value}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_settings()