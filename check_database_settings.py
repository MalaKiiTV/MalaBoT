"""
Database Settings Checker
Run this to see what's actually stored in your database
"""

import sqlite3
import json

def check_settings():
    """Check what settings are stored in the database"""
    
    try:
        conn = sqlite3.connect('data/bot.db')
        cursor = conn.cursor()
        
        # Get all settings
        cursor.execute("SELECT key, value FROM settings ORDER BY key")
        settings = cursor.fetchall()
        
        print("=" * 80)
        print("DATABASE SETTINGS CHECK")
        print("=" * 80)
        print()
        
        # Group by guild
        guild_settings = {}
        global_settings = []
        
        for key, value in settings:
            if '_' in key and key.split('_')[-1].isdigit():
                # Guild-specific setting
                parts = key.rsplit('_', 1)
                setting_name = parts[0]
                guild_id = parts[1]
                
                if guild_id not in guild_settings:
                    guild_settings[guild_id] = []
                
                guild_settings[guild_id].append((setting_name, value))
            else:
                # Global setting
                global_settings.append((key, value))
        
        # Print global settings
        if global_settings:
            print("GLOBAL SETTINGS:")
            print("-" * 80)
            for key, value in global_settings:
                print(f"  {key}: {value}")
            print()
        
        # Print guild-specific settings
        for guild_id, settings_list in guild_settings.items():
            print(f"GUILD {guild_id}:")
            print("-" * 80)
            
            # Group by category
            categories = {
                'verification': [],
                'welcome': [],
                'goodbye': [],
                'birthday': [],
                'xp': [],
                'role_connections': [],
                'general': []
            }
            
            for key, value in settings_list:
                if 'verify' in key or 'cheater' in key:
                    categories['verification'].append((key, value))
                elif 'welcome' in key:
                    categories['welcome'].append((key, value))
                elif 'goodbye' in key:
                    categories['goodbye'].append((key, value))
                elif 'birthday' in key:
                    categories['birthday'].append((key, value))
                elif 'xp' in key:
                    categories['xp'].append((key, value))
                elif 'role_connection' in key or 'protected_role' in key:
                    categories['role_connections'].append((key, value))
                else:
                    categories['general'].append((key, value))
            
            for category, items in categories.items():
                if items:
                    print(f"\n  {category.upper()}:")
                    for key, value in items:
                        # Try to pretty-print JSON
                        try:
                            if value and (value.startswith('[') or value.startswith('{')):
                                parsed = json.loads(value)
                                if isinstance(parsed, list):
                                    print(f"    {key}: {len(parsed)} items")
                                    if parsed and len(parsed) <= 3:
                                        for item in parsed:
                                            print(f"      - {item}")
                                else:
                                    print(f"    {key}: {value[:100]}...")
                            else:
                                print(f"    {key}: {value}")
                        except:
                            print(f"    {key}: {value}")
            print()
        
        conn.close()
        
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total settings: {len(settings)}")
        print(f"Global settings: {len(global_settings)}")
        print(f"Guilds with settings: {len(guild_settings)}")
        print()
        
        # Check for old format settings
        print("CHECKING FOR OLD FORMAT SETTINGS:")
        print("-" * 80)
        old_format_found = False
        
        for key, value in settings:
            # Check for old XP format (min_xp, max_xp)
            if 'min_xp' in key or 'max_xp' in key:
                print(f"  ⚠️ OLD XP FORMAT: {key} = {value}")
                old_format_found = True
            
            # Check for non-guild-specific welcome/goodbye
            if key in ['welcome_channel_id', 'welcome_message', 'welcome_title', 'welcome_image']:
                print(f"  ⚠️ OLD WELCOME FORMAT: {key} = {value}")
                old_format_found = True
            
            if key in ['goodbye_channel_id', 'goodbye_message', 'goodbye_title', 'goodbye_image']:
                print(f"  ⚠️ OLD GOODBYE FORMAT: {key} = {value}")
                old_format_found = True
        
        if not old_format_found:
            print("  ✅ No old format settings found")
        
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_settings()