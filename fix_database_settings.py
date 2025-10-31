"""
Database Settings Fixer
Fixes old format settings and migrates to new guild-specific format
"""

import sqlite3
import json

def fix_settings(guild_id: int):
    """Fix settings for a specific guild"""
    
    try:
        conn = sqlite3.connect('data/bot.db')
        cursor = conn.cursor()
        
        print("=" * 80)
        print(f"FIXING SETTINGS FOR GUILD {guild_id}")
        print("=" * 80)
        print()
        
        fixes_applied = []
        
        # 1. Check for old XP format (min_xp, max_xp)
        cursor.execute("SELECT value FROM settings WHERE key = ?", (f"min_xp_{guild_id}",))
        min_xp = cursor.fetchone()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (f"max_xp_{guild_id}",))
        max_xp = cursor.fetchone()
        
        if min_xp or max_xp:
            print("⚠️ Found old XP format (min_xp/max_xp)")
            
            # Use average or default to 10
            if min_xp and max_xp:
                avg_xp = (int(min_xp[0]) + int(max_xp[0])) // 2
            elif min_xp:
                avg_xp = int(min_xp[0])
            elif max_xp:
                avg_xp = int(max_xp[0])
            else:
                avg_xp = 10
            
            # Set new format
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (f"xp_per_message_{guild_id}", str(avg_xp))
            )
            fixes_applied.append(f"Set xp_per_message_{guild_id} = {avg_xp}")
            
            # Delete old keys
            cursor.execute("DELETE FROM settings WHERE key = ?", (f"min_xp_{guild_id}",))
            cursor.execute("DELETE FROM settings WHERE key = ?", (f"max_xp_{guild_id}",))
            fixes_applied.append("Deleted old min_xp and max_xp keys")
        
        # 2. Check for non-guild-specific welcome settings
        old_welcome_keys = ['welcome_channel_id', 'welcome_message', 'welcome_title', 'welcome_image']
        for old_key in old_welcome_keys:
            cursor.execute("SELECT value FROM settings WHERE key = ?", (old_key,))
            result = cursor.fetchone()
            if result:
                new_key = f"{old_key.replace('_id', '')}_{guild_id}"
                if old_key == 'welcome_channel_id':
                    new_key = f"welcome_channel_{guild_id}"
                
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (new_key, result[0])
                )
                fixes_applied.append(f"Migrated {old_key} → {new_key}")
                
                # Delete old key
                cursor.execute("DELETE FROM settings WHERE key = ?", (old_key,))
        
        # 3. Check for non-guild-specific goodbye settings
        old_goodbye_keys = ['goodbye_channel_id', 'goodbye_message', 'goodbye_title', 'goodbye_image']
        for old_key in old_goodbye_keys:
            cursor.execute("SELECT value FROM settings WHERE key = ?", (old_key,))
            result = cursor.fetchone()
            if result:
                new_key = f"{old_key.replace('_id', '')}_{guild_id}"
                if old_key == 'goodbye_channel_id':
                    new_key = f"goodbye_channel_{guild_id}"
                
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (new_key, result[0])
                )
                fixes_applied.append(f"Migrated {old_key} → {new_key}")
                
                # Delete old key
                cursor.execute("DELETE FROM settings WHERE key = ?", (old_key,))
        
        # Commit changes
        conn.commit()
        
        print("FIXES APPLIED:")
        print("-" * 80)
        if fixes_applied:
            for fix in fixes_applied:
                print(f"  ✅ {fix}")
        else:
            print("  ℹ️ No fixes needed - all settings are in correct format")
        print()
        
        # Show current settings
        print("CURRENT SETTINGS:")
        print("-" * 80)
        cursor.execute(
            "SELECT key, value FROM settings WHERE key LIKE ? ORDER BY key",
            (f"%_{guild_id}",)
        )
        settings = cursor.fetchall()
        
        for key, value in settings:
            # Truncate long values
            display_value = value[:100] + "..." if value and len(value) > 100 else value
            print(f"  {key}: {display_value}")
        
        conn.close()
        
        print()
        print("=" * 80)
        print("✅ DONE! Restart your bot and run /setup → View Current Config")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python fix_database_settings.py <guild_id>")
        print()
        print("To find your guild ID:")
        print("1. Enable Developer Mode in Discord (Settings → Advanced)")
        print("2. Right-click your server name")
        print("3. Click 'Copy ID'")
        sys.exit(1)
    
    guild_id = int(sys.argv[1])
    fix_settings(guild_id)