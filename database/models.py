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
        """Get or create database connection with proper error handling."""
        if self._connection is None:
            try:
                self._connection = await aiosqlite.connect(
                    self.db_path,
                    timeout=30.0
                )
                # Enable foreign keys
                await self._connection.execute("PRAGMA foreign_keys = ON")
                # Set journal mode for better concurrency
                await self._connection.execute("PRAGMA journal_mode = WAL")
                await self._connection.commit()
            except Exception as e:
                print(f"❌ Failed to connect to database: {e}")
                raise
        return self._connection

    async def initialize(self) -> None:
        """Initialize database and create all tables."""
        conn = await self.get_connection()

        # Users table (removed xp and level - now in user_xp table)
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

        # User XP table
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_xp (
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 0,
                last_message_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, guild_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """
        )

        # Birthdays table
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS birthdays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                birthday DATE NOT NULL,
                timezone TEXT DEFAULT 'UTC',
                announced_year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, guild_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """
        )

        # Settings table
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                setting_key TEXT NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(guild_id, setting_key)
            )
        """
        )

        # Mod logs table
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mod_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER,
                moderator_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                reason TEXT,
                duration INTEGER,
                channel_id INTEGER,
                message_count INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Roast XP table
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS roast_xp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                base_xp INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Roast log table (PER-GUILD SYSTEM)
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS roast_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                target_id INTEGER,
                action TEXT NOT NULL,
                xp_gained INTEGER,
                message_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """
        )

        # Audit log table
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                category TEXT NOT NULL,
                action TEXT NOT NULL,
                user_id INTEGER DEFAULT NULL,
                target_id INTEGER DEFAULT NULL,
                channel_id INTEGER DEFAULT NULL,
                details TEXT,
                guild_id INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Health logs table - FIXED SCHEMA
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS health_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component TEXT NOT NULL,
                status TEXT NOT NULL,
                value REAL,
                details TEXT,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                uptime INTEGER,
                guild_count INTEGER,
                user_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # System flags table
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS system_flags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flag_name TEXT NOT NULL UNIQUE,
                flag_value TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Verifications table (PER-GUILD SYSTEM)
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                activision_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                screenshot_url TEXT,
                status TEXT DEFAULT 'pending',
                reviewed_by INTEGER,
                reviewed_at TIMESTAMP,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Appeals table
        await conn.execute(
            """
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
        """
        )

        # Level roles table
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS level_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                level INTEGER NOT NULL,
                role_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(guild_id, level)
            )
        """
        )

        # Daily checkins table (PER-GUILD SYSTEM)
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                last_checkin DATE NOT NULL,
                checkin_streak INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, guild_id)
            )
        """
        )

        await conn.commit()

        # Initialize roast_xp if not exists
        await self._initialize_roast_xp()

    async def _initialize_roast_xp(self) -> None:
        """Initialize roast XP table with default values."""
        conn = await self.get_connection()
        cursor = await conn.execute("SELECT COUNT(*) FROM roast_xp")
        count = (await cursor.fetchone())[0]

        if count == 0:
            await conn.execute(
                """
                INSERT INTO roast_xp (action, base_xp) VALUES
                    ('roast_success', 15),
                    ('roast_fail', 5),
                    ('defend_success', 10),
                    ('defend_fail', 3),
                    ('compliment', 8)
            """
            )
            await conn.commit()

    # === XP METHODS ===

    async def get_user_xp(self, user_id: int, guild_id: int) -> int:
        """Get user's current XP for a specific guild."""
        conn = await self.get_connection()

        # Ensure user exists
        await conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username, discriminator) VALUES (?, 'Unknown', '0')",
            (user_id,),
        )
        await conn.commit()

        cursor = await conn.execute(
            "SELECT xp FROM user_xp WHERE user_id = ? AND guild_id = ?", 
            (user_id, guild_id)
        )
        result = await cursor.fetchone()
        return result[0] if result else 0

    async def set_user_xp(self, user_id: int, guild_id: int, amount: int) -> tuple[int, int]:
        """Set user's XP to a specific amount for a specific guild and calculate level."""
        from config.constants import XP_TABLE

        # Calculate the appropriate level for the XP amount
        level = 1
        for lvl, req_xp in enumerate(XP_TABLE):
            if amount >= req_xp:
                level = lvl + 1
            else:
                break

        conn = await self.get_connection()

        # Ensure user exists
        await conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username, discriminator) VALUES (?, 'Unknown', '0')",
            (user_id,),
        )
        await conn.commit()

        # Set XP in user_xp table
        await conn.execute(
            """
            INSERT OR REPLACE INTO user_xp (user_id, guild_id, xp, level, last_message_time)
            VALUES (?, ?, ?, ?, datetime('now'))
            """,
            (user_id, guild_id, amount, level),
        )
        await conn.commit()

        return amount, level

    async def update_user_xp(self, user_id: int, xp_change: int, guild_id: int) -> tuple[int, int, bool]:
        """Update user's XP and recalculate level. Returns (new_xp, new_level, leveled_up)."""
        if guild_id is None:
            raise ValueError("guild_id is required for XP operations")

        conn = await self.get_connection()

        # Ensure user exists
        await conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username, discriminator) VALUES (?, 'Unknown', '0')",
            (user_id,),
        )
        await conn.commit()

        # Get current XP and level for this guild
        cursor = await conn.execute(
            "SELECT xp, level FROM user_xp WHERE user_id = ? AND guild_id = ?", 
            (user_id, guild_id)
        )
        result = await cursor.fetchone()
        current_xp = result[0] if result else 0
        old_level = result[1] if result else 0

        # Calculate new XP
        new_xp = max(0, current_xp + xp_change)

        # Get server's XP progression type
        progression_type = await self.get_setting("xp_progression_type", guild_id) or "custom"

        # Calculate new level based on progression type
        new_level = await self._calculate_level_from_xp(new_xp, progression_type)

        # Check if leveled up
        leveled_up = new_level > old_level

        # Update XP in user_xp table
        await conn.execute(
            """
            INSERT INTO user_xp (user_id, guild_id, xp, level, last_message_time)
            VALUES (?, ?, ?, ?, datetime('now'))
            ON CONFLICT(user_id, guild_id) 
            DO UPDATE SET 
                xp = excluded.xp,
                level = excluded.level,
                last_message_time = excluded.last_message_time
            """,
            (user_id, guild_id, new_xp, new_level),
        )
        await conn.commit()

        return new_xp, new_level, leveled_up

    async def _calculate_level_from_xp(self, xp: int, progression_type: str) -> int:
        """Calculate level from XP based on progression type."""
        if progression_type == "basic":
            # Linear: 100 XP per level after level 1
            # Level 0: 0-49 XP
            # Level 1: 50-149 XP
            # Level 2: 150-249 XP, etc.
            if xp < 50:
                return 0
            return ((xp - 50) // 100) + 1

        elif progression_type == "gradual":
            # Exponential: Gets harder each level
            # Level 0: 0-49 XP
            # Level 1: 50-149 XP (100 XP needed)
            # Level 2: 150-349 XP (200 XP needed)
            # Level 3: 350-649 XP (300 XP needed), etc.
            if xp < 50:
                return 0
            
            level = 1
            total_xp_needed = 50  # Start at 50 for level 1
            
            while level < 1000:  # Safety cap
                # Each level needs: level * 100 XP
                xp_for_next_level = (level + 1) * 100
                total_xp_needed += xp_for_next_level
                
                if xp < total_xp_needed:
                    return level
                level += 1
            
            return 1000

        elif progression_type == "custom":
            # Hybrid: Uses XP_TABLE from constants
            from config.constants import XP_TABLE
            
            # Level 0 if below 50 XP
            if xp < 50:
                return 0
            
            level = 0
            for lvl in sorted(XP_TABLE.keys()):
                if xp >= XP_TABLE[lvl]:
                    level = lvl
                else:
                    break
            return level

        else:
            # Default to custom
            return await self._calculate_level_from_xp(xp, "custom")


    async def remove_user_xp(self, user_id: int, guild_id: int, amount: int) -> tuple[int, int]:
        """Remove XP from user (alias for update_user_xp with negative value)."""
        return await self.update_user_xp(user_id, -amount, guild_id)

    async def get_user_level(self, user_id: int, guild_id: int) -> int:
        """Get user's current level for a specific guild."""
        conn = await self.get_connection()
        cursor = await conn.execute(
            "SELECT level FROM user_xp WHERE user_id = ? AND guild_id = ?", 
            (user_id, guild_id)
        )
        result = await cursor.fetchone()
        return result[0] if result else 1

    async def get_user_rank(self, user_id: int, guild_id: int) -> int:
        """Get user's rank in the guild."""
        conn = await self.get_connection()

        # Get all users in this guild with XP, sorted by XP descending
        cursor = await conn.execute(
            "SELECT user_id FROM user_xp WHERE guild_id = ? AND xp > 0 ORDER BY xp DESC",
            (guild_id,)
        )
        all_users = await cursor.fetchall()

        # Find user's position (1-indexed)
        for rank, (uid,) in enumerate(all_users, 1):
            if uid == user_id:
                return rank

        return len(all_users) + 1  # User not found or has no XP

    # === USER METHODS ===

    async def get_user(self, user_id: int) -> Optional[dict]:
        """Get user data."""
        conn = await self.get_connection()
        cursor = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()

        if not row:
            return None

        # Convert to dict
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row, strict=False))

    # === BIRTHDAY METHODS ===

    async def set_birthday(
        self, user_id: int, guild_id: int, birthday: str, timezone: str = "UTC"
    ) -> None:
        """Set user birthday for a specific guild."""
        conn = await self.get_connection()
        await conn.execute(
            """
            INSERT OR REPLACE INTO birthdays (user_id, guild_id, birthday, timezone)
            VALUES (?, ?, ?, ?)
        """,
            (user_id, guild_id, birthday, timezone),
        )
        await conn.commit()

    async def set_user_birthday(self, user_id: int, guild_id: int, birthday: str) -> bool:
        """Set user birthday for a specific guild (returns success status)."""
        try:
            await self.set_birthday(user_id, guild_id, birthday)
            return True
        except Exception:
            return False

    async def remove_user_birthday(self, user_id: int, guild_id: int) -> bool:
        """Remove user birthday (returns success status)."""
        try:
            conn = await self.get_connection()
            await conn.execute(
                "DELETE FROM birthdays WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id),
            )
            await conn.commit()
            return True
        except Exception:
            return False

    async def delete_user_data_from_guild(self, user_id: int, guild_id: int) -> bool:
        """Delete all user data for a specific guild when they leave."""
        try:
            conn = await self.get_connection()
            
            # Delete XP data
            await conn.execute(
                "DELETE FROM user_xp WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            
            # Delete birthday data
            await conn.execute(
                "DELETE FROM birthdays WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            
            # Delete verification data
            await conn.execute(
                "DELETE FROM verifications WHERE discord_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            
            # Delete appeals data
            await conn.execute(
                "DELETE FROM appeals WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            
            # Delete daily checkins data
            await conn.execute(
                "DELETE FROM daily_checkins WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            
            await conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting user data from guild: {e}")
            return False

    async def get_birthday(self, user_id: int, guild_id: int) -> Optional[tuple]:
        """Get user birthday for a specific guild."""
        conn = await self.get_connection()
        cursor = await conn.execute(
            "SELECT * FROM birthdays WHERE user_id = ? AND guild_id = ?", 
            (user_id, guild_id)
        )
        return await cursor.fetchone()

    async def get_user_birthday(self, user_id: int, guild_id: int) -> Optional[tuple]:
        """Get user birthday for a specific guild (alias)."""
        return await self.get_birthday(user_id, guild_id)

    async def get_all_birthdays(self) -> list:
        """Get all birthdays."""
        conn = await self.get_connection()
        cursor = await conn.execute("SELECT * FROM birthdays ORDER BY birthday")
        return await cursor.fetchall()

    async def get_today_birthdays(self, today: Optional[str] = None) -> list:
        """Get today's birthdays in MM-DD format."""
        conn = await self.get_connection()

        if today:
            # Use provided date
            cursor = await conn.execute(
                "SELECT user_id FROM birthdays WHERE birthday LIKE ?", (f"%{today}%",)
            )
        else:
            # Use current date
            cursor = await conn.execute(
                """
                SELECT user_id FROM birthdays
                WHERE strftime('%m-%d', birthday) = strftime('%m-%d', 'now')
            """
            )

        return await cursor.fetchall()

    async def get_unannounced_birthdays(self, current_year: int) -> list:
        """Get birthdays that haven't been announced this year."""
        conn = await self.get_connection()
        cursor = await conn.execute(
            """
            SELECT user_id, birthday FROM birthdays
            WHERE strftime('%m-%d', birthday) = strftime('%m-%d', 'now')
            AND (announced_year IS NULL OR announced_year < ?)
        """,
            (current_year,),
        )
        return await cursor.fetchall()

    async def mark_birthday_announced(self, user_id: int, year: int) -> None:
        """Mark that a birthday has been announced for a specific year."""
        conn = await self.get_connection()
        await conn.execute(
            """
            UPDATE birthdays
            SET announced_year = ?
            WHERE user_id = ?
        """,
            (year, user_id),
        )
        await conn.commit()

    # === LOGGING METHODS ===

    async def log_event(
        self,
        category: str,
        action: str,
        user_id: Optional[int] = None,
        target_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        details: Optional[str] = None,
        guild_id: Optional[int] = None,
    ) -> None:
        """Log an event to the audit log."""
        conn = await self.get_connection()
        await conn.execute(
            """
            INSERT INTO audit_log (category, action, user_id, target_id, channel_id, details, guild_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (category, action, user_id, target_id, channel_id, details, guild_id),
        )
        await conn.commit()

    async def log_moderation_action(
        self,
        moderator_id: int,
        action: str,
        target_id: Optional[int] = None,
        reason: Optional[str] = None,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        message_count: Optional[int] = None,
    ) -> None:
        """Log moderation action."""
        conn = await self.get_connection()
        await conn.execute(
            """
            INSERT INTO mod_logs (moderator_id, user_id, action, reason, guild_id, channel_id, message_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                moderator_id,
                target_id,
                action,
                reason,
                guild_id,
                channel_id,
                message_count,
            ),
        )
        await conn.commit()

    async def get_recent_moderation_logs(self, limit: int = 10) -> list[dict]:
        """Get recent moderation logs."""
        conn = await self.get_connection()
        cursor = await conn.execute(
            """
            SELECT * FROM mod_logs
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (limit,),
        )

        rows = await cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        return [dict(zip(columns, row, strict=False)) for row in rows]

    async def log_health_check(
        self,
        component: str,
        status: str,
        value: Optional[float] = None,
        details: Optional[str] = None,
    ) -> None:
        """Log health check results."""
        conn = await self.get_connection()
        await conn.execute(
            """
            INSERT INTO health_logs (component, status, value, details)
            VALUES (?, ?, ?, ?)
        """,
            (component, status, value, details),
        )
        await conn.commit()

    async def log_roast_user(self, user_id: int) -> None:
        """Log that user roasted the bot."""
        await self.log_event(
            category="ROAST",
            action="USER_ROAST",
            user_id=user_id,
            details="User roasted the bot",
        )

    # === SETTINGS METHODS ===

    async def get_setting(
        self, key: str, guild_id: Optional[int] = None
    ) -> Optional[str]:
        """Get setting value."""
        conn = await self.get_connection()
        if guild_id:
            cursor = await conn.execute(
                "SELECT value FROM settings WHERE setting_key = ? AND guild_id = ?",
                (key, guild_id),
            )
        else:
            cursor = await conn.execute(
                "SELECT value FROM settings WHERE setting_key = ? AND guild_id IS NULL",
                (key,),
            )
        result = await cursor.fetchone()
        return result[0] if result else None

    async def set_setting(
        self, key: str, value: str, guild_id: Optional[int] = None
    ) -> None:
        """Set setting value."""
        conn = await self.get_connection()
        await conn.execute(
            """
            INSERT OR REPLACE INTO settings (setting_key, value, guild_id, updated_at)
            VALUES (?, ?, ?, datetime('now'))
        """,
            (key, value, guild_id),
        )
        await conn.commit()

    # === SYSTEM FLAGS ===

    async def get_flag(self, flag_name: str) -> Any:
        """Get system flag value."""
        conn = await self.get_connection()
        cursor = await conn.execute(
            "SELECT flag_value FROM system_flags WHERE flag_name = ?", (flag_name,)
        )
        result = await cursor.fetchone()
        return result[0] if result else None

    async def set_flag(
        self, flag_name: str, flag_value: Any, description: Optional[str] = None
    ) -> None:
        """Set system flag."""
        conn = await self.get_connection()
        await conn.execute(
            """
            INSERT OR REPLACE INTO system_flags (flag_name, flag_value, description)
            VALUES (?, ?, ?)
        """,
            (flag_name, str(flag_value), description),
        )
        await conn.commit()

    async def clear_flag(self, flag_name: str) -> None:
        """Clear system flag."""
        conn = await self.get_connection()
        await conn.execute("DELETE FROM system_flags WHERE flag_name = ?", (flag_name,))
        await conn.commit()

    # === AUDIT METHODS ===

    async def get_audit_logs(self, limit: int = 100) -> list[dict]:
        """Get recent audit logs."""
        conn = await self.get_connection()
        cursor = await conn.execute(
            "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", (limit,)
        )

        rows = await cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        return [dict(zip(columns, row, strict=False)) for row in rows]

    async def get_daily_digest_stats(self) -> dict:
        """Get optimized daily digest statistics."""
        conn = await self.get_connection()

        cursor = await conn.execute(
            """
            SELECT
                COUNT(*) as total_logs,
                COUNT(CASE WHEN category = 'CRITICAL' THEN 1 END) as critical_events,
                COUNT(CASE WHEN category = 'WARNING' THEN 1 END) as warnings,
                COUNT(CASE WHEN action LIKE '%BAN%' OR action LIKE '%KICK%' OR action LIKE '%MUTE%' THEN 1 END) as moderation_actions,
                COUNT(CASE WHEN action LIKE '%JOIN%' OR action LIKE '%LEAVE%' THEN 1 END) as user_events
            FROM audit_log
            WHERE timestamp >= datetime('now', '-1 day')
        """
        )

        result = await cursor.fetchone()
        return {
            "total_logs": result[0] if result else 0,
            "critical_events": result[1] if result else 0,
            "warnings": result[2] if result else 0,
            "moderation_actions": result[3] if result else 0,
            "user_events": result[4] if result else 0,
        }

    # === ROAST METHODS ===

    async def add_roast_xp(self, xp_amount: int) -> dict:
        """Add roast XP."""
        # This is a placeholder - implement based on your roast XP system
        return {"xp_gained": xp_amount, "bot_level": 1}

    # === CLEANUP ===

    async def close(self) -> None:
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def add_xp(self, user_id: int, guild_id: int, xp_amount: int) -> tuple[int, int]:
        """Add XP to a user and return their new XP and level."""
        conn = await self.get_connection()
        
        try:
            # Ensure user exists in users table
            await conn.execute(
                "INSERT OR IGNORE INTO users (user_id, username, discriminator) VALUES (?, 'Unknown', '0')",
                (user_id,),
            )
            
            # Get current XP or use 0 if new
            cursor = await conn.execute(
                "SELECT xp FROM user_xp WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            result = await cursor.fetchone()
            current_xp = result[0] if result else 0
            
            new_xp = current_xp + xp_amount
            
            # Calculate level using the same formula as other XP methods
            progression_type = await self.get_setting("xp_progression_type", guild_id) or "custom"
            new_level = await self._calculate_level_from_xp(new_xp, progression_type)
            
            # Update XP using UPSERT
            await conn.execute(
                """
                INSERT INTO user_xp (user_id, guild_id, xp, level, last_message_time)
                VALUES (?, ?, ?, ?, datetime('now'))
                ON CONFLICT(user_id, guild_id) 
                DO UPDATE SET 
                    xp = excluded.xp,
                    level = excluded.level,
                    last_message_time = excluded.last_message_time
                """,
                (user_id, guild_id, new_xp, new_level)
            )
            
            await conn.commit()
            return new_xp, new_level
            
        except Exception as e:
            await conn.rollback()
            raise e
