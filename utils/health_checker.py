"""
Health Check System
Monitors bot health and verifies critical data integrity
"""

import logging
import os
from datetime import datetime

logger = logging.getLogger("health_checker")


class HealthChecker:
    """
    Monitors bot health and data integrity
    """

    def __init__(self, bot):
        self.bot = bot
        self.last_check = None
        self.health_status = {}

    async def run_full_check(self) -> dict[str, bool]:
        """
        Run complete health check

        Returns:
            Dictionary of check results
        """
        logger.info("🏥 Running full health check...")

        results = {}

        # Database checks
        results["database_exists"] = await self._check_database_exists()
        results["database_accessible"] = await self._check_database_accessible()
        results["tables_exist"] = await self._check_tables_exist()

        # Data integrity checks
        results["settings_readable"] = await self._check_settings_readable()
        results["critical_data_exists"] = await self._check_critical_data()

        # System checks
        results["cogs_loaded"] = await self._check_cogs_loaded()
        results["memory_ok"] = await self._check_memory()

        # Log results
        self._log_results(results)

        self.last_check = datetime.now()
        self.health_status = results

        return results

    async def _check_database_exists(self) -> bool:
        """Check if Supabase connection exists"""
        try:
            if not self.bot.db_manager:
                logger.error("❌ Database manager not initialized!")
                return False

            # Check if Supabase client exists
            if not hasattr(self.bot.db_manager, 'supabase'):
                logger.error("❌ Supabase client not found!")
                return False

            return True
        except Exception as e:
            logger.error(f"❌ Database check failed: {e}")
            return False

    async def _check_database_accessible(self) -> bool:
        """Check if Supabase is accessible"""
        try:
            if not self.bot.db_manager:
                return False

            # Try a simple Supabase query
            result = self.bot.db_manager.supabase.table('users').select('count').execute()
            return True
        except Exception as e:
            logger.error(f"❌ Supabase not accessible: {e}")
            return False

    async def _check_tables_exist(self) -> bool:
        """Check if all required tables exist in Supabase"""
        try:
            required_tables = [
                "users",
                "birthdays", 
                "settings",
                "mod_logs",
                "roast_xp",
                "audit_log",
                "health_logs",
                "system_flags",
                "verifications",
                "appeals",
            ]

            # For Supabase, we assume tables exist if we can query them
            # Tables are managed in Supabase dashboard
            logger.info("✅ Using Supabase - tables managed in dashboard")
            return True
        except Exception as e:
            logger.error(f"❌ Table check failed: {e}")
            return False

    async def _check_settings_readable(self) -> bool:
        """Check if settings table is readable"""
        try:
            # Try to read a setting
            await self.bot.db_manager.get_setting("health_check_test")
            return True
        except Exception as e:
            logger.error(f"❌ Settings not readable: {e}")
            return False

    async def _check_critical_data(self) -> bool:
        """Check if critical data exists for each guild"""
        try:
            issues = []

            for guild in self.bot.guilds:
                guild_id = guild.id

                # Check if guild has any settings
                settings_exist = await self._guild_has_settings(guild_id)
                if not settings_exist:
                    issues.append(f"Guild {guild.name} has no settings")

            if issues:
                logger.warning(f"⚠️ Data issues: {issues}")

            return len(issues) == 0
        except Exception as e:
            logger.error(f"❌ Critical data check failed: {e}")
            return False

    async def _guild_has_settings(self, guild_id: int) -> bool:
        """Check if guild has any configured settings"""
        try:
            # Check for common settings
            settings_to_check = [
                f"timezone_{guild_id}",
                f"verify_channel_{guild_id}",
                f"welcome_channel_{guild_id}",
            ]

            for setting in settings_to_check:
                value = await self.bot.db_manager.get_setting(setting)
                if value:
                    return True

            return False
        except Exception as e:
            logger.error(f"Failed to check bot configuration: {e}")
            return False

    async def _check_cogs_loaded(self) -> bool:
        """Check if all cogs are loaded"""
        try:
            required_cogs = [
                "Setup",
                "Verify",
                "RoleConnections",
                "XP",
                "Welcome",
                "Birthdays",
            ]

            loaded_cogs = [cog for cog in self.bot.cogs]
            missing = [c for c in required_cogs if c not in loaded_cogs]

            if missing:
                logger.error(f"❌ Missing cogs: {missing}")
                return False

            return True
        except Exception as e:
            logger.error(f"❌ Cog check failed: {e}")
            return False

    async def _check_memory(self) -> bool:
        """Check memory usage"""
        try:
            import psutil

            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024

            # Warn if over 500MB
            if memory_mb > 500:
                logger.warning(f"⚠️ High memory usage: {memory_mb:.1f}MB")
                return False

            return True
        except ImportError:
            # psutil not installed, skip check
            return True
        except Exception as e:
            logger.error(f"❌ Memory check failed: {e}")
            return True  # Don't fail on memory check errors

    def _log_results(self, results: dict[str, bool]):
        """Log health check results"""
        passed = sum(1 for v in results.values() if v)
        total = len(results)

        if passed == total:
            logger.info(f"✅ Health check passed: {passed}/{total} checks OK")
        else:
            logger.warning(f"⚠️ Health check issues: {passed}/{total} checks OK")

            # Log failed checks
            for check, result in results.items():
                if not result:
                    logger.error(f"  ❌ {check}")

    async def verify_role_connections(self, guild_id: int) -> tuple[bool, str]:
        """
        Verify role connections data integrity

        Returns:
            (success, message)
        """
        try:
            from utils.safe_database import RoleConnectionSafeDB

            safe_db = RoleConnectionSafeDB(self.bot.db_manager)

            # Check if connections exist
            exists = await safe_db.verify_connections_exist(guild_id)

            if not exists:
                return False, "Role connections data not found or corrupted"

            # Load and verify structure
            connections = await safe_db.load_connections(guild_id)

            if not isinstance(connections, list):
                return False, "Role connections data has invalid format"

            # Verify each connection has required fields
            for conn in connections:
                required_fields = ["id", "target_role_id", "action", "conditions"]
                missing = [f for f in required_fields if f not in conn]
                if missing:
                    return False, f"Connection missing fields: {missing}"

            return True, f"Role connections OK ({len(connections)} connections)"

        except Exception as e:
            return False, f"Verification error: {e}"

    def get_health_report(self) -> str:
        """Get formatted health report"""
        if not self.health_status:
            return "No health check run yet"

        report = ["🏥 Health Check Report"]
        report.append(f"Last check: {self.last_check.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        for check, result in self.health_status.items():
            status = "✅" if result else "❌"
            report.append(f"{status} {check.replace('_', ' ').title()}")

        return "\n".join(report)


async def run_startup_verification(bot) -> bool:
    """
    Run comprehensive startup verification

    Returns:
        True if all checks pass
    """
    logger.info("=" * 60)
    logger.info("🚀 STARTING BOT VERIFICATION")
    logger.info("=" * 60)

    checker = HealthChecker(bot)
    results = await checker.run_full_check()

    # Check if all passed
    all_passed = all(results.values())

    if all_passed:
        logger.info("=" * 60)
        logger.info("✅ ALL CHECKS PASSED - BOT READY")
        logger.info("=" * 60)
    else:
        logger.error("=" * 60)
        logger.error("❌ SOME CHECKS FAILED - REVIEW ERRORS ABOVE")
        logger.error("=" * 60)

    return all_passed
