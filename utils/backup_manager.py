"""
Automatic Backup Manager
Handles database backups, verification, and recovery
"""

import datetime
import json
import logging
import os
import shutil

logger = logging.getLogger('backup_manager')

class BackupManager:
    """Manages automatic database backups and recovery"""

    def __init__(self, db_path: str = "data/bot.db", backup_dir: str = "data/backups"):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.max_backups = 7  # Keep last 7 days

        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)

    def create_backup(self, backup_type: str = "auto") -> str:
        """
        Create a database backup

        Args:
            backup_type: Type of backup (auto, manual, pre-migration)

        Returns:
            Path to backup file
        """
        try:
            if not os.path.exists(self.db_path):
                logger.error(f"Database file not found: {self.db_path}")
                return None

            timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
            backup_filename = f"bot_backup_{backup_type}_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)

            # Copy database file
            shutil.copy2(self.db_path, backup_path)

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
            import sqlite3

            # Check file exists and has size
            if not os.path.exists(backup_path):
                return False

            if os.path.getsize(backup_path) == 0:
                return False

            # Try to open database
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()

            # Verify tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            conn.close()

            # Should have at least some tables
            return len(tables) > 0

        except Exception as e:
            logger.error(f"Backup verification error: {e}")
            return False

    def restore_backup(self, backup_path: str) -> bool:
        """
        Restore database from backup

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

            # Create backup of current database before restoring
            self.create_backup("pre-restore")

            # Restore backup
            shutil.copy2(backup_path, self.db_path)

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
            if filename.endswith('.db'):
                filepath = os.path.join(self.backup_dir, filename)
                metadata_path = filepath + '.meta'

                backup_info = {
                    'filename': filename,
                    'path': filepath,
                    'size': os.path.getsize(filepath),
                    'created': datetime.datetime.fromtimestamp(os.path.getctime(filepath), tz=datetime.UTC),
                    'type': 'unknown'
                }

                # Load metadata if exists
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path) as f:
                            metadata = json.load(f)
                            backup_info.update(metadata)
                    except Exception:
                        pass

                backups.append(backup_info)

        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)

        return backups

    def get_latest_backup(self) -> str:
        """
        Get path to most recent backup

        Returns:
            Path to latest backup or None
        """
        backups = self.list_backups()
        return backups[0]['path'] if backups else None

    def _create_metadata(self, backup_path: str, backup_type: str):
        """Create metadata file for backup"""
        metadata = {
            'type': backup_type,
            'created': datetime.datetime.now(datetime.UTC).isoformat(),
            'original_size': os.path.getsize(self.db_path),
            'backup_size': os.path.getsize(backup_path)
        }

        metadata_path = backup_path + '.meta'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def _cleanup_old_backups(self):
        """Remove backups older than max_backups days"""
        try:
            backups = self.list_backups()

            # Keep only max_backups most recent
            if len(backups) > self.max_backups:
                for backup in backups[self.max_backups:]:
                    try:
                        os.remove(backup['path'])
                        metadata_path = backup['path'] + '.meta'
                        if os.path.exists(metadata_path):
                            os.remove(metadata_path)
                        logger.info(f"Removed old backup: {backup['filename']}")
                    except Exception as e:
                        logger.error(f"Failed to remove old backup: {e}")

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    def auto_backup_if_needed(self) -> bool:
        """
        Create automatic backup if needed (once per day)

        Returns:
            True if backup was created
        """
        try:
            backups = self.list_backups()

            # Check if we have a backup from today
            today = datetime.datetime.now(datetime.UTC).date()
            for backup in backups:
                if backup['created'].date() == today and backup['type'] == 'auto':
                    logger.debug("Daily backup already exists")
                    return False

            # Create daily backup
            self.create_backup("auto")
            return True

        except Exception as e:
            logger.error(f"Auto backup check failed: {e}")
            return False


# Convenience functions
def create_backup(backup_type: str = "manual") -> str:
    """Create a database backup"""
    manager = BackupManager()
    return manager.create_backup(backup_type)

def restore_latest_backup() -> bool:
    """Restore from most recent backup"""
    manager = BackupManager()
    latest = manager.get_latest_backup()
    if latest:
        return manager.restore_backup(latest)
    return False

def list_backups() -> list:
    """List all available backups"""
    manager = BackupManager()
    return manager.list_backups()
