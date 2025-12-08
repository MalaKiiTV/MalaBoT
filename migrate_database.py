"""Database Migration Script"""
import aiosqlite
import asyncio
import os
import shutil
from datetime import datetime

async def migrate():
    db_path = "data/bot.db"
    
    # Backup
    if os.path.exists(db_path):
        backup = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(db_path, backup)
        print(f"Backup: {backup}")
    
    conn = await aiosqlite.connect(db_path)
    
    try:
        # Get existing tables
        cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in await cursor.fetchall()]
        
        if 'mod_logs' in tables:
            # Check columns
            cursor = await conn.execute("PRAGMA table_info(mod_logs)")
            columns = [row[1] for row in await cursor.fetchall()]
            
            if 'case_number' not in columns:
                print("Fixing mod_logs...")
                
                await conn.execute("""
                    CREATE TABLE mod_logs_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        case_number INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        moderator_id INTEGER NOT NULL,
                        action_type TEXT NOT NULL,
                        reason TEXT,
                        duration INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Copy data with case numbers
                cursor = await conn.execute("SELECT DISTINCT guild_id FROM mod_logs")
                guilds = [row[0] for row in await cursor.fetchall()]
                
                for guild_id in guilds:
                    cursor = await conn.execute(
                        "SELECT * FROM mod_logs WHERE guild_id = ? ORDER BY id",
                        (guild_id,)
                    )
                    rows = await cursor.fetchall()
                    
                    for idx, row in enumerate(rows, 1):
                        await conn.execute(
                            """INSERT INTO mod_logs_new 
                               (id, guild_id, case_number, user_id, moderator_id, action_type, reason, duration, created_at)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (row[0], row[1], idx, row[2], row[3], row[4], row[5], row[6], row[7])
                        )
                
                await conn.execute("DROP TABLE mod_logs")
                await conn.execute("ALTER TABLE mod_logs_new RENAME TO mod_logs")
                print("✅ Fixed mod_logs")
        
        await conn.commit()
        print("✅ Done!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

asyncio.run(migrate())
