"""
Database models and schema definitions for MalaBoT.
Uses aiosqlite for async database operations.
"""

import aiosqlite
from typing import Optional, Any


class DatabaseManager:
    """Manages all database operations for MalaBoT."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None

    async def get_connection(self) -> aiosqlite.Connection:
        if self._connection is None:
            self._connection = await aiosqlite.connect(self.db_path)
        return self._connection

    async def initialize(self) -> None:
        conn = await self.get_connection()

        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                discriminator TEXT NOT NULL,
                display_name TEXT,
                avatar_url TEXT,
                joined_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_bot BOOLEAN DEFAULT FALSE,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                total_messages INTEGER DEFAULT 0,
                warning_count INTEGER DEFAULT 0,
                kick_count INTEGER DEFAULT 0,
                ban_count INTEGER DEFAULT 0,
                is_muted BOOLEAN DEFAULT FALSE,
                muted_until TIMESTAMP,
                mute_reason TEXT,
                reputation INTEGER DEFAULT 0,
                bio TEXT,
                birthday DATE,
                currency_balance INTEGER DEFAULT 0,
                last_daily TIMESTAMP,
                last_work TIMESTAMP,
                last_xp_gain TIMESTAMP,
                xp_multiplier REAL DEFAULT 1.0,
                custom_title TEXT,
                premium_expires TIMESTAMP,
                is_premium BOOLEAN DEFAULT FALSE
            )
            """
        )

        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS birthdays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                birthday DATE NOT NULL,
                timezone TEXT DEFAULT 'UTC',
                announced_year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """
        )

        await conn.commit()

    # === XP METHODS ===

    def calculate_level(self, xp: int) -> int:
        """Quadratic XP progression, compatible with xp.py."""
        level = 1
        while xp >= 10 * (level ** 2):
            level += 1
        return level

    async def get_user_xp(self, user_id: int) -> int:
        conn = await self.get_connection()
        await conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username, discriminator) VALUES (?, 'Unknown', '0')",
            (user_id,),
        )
        await conn.commit()
        cursor = await conn.execute("SELECT xp FROM users WHERE user_id = ?", (user_id,))
        result = await cursor.fetchone()
        return result[0] if result else 0

    async def set_user_xp(self, user_id: int, amount: int) -> tuple[int, int]:
        """Set user's XP and recalculate level."""
        conn = await self.get_connection()
        await conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username, discriminator) VALUES (?, 'Unknown', '0')",
            (user_id,),
        )
        new_xp = max(0, amount)
        level = self.calculate_level(new_xp)
        await conn.execute(
            "UPDATE users SET xp = ?, level = ? WHERE user_id = ?",
            (new_xp, level, user_id),
        )
        await conn.commit()
        return new_xp, level

    async def update_user_xp(self, user_id: int, xp_change: int) -> tuple[int, int]:
        """Update user's XP and recalculate level safely."""
        conn = await self.get_connection()
        await conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username, discriminator) VALUES (?, 'Unknown', '0')",
            (user_id,),
        )
        await conn.commit()
        cursor = await conn.execute("SELECT xp FROM users WHERE user_id = ?", (user_id,))
        result = await cursor.fetchone()
        current_xp = result[0] if result else 0
        new_xp = max(0, current_xp + xp_change)
        level = self.calculate_level(new_xp)
        await conn.execute(
            "UPDATE users SET xp = ?, level = ? WHERE user_id = ?",
            (new_xp, level, user_id),
        )
        await conn.commit()
        return new_xp, level

    async def remove_user_xp(self, user_id: int, amount: int) -> tuple[int, int]:
        return await self.update_user_xp(user_id, -amount)

    async def get_user_level(self, user_id: int) -> int:
        conn = await self.get_connection()
        cursor = await conn.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
        result = await cursor.fetchone()
        return result[0] if result else 1

    # === BIRTHDAY METHODS ===

    async def set_user_birthday(self, user_id: int, birthday: str) -> bool:
        try:
            conn = await self.get_connection()
            await conn.execute(
                "INSERT OR REPLACE INTO birthdays (user_id, birthday) VALUES (?, ?)",
                (user_id, birthday),
            )
            await conn.commit()
            return True
        except Exception:
            return False

    async def get_user_birthday(self, user_id: int) -> Optional[tuple]:
        conn = await self.get_connection()
        cursor = await conn.execute("SELECT birthday FROM birthdays WHERE user_id = ?", (user_id,))
        return await cursor.fetchone()

    # === CLEANUP ===

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()
            self._connection = None
