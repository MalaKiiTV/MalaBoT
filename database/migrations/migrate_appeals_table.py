#!/usr/bin/env python3
"""
Migration script to remove UNIQUE constraint from appeals table.
This allows users to submit multiple appeals across different jail sessions.
"""

import asyncio
import os

import aiosqlite


async def migrate_appeals_table():
    """Remove UNIQUE constraint from appeals table"""
    db_path = "data/bot.db"

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    print("Starting appeals table migration...")

    async with aiosqlite.connect(db_path) as conn:
        # Check if the table exists
        cursor = await conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='appeals'"
        )
        if not await cursor.fetchone():
            print("Appeals table doesn't exist yet. No migration needed.")
            return

        # Get current data
        cursor = await conn.execute("SELECT * FROM appeals")
        appeals_data = await cursor.fetchall()

        # Get column names
        cursor = await conn.execute("PRAGMA table_info(appeals)")
        columns = await cursor.fetchall()
        column_names = [col[1] for col in columns]

        print(f"Found {len(appeals_data)} existing appeals")

        # Drop the old table
        await conn.execute("DROP TABLE IF EXISTS appeals")

        # Create new table without UNIQUE constraint
        await conn.execute(
            """
            CREATE TABLE appeals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                appeal_text TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_by INTEGER DEFAULT NULL,
                reviewed_at TIMESTAMP DEFAULT NULL,
                review_notes TEXT DEFAULT NULL
            )
        """
        )

        # Re-insert data
        if appeals_data:
            placeholders = ",".join(["?" for _ in column_names])
            await conn.executemany(
                f"INSERT INTO appeals ({','.join(column_names)}) VALUES ({placeholders})",
                appeals_data,
            )

        await conn.commit()
        print(f"✅ Migration complete! Re-inserted {len(appeals_data)} appeals")
        print("Users can now submit new appeals after leaving and rejoining.")


if __name__ == "__main__":
    asyncio.run(migrate_appeals_table())
