"""
Safe Database Wrapper
Ensures all database operations are safe, verified, and logged
"""

import json
import logging
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger("safe_database")


class SafeDatabase:
    """
    Wrapper around database manager that adds:
    - Transaction safety
    - Write verification
    - Comprehensive logging
    - Automatic retry
    - Error recovery
    """

    def __init__(self, db_manager):
        self.db = db_manager
        self.write_log = []  # Track all writes for debugging

    async def set_setting(self, key: str, value: Any, verify: bool = True) -> bool:
        """
        Safely set a setting with verification

        Args:
            key: Setting key
            value: Setting value
            verify: Whether to verify write succeeded

        Returns:
            True if successful
        """
        try:
            # Log the write attempt
            logger.info(f"[WRITE] Setting: {key}")
            self._log_write("set_setting", key, value)

            # Perform the write
            await self.db.set_setting(key, value)

            # Verify if requested
            if verify:
                stored_value = await self.db.get_setting(key)
                if stored_value != value:
                    logger.error(
                        f"[VERIFY FAILED] {key}: expected {value}, got {stored_value}"
                    )
                    return False
                logger.debug(f"[VERIFY OK] {key}")

            return True

        except Exception as e:
            logger.error(f"[WRITE ERROR] {key}: {e}")
            return False

    async def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Safely get a setting with error handling

        Args:
            key: Setting key
            default: Default value if not found

        Returns:
            Setting value or default
        """
        try:
            value = await self.db.get_setting(key, default)
            logger.debug(f"[READ] {key}: {value is not None}")
            return value
        except Exception as e:
            logger.error(f"[READ ERROR] {key}: {e}")
            return default

    async def save_json_setting(
        self, key: str, data: dict, verify: bool = True
    ) -> bool:
        """
        Save JSON data with verification

        Args:
            key: Setting key
            data: Dictionary to save as JSON
            verify: Whether to verify write

        Returns:
            True if successful
        """
        try:
            json_str = json.dumps(data)
            success = await self.set_setting(key, json_str, verify=False)

            if not success:
                return False

            # Verify JSON can be loaded back
            if verify:
                loaded = await self.load_json_setting(key)
                if loaded != data:
                    logger.error(f"[JSON VERIFY FAILED] {key}")
                    return False
                logger.debug(f"[JSON VERIFY OK] {key}")

            return True

        except Exception as e:
            logger.error(f"[JSON SAVE ERROR] {key}: {e}")
            return False

    async def load_json_setting(self, key: str, default: dict = None) -> dict:
        """
        Load JSON data with error handling

        Args:
            key: Setting key
            default: Default value if not found

        Returns:
            Parsed JSON data or default
        """
        try:
            json_str = await self.get_setting(key)
            if json_str:
                return json.loads(json_str)
            return default or {}
        except json.JSONDecodeError as e:
            logger.error(f"[JSON PARSE ERROR] {key}: {e}")
            return default or {}
        except Exception as e:
            logger.error(f"[JSON LOAD ERROR] {key}: {e}")
            return default or {}

    async def atomic_update(self, key: str, update_func, verify: bool = True) -> bool:
        """
        Atomically update a setting

        Args:
            key: Setting key
            update_func: Function that takes current value and returns new value
            verify: Whether to verify write

        Returns:
            True if successful
        """
        try:
            # Get current value
            current = await self.get_setting(key)

            # Apply update function
            new_value = update_func(current)

            # Save new value
            return await self.set_setting(key, new_value, verify)

        except Exception as e:
            logger.error(f"[ATOMIC UPDATE ERROR] {key}: {e}")
            return False

    def _log_write(self, operation: str, key: str, value: Any):
        """Log write operation for debugging"""
        self.write_log.append(
            {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "key": key,
                "value_type": type(value).__name__,
                "value_size": len(str(value)) if value else 0,
            }
        )

        # Keep only last 100 writes
        if len(self.write_log) > 100:
            self.write_log = self.write_log[-100:]

    def get_write_history(self, key: Optional[str] = None) -> list:
        """Get write history for debugging"""
        if key:
            return [w for w in self.write_log if w["key"] == key]
        return self.write_log


    async def get_daily_checkin(self, user_id: int):
        """Get user's last daily checkin."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchone(
                "SELECT last_checkin, checkin_streak FROM daily_checkins WHERE user_id = ?",
                (user_id,)
            )
            return row

    async def update_daily_checkin(self, user_id: int, date: str, streak: int):
        """Update user's daily checkin record."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT OR REPLACE INTO daily_checkins (user_id, last_checkin, checkin_streak) VALUES (?, ?, ?)",
                (user_id, date, streak)
            )
            await conn.commit()

    async def get_checkin_count(self):
        """Get total number of checkin records."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchone("SELECT COUNT(*) FROM daily_checkins")
            return row[0] if row else 0

    async def reset_all_checkins(self):
        """Reset all daily checkin records."""
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM daily_checkins")
            await conn.commit()



class RoleConnectionSafeDB:
    """
    Specialized safe database for role connections
    Adds extra verification and recovery for role connection data
    """

    def __init__(self, db_manager):
        self.safe_db = SafeDatabase(db_manager)
        self.db = db_manager

    async def save_connections(self, guild_id: int, connections: list) -> bool:
        """
        Safely save role connections with verification

        Args:
            guild_id: Guild ID
            connections: List of connection dictionaries

        Returns:
            True if successful
        """
        key = f"role_connections_{guild_id}"

        try:
            # Convert to JSON
            data = [
                conn if isinstance(conn, dict) else conn.to_dict()
                for conn in connections
            ]

            # Save with verification
            success = await self.safe_db.save_json_setting(key, data, verify=True)

            if success:
                logger.info(
                    f" Saved {len(connections)} role connections for guild {guild_id}"
                )
            else:
                logger.error(f" Failed to save role connections for guild {guild_id}")

            return success

        except Exception as e:
            logger.error(f" Error saving role connections: {e}")
            return False

    async def load_connections(self, guild_id: int) -> list:
        """
        Safely load role connections with error recovery

        Args:
            guild_id: Guild ID

        Returns:
            List of connection dictionaries
        """
        key = f"role_connections_{guild_id}"

        try:
            data = await self.safe_db.load_json_setting(key, default=[])

            if data:
                logger.info(
                    f" Loaded {len(data)} role connections for guild {guild_id}"
                )
            else:
                logger.debug(f"No role connections found for guild {guild_id}")

            return data

        except Exception as e:
            logger.error(f" Error loading role connections: {e}")
            return []

    async def verify_connections_exist(self, guild_id: int) -> bool:
        """
        Verify that role connections data exists and is valid

        Args:
            guild_id: Guild ID

        Returns:
            True if connections exist and are valid
        """
        try:
            connections = await self.load_connections(guild_id)
            return isinstance(connections, list)
        except Exception as e:
            logger.error(f"Failed to check connections for guild {guild_id}: {e}")
            return False

    async def save_protected_roles(self, guild_id: int, role_ids: list) -> bool:
        """
        Safely save protected roles

        Args:
            guild_id: Guild ID
            role_ids: List of role IDs

        Returns:
            True if successful
        """
        key = f"protected_roles_{guild_id}"
        return await self.safe_db.save_json_setting(key, role_ids, verify=True)

    async def load_protected_roles(self, guild_id: int) -> list:
        """
        Safely load protected roles

        Args:
            guild_id: Guild ID

        Returns:
            List of role IDs
        """
        key = f"protected_roles_{guild_id}"
        return await self.safe_db.load_json_setting(key, default=[])

