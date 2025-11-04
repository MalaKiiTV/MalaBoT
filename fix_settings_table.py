#!/usr/bin/env python3
"""
Simple script to create the missing settings table
"""

import asyncio
import aiosqlite
import os

async def create_settings_table():
    """Create the settings table directly"""
    
    db_path = "data/bot.db"
    
    print("🔧 Creating Settings Table")
    print(f"Database: {db_path}")
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    try:
        conn = await aiosqlite.connect(db_path)
        
        # Create settings table with correct schema
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                setting_key TEXT NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(guild_id, setting_key)
            )
        """)
        
        await conn.commit()
        
        # Verify the table was created
        cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
        table_exists = await cursor.fetchone()
        
        if table_exists:
            print("✅ Settings table created successfully!")
            
            # Show schema
            cursor = await conn.execute("PRAGMA table_info(settings)")
            columns = await cursor.fetchall()
            print(f"📋 Schema: {[col[1] for col in columns]}")
        else:
            print("❌ Failed to create settings table")
        
        await conn.close()
        print("🎉 Migration completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(create_settings_table())