#!/usr/bin/env python3
"""
Migration script to ensure settings table exists with correct schema
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import DatabaseManager


async def migrate_settings_table():
    """Create or update the settings table with correct schema"""

    # Use your database path
    db_path = "data/bot.db"

    print("🔧 Settings Table Migration")
    print(f"Database: {db_path}")

    try:
        # Initialize database
        db_manager = DatabaseManager(db_path)
        await db_manager.initialize()

        conn = await db_manager.get_connection()

        # Check if settings table exists
        cursor = await conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='settings'"
        )
        table_exists = await cursor.fetchone()

        if table_exists:
            print("✅ Settings table exists, checking schema...")

            # Check current schema
            cursor = await conn.execute("PRAGMA table_info(settings)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]

            print(f"Current columns: {column_names}")

            # Check if required columns exist
            required_columns = [
                "id",
                "guild_id",
                "key",
                "value",
                "created_at",
                "updated_at",
            ]
            missing_columns = [
                col for col in required_columns if col not in column_names
            ]

            if missing_columns:
                print(f"❌ Missing columns: {missing_columns}")
                print("🔄 Recreating settings table...")

                # Drop and recreate
                await conn.execute("DROP TABLE settings")
                await create_settings_table(conn)
                print("✅ Settings table recreated with correct schema")
            else:
                print("✅ Settings table schema is correct")

        else:
            print("❌ Settings table doesn't exist, creating it...")
            await create_settings_table(conn)
            print("✅ Settings table created successfully")

        await conn.commit()
        await db_manager.close()

        print("🎉 Migration completed successfully!")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise


async def create_settings_table(conn):
    """Create the settings table with correct schema"""
    await conn.execute(
        """
        CREATE TABLE settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(guild_id, key)
        )
    """
    )


if __name__ == "__main__":
    asyncio.run(migrate_settings_table())
