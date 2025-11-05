"""
Database models and management for MalaBoT.
"""
import aiosqlite
import math
from utils.logger import get_logger

logger = get_logger('database')

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    async def initialize(self):
        """Initializes the database connection and creates tables if they don't exist."""
        self.conn = await aiosqlite.connect(self.db_path)
        await self.create_tables()
        logger.info("Database initialized successfully")

    async def get_connection(self):
        """Returns the database connection."""
        if not self.conn:
            await self.initialize()
        return self.conn

    async def create_tables(self):
        """Creates all necessary tables for the bot."""
        async with self.conn.cursor() as cursor:
            # User XP and Levels
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL UNIQUE,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 0
                )
            """)
            # Guild Settings
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY,
                    guild_id INTEGER NOT NULL,
                    setting_name TEXT NOT NULL,
                    setting_value TEXT,
                    UNIQUE(guild_id, setting_name)
                )
            """)
            # Birthdays
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS birthdays (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL UNIQUE,
                    birthday TEXT NOT NULL,
                    year TEXT,
                    timezone TEXT DEFAULT 'UTC',
                    announced_year INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Verifications
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS verifications (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    verification_type TEXT NOT NULL,
                    status TEXT DEFAULT 'pending', -- pending, verified, rejected, cheater
                    data TEXT, -- JSON for activision_id, platform, etc.
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reviewed_by INTEGER,
                    reviewed_at TIMESTAMP,
                    notes TEXT
                )
            """)
            # Appeals
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS appeals (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    appeal_text TEXT NOT NULL,
                    status TEXT DEFAULT 'pending', -- pending, approved, denied
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reviewed_by INTEGER,
                    reviewed_at TIMESTAMP,
                    review_notes TEXT
                )
            """)
            # Event Logs
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS event_logs (
                    id INTEGER PRIMARY KEY,
                    category TEXT NOT NULL,
                    action TEXT NOT NULL,
                    user_id INTEGER,
                    target_id INTEGER,
                    guild_id INTEGER,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        await self.conn.commit()
        logger.info("All tables created or verified.")

    # --- XP and Level Methods ---

    def _calculate_level(self, xp: int) -> int:
        """Calculates level based on XP."""
        if xp < 0: return 0
        return math.floor(0.1 * math.sqrt(xp))

    async def get_user_data(self, user_id: int):
        """Gets all data for a user."""
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            return await cursor.fetchone()

    async def update_user_xp(self, user_id: int, xp_to_add: int):
        """Adds XP to a user and updates their level accordingly."""
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT xp FROM users WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()
            
            current_xp = 0
            if result:
                current_xp = result[0]
            
            new_xp = current_xp + xp_to_add
            new_level = self._calculate_level(new_xp)
            
            await cursor.execute(
                "INSERT OR REPLACE INTO users (user_id, xp, level) VALUES (?, ?, ?)",
                (user_id, new_xp, new_level)
            )
        await self.conn.commit()

    async def set_user_xp(self, user_id: int, xp: int):
        """Sets a user's XP and recalculates their level."""
        level = self._calculate_level(xp)
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "INSERT OR REPLACE INTO users (user_id, xp, level) VALUES (?, ?, ?)",
                (user_id, xp, level)
            )
        await self.conn.commit()
        
    async def get_user_xp(self, user_id: int) -> int:
        """Gets a user's XP."""
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT xp FROM users WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def get_user_level(self, user_id: int) -> int:
        """Gets a user's level."""
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()
            return result[0] if result else 0
            
    async def get_leaderboard(self, limit: int = 10):
        """Gets the top users by XP for the leaderboard."""
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT user_id, xp, level FROM users ORDER BY xp DESC LIMIT ?", (limit,))
            return await cursor.fetchall()

    # --- Birthday Methods ---
    
    async def set_birthday(self, user_id: int, birthday: str, year: str = None):
        """Sets a user's birthday."""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "INSERT OR REPLACE INTO birthdays (user_id, birthday, year) VALUES (?, ?, ?)",
                (user_id, birthday, year)
            )
        await self.conn.commit()

    async def get_birthday(self, user_id: int):
        """Gets a user's birthday."""
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM birthdays WHERE user_id = ?", (user_id,))
            return await cursor.fetchone()

    async def get_all_birthdays(self):
        """Gets all birthdays from the database."""
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM birthdays")
            return await cursor.fetchall()
            
    # --- Settings Methods ---

    async def set_setting(self, guild_id: int, setting_name: str, setting_value: str):
        """Sets a configuration setting for a guild."""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "INSERT OR REPLACE INTO settings (guild_id, setting_name, setting_value) VALUES (?, ?, ?)",
                (guild_id, setting_name, setting_value)
            )
        await self.conn.commit()

    async def get_setting(self, setting_name: str, guild_id: int) -> str:
        """Gets a configuration setting for a guild."""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT setting_value FROM settings WHERE guild_id = ? AND setting_name = ?",
                (guild_id, setting_name)
            )
            result = await cursor.fetchone()
            return result[0] if result else None
            
    # --- Event Log Methods ---
    
    async def log_event(self, category: str, action: str, user_id: int = None, target_id: int = None, guild_id: int = None, details: str = None):
        """Logs an event to the database."""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO event_logs (category, action, user_id, target_id, guild_id, details) VALUES (?, ?, ?, ?, ?, ?)",
                (category, action, user_id, target_id, guild_id, details)
            )
        await self.conn.commit()