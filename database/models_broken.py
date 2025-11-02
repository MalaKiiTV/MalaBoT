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
    
    async def initialize(self):
        """Initialize database and create all tables."""
        await self._create_tables()
        await self._verify_integrity()
    
    async def get_connection(self) -> aiosqlite.Connection:
        """Get database connection (creates if needed)."""
        if self._connection is None:
            self._connection = await aiosqlite.connect(self.db_path)
            await self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection
    
    async def close(self):
        """Close database connection and clean up."""
        if self._connection:
            try:
                # Commit any pending transactions
                await self._connection.commit()
                # Close the connection
                await self._connection.close()
                self._connection = None
                print("[DatabaseManager] Database connection closed successfully")
            except Exception as e:
                print(f"[DatabaseManager] Error closing database connection: {e}")
                self._connection = None
    
    async def _create_tables(self):
        """Create all necessary database tables."""
        conn = await self.get_connection()
        
        # Users table for XP system
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                last_message TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                daily_streak INTEGER DEFAULT 0,
                last_daily_award_date DATE DEFAULT NULL,
                total_messages INTEGER DEFAULT 0
            )
        """)
        
        # Birthdays table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS birthdays (
                user_id INTEGER PRIMARY KEY,
                birthday TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_celebrated DATE DEFAULT NULL
            )
        """)
        
        # Settings table for server configuration
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Moderation logs table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS mod_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                moderator_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                channel_id INTEGER,
                message_count INTEGER DEFAULT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Roast XP table (bot progression)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS roast_xp (
                id INTEGER PRIMARY KEY,
                bot_level INTEGER DEFAULT 1,
                current_xp INTEGER DEFAULT 0,
                next_level_xp INTEGER DEFAULT 50,
                total_roasts_received INTEGER DEFAULT 0,
                final_title_override TEXT DEFAULT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Roast log table (users who roasted the bot)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS roast_log (
                user_id INTEGER PRIMARY KEY,
                times_roasted INTEGER DEFAULT 0,
                last_roast TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                funniest_roast TEXT DEFAULT NULL
            )
        """)
        
        # Audit log table for comprehensive event tracking
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                category TEXT NOT NULL,
                action TEXT NOT NULL,
                user_id INTEGER DEFAULT NULL,
                target_id INTEGER DEFAULT NULL,
                channel_id INTEGER DEFAULT NULL,
                details TEXT,
                guild_id INTEGER DEFAULT NULL
            )
        """)
        
        # Health monitor logs
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS health_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                check_type TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                value REAL DEFAULT NULL
            )
        """)
        
        # System flags for crash detection
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS system_flags (
                flag_name TEXT PRIMARY KEY,
                flag_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
                # Verification table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id INTEGER NOT NULL,
                activision_id TEXT NOT NULL,
                platform TEXT,
                screenshot_url TEXT,
                status TEXT DEFAULT 'pending',
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_by INTEGER DEFAULT NULL,
                reviewed_at TIMESTAMP DEFAULT NULL,
                notes TEXT DEFAULT NULL
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
                INSERT INTO roast_xp (bot_level, current_xp, next_level_xp, total_roasts_received)
                VALUES (1, 0, 50, 0)
            """)
            await conn.commit()
    
    async def _verify_integrity(self):
        """Verify database integrity and fix if needed."""
        try:
            conn = await self.get_connection()
            await conn.execute("SELECT 1")
            await conn.commit()
        except sqlite3.DatabaseError as e:
            raise Exception(f"Database integrity check failed: {e}")
    
    # User XP Methods
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data from database."""
        conn = await self.get_connection()
        cursor = await conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    
    async def create_user(self, user_id: int) -> Dict[str, Any]:
        """Create new user entry."""
        conn = await self.get_connection()
        await conn.execute("""
            INSERT INTO users (user_id, xp, level, last_message, daily_streak, total_messages)
            VALUES (?, 0, 1, CURRENT_TIMESTAMP, 0, 0)
        """, (user_id,))
        await conn.commit()
        return await self.get_user(user_id)
    
    async def update_user_xp(self, user_id: int, xp_gained: int) -> Dict[str, Any]:
        """Update user XP and calculate new level."""
        from config.constants import XP_TABLE
        
        user = await self.get_user(user_id)
        if not user:
            user = await self.create_user(user_id)
        
        new_xp = user['xp'] + xp_gained
        
        # Calculate new level
        new_level = user['level']
        for level, xp_required in sorted(XP_TABLE.items()):
            if new_xp >= xp_required:
                new_level = level
            else:
                break
        
        conn = await self.get_connection()
        await conn.execute("""
            UPDATE users 
            SET xp = ?, level = ?, last_message = CURRENT_TIMESTAMP, total_messages = total_messages + 1
            WHERE user_id = ?
        """, (new_xp, new_level, user_id))
        await conn.commit()
        
        return await self.get_user(user_id)
    
    async def add_user_xp(self, user_id: int, xp_gained: int) -> int:
        """Add XP to a user and return their new total."""
        await self.update_user_xp(user_id, xp_gained)
        return await self.get_user_xp(user_id)

    async def reset_user_xp(self, user_id: int):
        """Reset user's XP and level."""
        conn = await self.get_connection()
        await conn.execute("""
            UPDATE users 
            SET xp = 0, level = 1, daily_streak = 0, last_daily_award_date = NULL
            WHERE user_id = ?
        """, (user_id,))
        await conn.commit()
    
    async def get_user_xp(self, user_id: int) -> int:
        """Get user's current XP."""
        user = await self.get_user(user_id)
        return user['xp'] if user else 0
    
    async def get_user_level(self, user_id: int) -> int:
        """Get user's current level."""
        user = await self.get_user(user_id)
        return user['level'] if user else 1
    
    async def set_user_xp(self, user_id: int, xp: int):
        """Set user's XP to a specific amount."""
        from config.constants import XP_TABLE
        
        # Calculate level based on XP
        new_level = 1
        for level, xp_required in sorted(XP_TABLE.items()):
            if xp >= xp_required:
                new_level = level
            else:
                break
        
        conn = await self.get_connection()
        await conn.execute("""
            UPDATE users 
            SET xp = ?, level = ?
            WHERE user_id = ?
        """, (xp, new_level, user_id))
        await conn.commit()
    
    async def get_user_last_daily(self, user_id: int) -> str:
        """Get user's last daily claim timestamp."""
        user = await self.get_user(user_id)
        return user['last_daily_award_date'] if user else None
    
    async def update_user_last_daily(self, user_id: int, timestamp: str):
        """Update user's last daily claim timestamp."""
        conn = await self.get_connection()
        await conn.execute("""
            UPDATE users 
            SET last_daily_award_date = ?
            WHERE user_id = ?
        """, (timestamp, user_id))
        await conn.commit()
    
    async def get_user_streak(self, user_id: int) -> int:
        """Get user's daily streak."""
        user = await self.get_user(user_id)
        return user['daily_streak'] if user else 0
    
    async def update_user_streak(self, user_id: int, streak: int):
        """Update user's daily streak."""
        conn = await self.get_connection()
        await conn.execute("""
            UPDATE users 
            SET daily_streak = ?
            WHERE user_id = ?
        """, (streak, user_id))
        await conn.commit()
    
    # Birthday Methods
    async def set_birthday(self, user_id: int, birthday: str) -> bool:
        """Set user's birthday."""
        conn = await self.get_connection()
        await conn.execute("""
            INSERT OR REPLACE INTO birthdays (user_id, birthday, created_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (user_id, birthday))
        await conn.commit()
        return True
    
    async def get_birthday(self, user_id: int) -> Optional[str]:
        """Get user's birthday."""
        conn = await self.get_connection()
        cursor = await conn.execute(
            "SELECT birthday FROM birthdays WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None
    
    async def get_all_birthdays(self) -> List[Dict[str, Any]]:
        """Get all birthdays ordered by next upcoming."""
        conn = await self.get_connection()
        cursor = await conn.execute("""
            SELECT user_id, birthday FROM birthdays 
            ORDER BY birthday
        """)
        rows = await cursor.fetchall()
        return [{'user_id': row[0], 'birthday': row[1]} for row in rows]
    
    async def get_today_birthdays(self) -> List[int]:
        """Get list of user IDs with birthdays today."""
        from datetime import datetime
        today = datetime.now().strftime("%m-%d")
        
        conn = await self.get_connection()
        cursor = await conn.execute(
            "SELECT user_id FROM birthdays WHERE birthday = ?", (today,)
        )
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
    
    # Settings Methods
    async def get_setting(self, key: str, default_value: Any = None) -> Any:
        """Get setting value."""
        conn = await self.get_connection()
        cursor = await conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        )
        row = await cursor.fetchone()
        if row:
            # Try to parse as JSON for complex values
            try:
                return json.loads(row[0])
            except:
                return row[0]
        return default_value
    
    async def set_setting(self, key: str, value: Any):
        """Set setting value."""
        conn = await self.get_connection()
        # Convert to JSON string for complex values
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        await conn.execute("""
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value))
        await conn.commit()
    
    # Moderation Methods
    async def log_moderation_action(self, moderator_id: int, action: str, 
                                  channel_id: int, message_count: int = None, 
                                  details: str = None):
        """Log a moderation action."""
        conn = await self.get_connection()
        await conn.execute("""
            INSERT INTO mod_logs (moderator_id, action, channel_id, message_count, details)
            VALUES (?, ?, ?, ?, ?)
        """, (moderator_id, action, channel_id, message_count, details))
        await conn.commit()
    
    async def get_recent_moderation_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent moderation logs."""
        conn = await self.get_connection()
        cursor = await conn.execute("""
            SELECT * FROM mod_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        rows = await cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    # Roast XP Methods
    async def get_roast_xp(self) -> Dict[str, Any]:
        """Get bot's current roast XP data."""
        conn = await self.get_connection()
        cursor = await conn.execute("SELECT * FROM roast_xp WHERE id = 1")
        row = await cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    
    async def add_roast_xp(self, xp_gained: int) -> Dict[str, Any]:
        """Add XP to bot's roast level."""
        from config.constants import ROAST_XP_TABLE
        
        current = await self.get_roast_xp()
        if not current:
            return None
        
        new_xp = current['current_xp'] + xp_gained
        new_level = current['bot_level']
        
        # Calculate new level
        for level, xp_required in sorted(ROAST_XP_TABLE.items()):
            if new_xp >= xp_required:
                new_level = level
            else:
                break
        
        # Get next level XP requirement
        next_level_xp = ROAST_XP_TABLE.get(new_level + 1, new_xp + 100)
        
        conn = await self.get_connection()
        await conn.execute("""
            UPDATE roast_xp 
            SET bot_level = ?, current_xp = ?, next_level_xp = ?, 
                total_roasts_received = total_roasts_received + 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """, (new_level, new_xp, next_level_xp))
        await conn.commit()
        
        return await self.get_roast_xp()
    
    async def reset_roast_xp(self):
        """Reset bot's roast XP and level."""
        conn = await self.get_connection()
        await conn.execute("""
            UPDATE roast_xp 
            SET bot_level = 1, current_xp = 0, next_level_xp = 50, 
                total_roasts_received = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """)
        await conn.commit()
    
    async def log_roast_user(self, user_id: int):
        """Log that a user roasted the bot."""
        conn = await self.get_connection()
        
        # Check if user exists in roast_log
        cursor = await conn.execute(
            "SELECT times_roasted FROM roast_log WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            await conn.execute("""
                UPDATE roast_log 
                SET times_roasted = times_roasted + 1, last_roast = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (user_id,))
        else:
            await conn.execute("""
                INSERT INTO roast_log (user_id, times_roasted, last_roast)
                VALUES (?, 1, CURRENT_TIMESTAMP)
            """, (user_id,))
        
        await conn.commit()
    
    async def get_roast_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get roast leaderboard (users who roasted bot most)."""
        conn = await self.get_connection()
        cursor = await conn.execute("""
            SELECT user_id, times_roasted, last_roast 
            FROM roast_log 
            ORDER BY times_roasted DESC 
            LIMIT ?
        """, (limit,))
        rows = await cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    # Audit Log Methods
    async def get_leaderboard(self, guild_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get XP leaderboard for a guild."""
        conn = await self.get_connection()
        cursor = await conn.execute("""
            SELECT user_id, xp, level, total_messages
            FROM users
            ORDER BY xp DESC
            LIMIT ?
        """, (limit,))
        
        rows = await cursor.fetchall()
        return [
            {
                'user_id': row[0],
                'xp': row[1],
                'level': row[2],
                'total_messages': row[3]
            }
            for row in rows
        ]
    
    async def get_user_rank(self, user_id: int, guild_id: int) -> Optional[int]:
        """Get user's rank in the server based on XP."""
        conn = await self.get_connection()
        
        # Get all users ordered by XP
        cursor = await conn.execute("""
            SELECT user_id, xp
            FROM users
            ORDER BY xp DESC
        """)
        
        rows = await cursor.fetchall()
        
        # Find user's position
        for rank, (uid, xp) in enumerate(rows, start=1):
            if uid == user_id:
                return rank
        
        return None

    async def set_daily_claimed(self, user_id: int, guild_id: int):
        """Mark daily reward as claimed for a user."""
        from datetime import date
        conn = await self.get_connection()
        
        # Get current user data
        cursor = await conn.execute("""
            SELECT daily_streak, last_daily_award_date
            FROM users
            WHERE user_id = ?
        """, (user_id,))
        
        row = await cursor.fetchone()
        
        if row:
            current_streak = row[0] or 0
            last_daily = row[1]
            
            # Check if claimed today
            today = date.today().isoformat()
            if last_daily == today:
                return  # Already claimed today
            
            # Update streak
            new_streak = current_streak + 1
            
            await conn.execute("""
                UPDATE users
                SET daily_streak = ?,
                    last_daily_award_date = ?
                WHERE user_id = ?
            """, (new_streak, today, user_id))
        else:
            # Create new user entry
            today = date.today().isoformat()
            await conn.execute("""
                INSERT INTO users (user_id, daily_streak, last_daily_award_date)
                VALUES (?, 1, ?)
            """, (user_id, today))
        
        await conn.commit()


    async def increment_daily_streak(self, user_id: int, guild_id: int) -> int:
        """Increment and return the user's daily streak."""
        from datetime import date, timedelta
        conn = await self.get_connection()
        
        # Get current user data
        cursor = await conn.execute("""
            SELECT daily_streak, last_daily_award_date
            FROM users
            WHERE user_id = ?
        """, (user_id,))
        
        row = await cursor.fetchone()
        
        if row:
            current_streak = row[0] or 0
            last_daily = row[1]
            
            # Check if streak should continue
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            if last_daily:
                last_date = date.fromisoformat(last_daily)
                if last_date == yesterday:
                    # Streak continues
                    new_streak = current_streak + 1
                elif last_date == today:
                    # Already claimed today
                    new_streak = current_streak
                else:
                    # Streak broken
                    new_streak = 1
            else:
                new_streak = 1
            
            await conn.execute("""
                UPDATE users
                SET daily_streak = ?
                WHERE user_id = ?
            """, (new_streak, user_id))
            await conn.commit()
            
            return new_streak
        else:
            return 1

    async def log_event(self, category: str, action: str, user_id: int = None,
                       target_id: int = None, channel_id: int = None,
                       details: str = None, guild_id: int = None):
        """Log an event to the audit log."""
        conn = await self.get_connection()
        await conn.execute("""
            INSERT INTO audit_log (category, action, user_id, target_id, channel_id, details, guild_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (category, action, user_id, target_id, channel_id, details, guild_id))
        await conn.commit()
    
    async def get_audit_logs(self, limit: int = 20, category: str = None) -> List[Dict[str, Any]]:
        """Get audit logs with optional category filter."""
        conn = await self.get_connection()
        
        if category:
            cursor = await conn.execute("""
                SELECT * FROM audit_log 
                WHERE category = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (category, limit))
        else:
            cursor = await conn.execute("""
                SELECT * FROM audit_log 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
        
        rows = await cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    async def cleanup_old_audit_logs(self, days: int = 90):
        """Clean up audit logs older than specified days."""
        conn = await self.get_connection()
        await conn.execute("""
            DELETE FROM audit_log 
            WHERE timestamp < datetime('now', '-{} days')
        """.format(days))
        await conn.commit()
    
    # System Flags Methods
    async def set_flag(self, flag_name: str, flag_value: str):
        """Set a system flag."""
        conn = await self.get_connection()
        await conn.execute("""
            INSERT OR REPLACE INTO system_flags (flag_name, flag_value, created_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (flag_name, flag_value))
        await conn.commit()
    
    async def get_flag(self, flag_name: str) -> Optional[str]:
        """Get a system flag value."""
        conn = await self.get_connection()
        cursor = await conn.execute(
            "SELECT flag_value FROM system_flags WHERE flag_name = ?", (flag_name,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None
    
    async def clear_flag(self, flag_name: str):
        """Clear a system flag."""
        conn = await self.get_connection()
        await conn.execute(
            "DELETE FROM system_flags WHERE flag_name = ?", (flag_name,)
        )
        await conn.commit()
    
    # Health Monitor Methods
    async def log_health_check(self, check_type: str, status: str, 
                             details: str = None, value: float = None):
        """Log a health check result."""
        conn = await self.get_connection()
        await conn.execute("""
            INSERT INTO health_logs (check_type, status, details, value)
            VALUES (?, ?, ?, ?)
        """, (check_type, status, details, value))
        
        await conn.commit()
    
    async def get_recent_health_logs(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent health logs."""
        conn = await self.get_connection()
        cursor = await conn.execute("""
            SELECT * FROM health_logs 
            WHERE timestamp > datetime('now', '-{} hours')
            ORDER BY timestamp DESC
        """.format(hours))
        rows = await cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]