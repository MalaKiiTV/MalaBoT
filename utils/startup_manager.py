"""
Startup Manager
Handles bot initialization with comprehensive checks and safety measures
"""

import logging
from datetime import datetime
from utils.backup_manager import BackupManager
from utils.health_checker import HealthChecker
from utils.enhanced_logger import setup_logging, get_logger

logger = get_logger('startup')

class StartupManager:
    """
    Manages bot startup process with safety checks
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.backup_manager = BackupManager()
        self.health_checker = HealthChecker(bot)
        self.startup_time = None
        
    async def run_startup_sequence(self) -> bool:
        """
        Run complete startup sequence
        
        Returns:
            True if startup successful
        """
        self.startup_time = datetime.now()
        
        logger.info("=" * 70)
        logger.info("🚀 MALABOT STARTUP SEQUENCE")
        logger.info("=" * 70)
        
        try:
            # Step 1: Setup logging
            logger.info("📋 Step 1: Setting up logging system...")
            setup_logging()
            logger.info("✅ Logging system ready")
            
            # Step 2: Create startup backup
            logger.info("💾 Step 2: Creating startup backup...")
            backup_path = self.backup_manager.create_backup("startup")
            if backup_path:
                logger.info(f"✅ Startup backup created: {backup_path}")
            else:
                logger.warning("⚠️ Startup backup failed (continuing anyway)")
            
            # Step 3: Run health checks
            logger.info("🏥 Step 3: Running health checks...")
            health_results = await self.health_checker.run_full_check()
            
            # Check critical systems
            critical_checks = [
                'database_exists',
                'database_accessible',
                'tables_exist'
            ]
            
            critical_failed = [c for c in critical_checks if not health_results.get(c, False)]
            
            if critical_failed:
                logger.error(f"❌ Critical checks failed: {critical_failed}")
                logger.error("❌ STARTUP ABORTED - Fix critical issues and restart")
                return False
            
            logger.info("✅ All critical checks passed")
            
            # Step 4: Verify data integrity
            logger.info("🔍 Step 4: Verifying data integrity...")
            await self._verify_data_integrity()
            logger.info("✅ Data integrity verified")
            
            # Step 5: Load cogs
            logger.info("🔌 Step 5: Loading cogs...")
            # Cogs are loaded by bot.py, just verify here
            if len(self.bot.cogs) > 0:
                logger.info(f"✅ {len(self.bot.cogs)} cogs loaded")
            else:
                logger.warning("⚠️ No cogs loaded")
            
            # Step 6: Final verification
            logger.info("✔️ Step 6: Final verification...")
            await self._final_verification()
            logger.info("✅ Final verification complete")
            
            # Startup complete
            elapsed = (datetime.now() - self.startup_time).total_seconds()
            logger.info("=" * 70)
            logger.info(f"✅ STARTUP COMPLETE ({elapsed:.2f}s)")
            logger.info("=" * 70)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ STARTUP FAILED: {e}", exc_info=True)
            logger.error("=" * 70)
            return False
    
    async def _verify_data_integrity(self):
        """Verify critical data exists and is valid"""
        try:
            for guild in self.bot.guilds:
                guild_id = guild.id
                
                # Check role connections
                success, message = await self.health_checker.verify_role_connections(guild_id)
                if success:
                    logger.debug(f"  ✅ {guild.name}: {message}")
                else:
                    logger.warning(f"  ⚠️ {guild.name}: {message}")
                    
        except Exception as e:
            logger.error(f"Data integrity check error: {e}")
    
    async def _final_verification(self):
        """Final verification before going live"""
        try:
            # Verify bot is ready
            if not self.bot.is_ready():
                logger.warning("⚠️ Bot not fully ready yet")
            
            # Verify database manager
            if not self.bot.db_manager:
                raise Exception("Database manager not initialized")
            
            # Verify processing_members set exists
            if not hasattr(self.bot, 'processing_members'):
                self.bot.processing_members = set()
                logger.info("  ℹ️ Created processing_members set")
            
            # Verify pending_verifications dict exists
            if not hasattr(self.bot, 'pending_verifications'):
                self.bot.pending_verifications = {}
                logger.info("  ℹ️ Created pending_verifications dict")
            
        except Exception as e:
            logger.error(f"Final verification error: {e}")
            raise
    
    def get_startup_report(self) -> str:
        """Get formatted startup report"""
        if not self.startup_time:
            return "Startup not completed"
        
        elapsed = (datetime.now() - self.startup_time).total_seconds()
        
        report = [
            "=" * 50,
            "🚀 MALABOT STARTUP REPORT",
            "=" * 50,
            f"Startup Time: {self.startup_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Elapsed: {elapsed:.2f}s",
            f"Guilds: {len(self.bot.guilds)}",
            f"Cogs: {len(self.bot.cogs)}",
            "",
            "Health Status:",
            self.health_checker.get_health_report(),
            "=" * 50
        ]
        
        return "\n".join(report)


async def initialize_bot(bot) -> bool:
    """
    Initialize bot with full startup sequence
    
    Args:
        bot: Discord bot instance
        
    Returns:
        True if initialization successful
    """
    manager = StartupManager(bot)
    success = await manager.run_startup_sequence()
    
    if success:
        # Store manager for later use
        bot.startup_manager = manager
    
    return success