"""Automatic Backup Manager
Handles Supabase data backups, verification, and recovery
"""

import json
import logging
import os
import asyncio
from datetime import datetime
from src.database.supabase_models import DatabaseManager

logger = logging.getLogger("backup_manager")


class BackupManager:
    """Manages automatic Supabase data backups and recovery"""

    def __init__(self, backup_dir: str = "data/backups"):
        self.backup_dir = backup_dir
        self.max_backups = 7  # Keep last 7 days

        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)

    async def create_backup(self, backup_type: str = "auto") -> str:
        """
        Create a Supabase data backup

        Args:
            backup_type: Type of backup (auto, manual, pre-migration)

        Returns:
            Path to backup file
        """
        try:
            db = DatabaseManager()
            await db.initialize()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"supabase_backup_{backup_type}_{timestamp}.json"
            backup_path = os.path.join(self.backup_dir, backup_filename)

            # Get all data from Supabase
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "type": backup_type,
                "tables": {}
            }

            # List of tables to backup
            tables = ['users', 'birthdays', 'audit_log', 'mod_logs', 'health_logs', 'settings', 'system_flags']

            for table in tables:
                try:
                    result = db.supabase.table(table).select('*').execute()
                    backup_data["tables"][table] = result.data
                    logger.info(f"Backed up {len(result.data)} records from {table}")
                except Exception as e:
                    logger.warning(f"Failed to backup table {table}: {e}")
                    backup_data["tables"][table] = []

            # Save backup to file
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)

            # Verify backup
            if self.verify_backup(backup_path):
                logger.info(f"✅ Backup created successfully: {backup_filename}")

                # Create metadata file
                self._create_metadata(backup_path, backup_type)

                # Cleanup old backups
                self._cleanup_old_backups()

                return backup_path
            else:
                logger.error(f"❌ Backup verification failed: {backup_filename}")
                os.remove(backup_path)
                return None

        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            return None

    def verify_backup(self, backup_path: str) -> bool:
        """
        Verify backup file integrity

        Args:
            backup_path: Path to backup file

        Returns:
            True if backup is valid
        """
        try:
            # Check file exists and has size
            if not os.path.exists(backup_path):
                return False

            if os.path.getsize(backup_path) == 0:
                return False

            # Try to load JSON
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)

            # Verify structure
            required_keys = ['timestamp', 'type', 'tables']
            if not all(key in backup_data for key in required_keys):
                return False

            return True

        except Exception as e:
            logger.error(f"Backup verification error: {e}")
            return False

    async def restore_backup(self, backup_path: str) -> bool:
        """
        Restore Supabase data from backup

        Args:
            backup_path: Path to backup file

        Returns:
            True if restore successful
        """
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False

            if not self.verify_backup(backup_path):
                logger.error(f"Backup file is corrupted: {backup_path}")
                return False

            # Create backup of current data before restoring
            current_backup = await self.create_backup("pre-restore")
            if not current_backup:
                logger.warning("Failed to create pre-restore backup")

            # Load backup data
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)

            db = DatabaseManager()
            await db.initialize()

            # Restore data for each table
            for table_name, records in backup_data["tables"].items():
                try:
                    if records:  # Only restore if there are records
                        # Clear existing data and insert backup data
                        db.supabase.table(table_name).delete().neq('id', -1).execute()  # Delete all
                        db.supabase.table(table_name).insert(records).execute()
                        logger.info(f"✅ Restored {len(records)} records to {table_name}")
                    else:
                        logger.info(f"⚠️ No records to restore for {table_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to restore table {table_name}: {e}")

            logger.info(f"✅ Database restored from: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Restore failed: {e}")
            return False

    def list_backups(self) -> list:
        """
        List all available backups

        Returns:
            List of backup files with metadata
        """
        backups = []

        for filename in os.listdir(self.backup_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.backup_dir, filename)
                metadata_path = filepath + ".meta"

                backup_info = {
                    "filename": filename,
                    "path": filepath,
                    "size": os.path.getsize(filepath),
                    "created": datetime.fromtimestamp(os.path.getctime(filepath)),
                    "type": "unknown",
                }

                # Load metadata if exists
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path) as f:
                            metadata = json.load(f)
                            backup_info.update(metadata)
                    except (json.JSONDecodeError, IOError) as e:
                        logger.warning(f"Failed to read metadata for {filename}: {e}")

                backups.append(backup_info)

        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)

        return backups

    def get_latest_backup(self) -> str:
        """
        Get path to most recent backup

        Returns:
            Path to latest backup or None
        """
        backups = self.list_backups()
        return backups[0]["path"] if backups else None

    def _create_metadata(self, backup_path: str, backup_type: str):
        """Create metadata file for backup"""
        metadata = {
            "type": backup_type,
            "created": datetime.now().isoformat(),
            "backup_size": os.path.getsize(backup_path),
        }

        metadata_path = backup_path + ".meta"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    def _cleanup_old_backups(self):
        """Remove backups older than max_backups days"""
        try:
            backups = self.list_backups()

            # Keep only max_backups most recent
            if len(backups) > self.max_backups:
                for backup in backups[self.max_backups:]:
                    try:
                        os.remove(backup["path"])
                        metadata_path = backup["path"] + ".meta"
                        if os.path.exists(metadata_path):
                            os.remove(metadata_path)
                        logger.info(f"Removed old backup: {backup['filename']}")
                    except Exception as e:
                        logger.error(f"Failed to remove old backup: {e}")

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    async def auto_backup_if_needed(self) -> bool:
        """
        Create automatic backup if needed (once per day)

        Returns:
            True if backup was created
        """
        try:
            backups = self.list_backups()

            # Check if we have a backup from today
            today = datetime.now().date()
            for backup in backups:
                if backup["created"].date() == today and backup["type"] == "auto":
                    logger.debug("Daily backup already exists")
                    return False

            # Create daily backup
            await self.create_backup("auto")
            return True

        except Exception as e:
            logger.error(f"Auto backup check failed: {e}")
            return False


# Convenience functions
async def create_backup(backup_type: str = "manual") -> str:
    """Create a Supabase data backup"""
    manager = BackupManager()
    return await manager.create_backup(backup_type)


async def restore_latest_backup() -> bool:
    """Restore from most recent backup"""
    manager = BackupManager()
    latest = manager.get_latest_backup()
    if latest:
        return await manager.restore_backup(latest)
    return False


def list_backups() -> list:
    """List all available backups"""
    manager = BackupManager()
    return manager.list_backups()
