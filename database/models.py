"""
Database models and schema definitions for MalaBoT.
Uses aiosqlite for async database operations.
"""

import sqlite3
import aiosqlite
from datetime import datetime
from typing import Optional, Dict, Any, List
import json

class DatabaseManager:
    """Manages all database operations for MalaBoT."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection = None
    
    async def get_connection(self):
        """Get database connection."""
        if self._connection is None:
            self._connection = await aiosqlite.connect(self.db_path)
        return self._connection
    
    async def initialize(self):
        """Initialize database and create all tables."""
        conn = await self.get_connection()
        
        # Users table
        await conn.execute("""
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
        """)
        
        # Birthdays table
        await conn.execute("""
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
        """)
        
        # Settings table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                setting_key TEXT NOT NULL,
                setting_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(guild_id, setting_key)
            )
        """)
        
        # Mod logs table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS mod_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                reason TEXT,
                duration INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (moderator_id) REFERENCES users(user_id)
            )
        """)
        
        # Roast XP table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS roast_xp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                base_xp INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Roast log table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS roast_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                target_id INTEGER,
                action TEXT NOT NULL,
                xp_gained INTEGER,
                message_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Audit log table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Health logs table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS health_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpu_usage REAL NOT NULL,
                memory_usage REAL NOT NULL,
                disk_usage REAL NOT NULL,
                uptime INTEGER NOT NULL,
                guild_count INTEGER NOT NULL,
                user_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # System flags table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS system_flags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flag_name TEXT NOT NULL UNIQUE,
                flag_value BOOLEAN NOT NULL DEFAULT FALSE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Verifications table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                verification_type TEXT NOT NULL,
                status TEXT NOT NULL,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Appeals table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS appeals (
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
        """)
        
        # Level roles table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS level_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                level INTEGER NOT NULL,
                role_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(guild_id, level)
            )
        """)
        
        await conn.commit()
        
        # Initialize roast_xp if not exists
        await self._initialize_roast_xp()
    
    async def _initialize_roast_xp(self):
        """Initialize roast XP table with default values."""
        conn = await self.get_connection()
        cursor = await conn.execute("SELECT COUNT(*) FROM roast_xp")
        count = (await cursor.fetchone())[0]
        
        if count == 0:
            await conn.execute("""
                INSERT INTO roast_xp (action, base_xp) VALUES
                    ('roast_success', 15),
                    ('roast_fail', 5),
                    ('defend_success', 10),
                    ('defend_fail', 3),
                    ('compliment', 8)
            """)
            await conn.commit()
    
    # Add missing methods that the bot needs
    
    async def add_user_xp(self, user_id: int, xp_gained: int) -> int:
        """Add XP to a user and return their new total."""
        await self.update_user_xp(user_id, xp_gained)
        return await self.get_user_xp(user_id)
    
    async def get_user_xp(self, user_id: int) -> int:
        """Get user's current XP."""
        conn = await self.get_connection()
        cursor = await conn.execute("SELECT xp FROM users WHERE user_id = ?", (user_id,))
        result = await cursor.fetchone()
        return result[0] if result else 0
    
    async def update_user_xp(self, user_id: int, xp_change: int):
        """Update user's XP."""
        conn = await self.get_connection()
        await conn.execute(
            "UPDATE users SET xp = xp + ?, last_xp_gain = CURRENT_TIMESTAMP WHERE user_id = ?",
            (xp_change, user_id)
        )
        await conn.commit()
    
    async def get_user(self, user_id: int):
        """Get user data."""
        conn = await self.get_connection()
        cursor = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cursor.fetchone()
    
    async def close(self):
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
