"""
Database migration verification utility
"""

import asyncio
import logging
from database.models import DatabaseManager

logger = logging.getLogger(__name__)

async def verify_migrations():
    """Verify all migrations have been applied"""
    try:
        db = DatabaseManager("data/bot.db")
        await db.initialize()
        
        # Check for migration table
        conn = await db.get_connection()
        cursor = await conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='migrations'
        """)
        
        if not await cursor.fetchone():
            # Create migrations table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await conn.commit()
            logger.info("Created migrations table")
        
        # List of migrations that should be applied
        required_migrations = [
            "add_component_to_health_logs",
            "migrate_appeals_table",
            "migrate_settings_table"
        ]
        
        # Check which are applied
        cursor = await conn.execute("SELECT name FROM migrations")
        applied = [row[0] for row in await cursor.fetchall()]
        
        missing = [m for m in required_migrations if m not in applied]
        if missing:
            logger.warning(f"Missing migrations: {missing}")
            return False
            
        logger.info("All migrations verified ✅")
        return True
        
    except Exception as e:
        logger.error(f"Migration check failed: {e}")
        return False
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(verify_migrations())