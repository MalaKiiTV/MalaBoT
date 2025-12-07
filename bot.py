"""
MalaBoT - Multifunctional Discord Bot
Main entry point and core bot framework.
"""

import asyncio
import os
import signal
import sys
from datetime import datetime, timedelta
from typing import Optional

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands

# Clear Discord.py's default handlers before our logger initializes
import logging
logging.getLogger("discord").handlers.clear()
logging.getLogger("discord.gateway").handlers.clear()
logging.getLogger("discord.client").handlers.clear()


# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from database.models import DatabaseManager
from utils.helpers import (
    create_embed,
    embed_helper,
    format_duration,
    get_system_info,
    safe_send_message,
    system_helper,
)
from utils.logger import get_logger, log_critical, log_startup_verification, log_system


class MalaBoT(commands.Bot):
    """Main bot class with advanced features."""

    def __init__(self):
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.presences = True

        # Initialize bot
        super().__init__(
            command_prefix=settings.BOT_PREFIX,
            intents=intents,
            help_command=None,  # We'll create our own help command
            owner_ids=set(settings.OWNER_IDS),
        )

        # Core components
        self.db_manager: Optional[DatabaseManager] = None
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.start_time: Optional[datetime] = None
        self.safe_mode: bool = False
        self.logger = get_logger("bot")

        # Processing locks for role operations
        self.processing_members: set = (
            set()
        )  # Member IDs being processed (e.g., cheater assignment)

        # Feature flags
        self.enabled_features = {
            "music": settings.ENABLE_MUSIC,
            "moderation": settings.ENABLE_MODERATION,
            "fun": settings.ENABLE_FUN,
            "utility": settings.ENABLE_UTILITY,
            "health_monitor": settings.ENABLE_HEALTH_MONITOR,
            "watchdog": settings.ENABLE_WATCHDOG,
        }

        # Status tracking
        self.cogs_loaded = []
        self.cogs_failed = []
        self.crash_count = 0

        # Register signal handlers
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""

        def signal_handler(signum, _frame):
            self.logger.info(
                f"Received signal {signum}, initiating graceful shutdown..."
            )
            # Use the bot's loop if available, otherwise force exit
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.shutdown())
                else:
                    # No running loop, force synchronous shutdown
                    self.logger.warning(
                        "No running event loop, forcing immediate shutdown"
                    )
                    sys.exit(0)
            except RuntimeError:
                # No event loop at all
                self.logger.warning(
                    "No event loop available, forcing immediate shutdown"
                )
                sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def setup_hook(self):
        """Called when the bot is starting up."""
        try:
            self.start_time = datetime.now()

            # Run startup verification
            await self._startup_verification()

            # Initialize database
            await self._initialize_database()

            # Check for crash flags and determine if safe mode is needed
            await self._check_crash_flags()

            # Load cogs based on mode
            await self._load_cogs()

            # Initialize scheduler
            await self._initialize_scheduler()

            # Start background tasks
            await self._start_background_tasks()

            self.logger.info("Bot setup completed successfully")

            # Send online message if configured
            if self.get_cog("Owner"):
                await self.get_cog("Owner").send_online_message()
        except Exception as e:
            log_critical("Failed during bot setup", e)
            raise

    async def _startup_verification(self):
        """Verify startup environment and auto-repair if needed."""
        self.logger.info("Running startup verification...")

        verification_results = {
            "environment": False,
            "directories": False,
            "log_files": False,
            "database": False,
            "details": [],
        }

        try:
            # Check environment
            errors = settings.validate()
            if not errors:
                verification_results["environment"] = True
            else:
                verification_results["details"].append(f"Environment errors: {errors}")

            # Check and create directories
            required_dirs = ["data/logs", "backups", "data/flags"]

            dirs_ok = True
            for dir_path in required_dirs:
                try:
                    os.makedirs(dir_path, exist_ok=True)
                except Exception as e:
                    dirs_ok = False
                    verification_results["details"].append(
                        f"Failed to create {dir_path}: {e}"
                    )

            verification_results["directories"] = dirs_ok

            # Check log file access
            try:
                os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
                with open(settings.LOG_FILE, "a") as f:
                    pass
                verification_results["log_files"] = True
            except Exception as e:
                verification_results["details"].append(f"Log file access failed: {e}")

            # Database check will be done in _initialize_database
            verification_results["database"] = True

        except Exception as e:
            verification_results["details"].append(f"Verification error: {e}")

        # Log results
        log_startup_verification(verification_results)

        # Auto-repair if enabled
        if settings.ENABLE_AUTO_REPAIR and not all(
            verification_results[k] for k in ["environment", "directories", "log_files"]
        ):
            self.logger.warning("Auto-repair triggered due to verification failures")
            # Auto-repair logic would go here

        return verification_results

    async def _initialize_database(self):
        """Initialize database connection."""
        try:
            self.db_manager = DatabaseManager(
                settings.DATABASE_URL.replace("sqlite:///", "")
                if settings.DATABASE_URL.startswith("sqlite://")
                else settings.DATABASE_URL
            )
            await self.db_manager.initialize()
            self.logger.info("Database initialized successfully")

            # Log startup event
            await self.db_manager.log_event(
                category="SYSTEM",
                action="STARTUP",
                details=f"Bot version {settings.BOT_VERSION} starting up",
            )

        except Exception as e:
            log_critical("Failed to initialize database", e)
            raise

    async def _check_crash_flags(self):
        """Check for crash flags and determine safe mode."""
        if not self.db_manager:
            return

        try:
            crash_flag = await self.db_manager.get_flag("crash_detected")

            if crash_flag:
                self.safe_mode = True
                self.logger.warning(
                    f"Crash flag detected: {crash_flag}. Entering safe mode."
                )

                # Clear the flag for next startup
                await self.db_manager.clear_flag("crash_detected")

                # Log crash recovery
                await self.db_manager.log_event(
                    category="SYSTEM",
                    action="SAFE_MODE_START",
                    details=f"Safe mode enabled due to crash: {crash_flag}",
                )

                # Create crash report
                self._create_crash_report(crash_flag)

        except Exception as e:
            self.logger.error(f"Error checking crash flags: {e}")

    def _create_crash_report(self, crash_reason: str):
        """Create a crash report file."""
        try:
            crash_report = f"""
CRASH REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
=========================================
Crash Reason: {crash_reason}
Bot Version: {settings.BOT_VERSION}
Safe Mode: Enabled

This crash report was generated automatically.
The bot will start in safe mode to prevent further issues.
"""

            # Write crash report to file
            crash_file = (
                f"data/logs/crash_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            with open(crash_file, "w", encoding="utf-8") as f:
                f.write(crash_report)

            self.logger.info(f"Crash report created: {crash_file}")

        except Exception as e:
            self.logger.error(f"Failed to create crash report: {e}")

    async def _load_cogs(self):
        """Load cogs based on current mode."""
        if self.safe_mode:
            # Safe mode: load only essential cogs
            essential_cogs = [
                "cogs.utility",
                "cogs.moderation",
                "cogs.xp",
                "cogs.birthdays",
                "cogs.owner",
                "cogs.verify",
            ]

            self.logger.info("Loading essential cogs in safe mode...")
            for cog in essential_cogs:
                await self._load_cog(cog)

        else:
            # Normal mode: load all enabled cogs
            cogs_to_load = [
                "cogs.utility",
                "cogs.fun",
                "cogs.moderation",
                "cogs.xp",
                "cogs.birthdays",
                "cogs.welcome",
                "cogs.owner",
                "cogs.verify",
                "cogs.setup",
                "cogs.appeal",
                "cogs.bot_control",
                "cogs.role_connections",
            ]

            self.logger.info("Loading all cogs...")
            for cog in cogs_to_load:
                await self._load_cog(cog)

        # Log loading results
        self.logger.info(f"Cogs loaded: {', '.join(self.cogs_loaded)}")
        if self.cogs_failed:
            self.logger.warning(f"Cogs failed to load: {', '.join(self.cogs_failed)}")

    async def _load_cog(self, cog_name: str):
        """Load a single cog."""
        try:
            await self.load_extension(cog_name)
            self.cogs_loaded.append(cog_name)
            self.logger.debug(f"Loaded cog: {cog_name}")
        except Exception as e:
            self.cogs_failed.append(cog_name)
            self.logger.error(f"Failed to load cog {cog_name}: {e}")

    async def _initialize_scheduler(self):
        """Initialize the APScheduler."""
        try:
            self.scheduler = AsyncIOScheduler()
            self.scheduler.start()
            self.logger.info("Scheduler initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize scheduler: {e}")

    async def _start_background_tasks(self):
        """Start background tasks."""
        if self.enabled_features["health_monitor"] and not self.safe_mode:
            # Start health monitor task
            asyncio.create_task(self._health_monitor_loop())

        if self.enabled_features["watchdog"] and not self.safe_mode:
            # Start watchdog task
            asyncio.create_task(self._watchdog_loop())

        # Start daily digest task
        asyncio.create_task(self._daily_digest_task())

        # Start birthday check task
        asyncio.create_task(self._birthday_check_loop())

    async def _health_monitor_loop(self):
        """Background health monitoring loop."""
        while self.is_ready():
            try:
                if self.db_manager:
                    # Check database connection
                    try:
                        await self.db_manager.get_connection()
                        await self.db_manager.log_health_check("database", "OK")
                    except Exception as e:
                        await self.db_manager.log_health_check(
                            "database", "CRITICAL", details=str(e)
                        )
                        # Set crash flag for recovery
                        await self.db_manager.set_flag(
                            "crash_detected", "database_connection_lost"
                        )

                # Check system resources
                sys_info = get_system_info()
                if sys_info:
                    if sys_info.get("cpu_percent", 0) > 80:
                        await self.db_manager.log_health_check(
                            "cpu",
                            "WARNING",
                            sys_info["cpu_percent"],
                            "High CPU usage detected",
                        )

                    if sys_info.get("memory_percent", 0) > 80:
                        await self.db_manager.log_health_check(
                            "memory",
                            "WARNING",
                            sys_info["memory_percent"],
                            "High memory usage detected",
                        )

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                self.logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def _watchdog_loop(self):
        """Background watchdog loop for monitoring bot health."""
        last_log_time = datetime.now()

        while self.is_ready():
            try:
                # Check if bot is responsive
                latency = self.latency
                if latency and latency > 3:  # 3 seconds for better responsiveness
                    await self.db_manager.log_health_check(
                        "latency", "CRITICAL", latency, "Bot appears to be unresponsive"
                    )
                    await self.db_manager.set_flag("crash_detected", "high_latency")

                # Check if logs are being updated
                current_time = datetime.now()
                if (current_time - last_log_time).total_seconds() > 300:  # 5 minutes
                    await self.db_manager.log_health_check(
                        "logs", "WARNING", details="No log updates detected recently"
                    )

                last_log_time = current_time
                await asyncio.sleep(settings.WATCHDOG_INTERVAL)

            except Exception as e:
                self.logger.error(f"Watchdog error: {e}")
                await asyncio.sleep(60)

    async def _daily_digest_task(self):
        """Daily digest task for owner notifications."""
        while True:
            try:
                # Calculate time until next daily digest
                now = datetime.now()
                digest_time = settings.OWNER_DAILY_DIGEST_TIME

                # Parse digest time (format: "HH:MM")
                try:
                    hour, minute = map(int, digest_time.split(":"))
                    next_digest = now.replace(
                        hour=hour, minute=minute, second=0, microsecond=0
                    )

                    if next_digest <= now:
                        next_digest += timedelta(days=1)

                    sleep_seconds = (next_digest - now).total_seconds()
                    await asyncio.sleep(sleep_seconds)

                    # Send daily digest
                    await self._send_daily_digest()

                except Exception as e:
                    self.logger.error(f"Error parsing digest time: {e}")
                    await asyncio.sleep(86400)  # Wait 24 hours and retry

            except Exception as e:
                self.logger.error(f"Daily digest error: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour and retry

    async def _birthday_check_loop(self):
        """Background loop for checking birthdays."""
        while True:
            try:
                # Check birthdays every hour
                await self._check_birthdays()
                await asyncio.sleep(3600)  # 1 hour

            except Exception as e:
                self.logger.error(f"Birthday check error: {e}")
                await asyncio.sleep(1800)  # Wait 30 minutes and retry

    async def _check_birthdays(self):
        """Check for birthdays today and send messages."""
        if not self.db_manager:
            return

        try:
            today_birthdays = await self.db_manager.get_today_birthdays()

            if today_birthdays:
                # Get birthday channel from settings
                birthday_channel_id = await self.db_manager.get_setting(
                    "birthday_channel_id"
                )

                if birthday_channel_id:
                    channel = self.get_channel(birthday_channel_id)
                    if channel:
                        for user_id in today_birthdays:
                            user = self.get_user(user_id)
                            if user:
                                embed = embed_helper.birthday_embed(
                                    title="Happy Birthday! 🎉",
                                    description=f"Happy birthday to {user.mention}! 🎂🎈",
                                    user=(
                                        user if hasattr(user, "display_name") else None
                                    ),
                                )

                                await safe_send_message(channel, embed=embed)

                                # Assign birthday role
                                await self._assign_birthday_role(user)

                                # Log celebration
                                await self.db_manager.log_event(
                                    category="BDAY",
                                    action="CELEBRATED",
                                    user_id=user_id,
                                    details="Automatic birthday celebration",
                                )

        except Exception as e:
            self.logger.error(f"Error checking birthdays: {e}")

    async def _assign_birthday_role(self, user: discord.Member):
        """Assign birthday role to user for 24 hours."""
        if not isinstance(user, discord.Member):
            return

        try:
            guild = user.guild

            # Get or create birthday role
            from config.constants import BIRTHDAY_ROLE_NAME

            birthday_role = discord.utils.get(guild.roles, name=BIRTHDAY_ROLE_NAME)

            if not birthday_role:
                # Create the role if it doesn't exist
                birthday_role = await guild.create_role(
                    name=BIRTHDAY_ROLE_NAME,
                    color=discord.Color.pink(),
                    reason="Birthday role for celebrations",
                )

            # Assign role
            await user.add_roles(birthday_role, reason="Birthday celebration")

            # Schedule role removal after 24 hours using persistent scheduler
            removal_time = datetime.now() + timedelta(hours=24)
            self.scheduler.add_job(
                self._remove_birthday_role,
                "date",
                run_date=removal_time,
                args=[user.id, birthday_role.id, guild.id],
                id=f"birthday_role_{user.id}_{int(datetime.now().timestamp())}",
                replace_existing=True,
            )

        except Exception as e:
            self.logger.error(f"Error assigning birthday role: {e}")

    async def _remove_birthday_role(self, user_id: int, role_id: int, guild_id: int):
        """Remove birthday role from user after 24 hours."""
        try:
            guild = self.get_guild(guild_id)
            if not guild:
                return
            user = guild.get_member(user_id)
            if not user:
                return
            role = guild.get_role(role_id)
            if not role:
                return
            if role in user.roles:
                await user.remove_roles(role, reason="Birthday period ended")
                await self.db_manager.log_event(
                    category="BDAY",
                    action="ROLE_REMOVED",
                    user_id=user_id,
                    details="Birthday role removed after 24 hours",
                )
        except Exception as e:
            self.logger.error(f"Error removing birthday role: {e}")

    async def _send_daily_digest(self):
        """Send daily digest to owner."""
        if not self.db_manager or not settings.OWNER_DAILY_DIGEST_ENABLED:
            return

        try:
            # Collect digest data
            uptime = (
                format_duration(int((datetime.now() - self.start_time).total_seconds()))
                if self.start_time
                else "Unknown"
            )

            # Get recent audit logs for statistics
            recent_logs = await self.db_manager.get_audit_logs(1000)
            stats = await self.db_manager.get_daily_digest_stats()

            digest_data = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "uptime": uptime,
                "active_users": len(
                    set(log["user_id"] for log in recent_logs if log["user_id"])
                ),
                "total_xp": sum(
                    1
                    for log in recent_logs
                    if log["category"] == "XP" and log["action"] == "GAIN"
                ),
                "birthdays": sum(
                    1
                    for log in recent_logs
                    if log["category"] == "BDAY" and log["action"] == "CELEBRATED"
                ),
                "total_logs": stats["total_logs"],
                "critical_events": stats["critical_events"],
                "warnings": stats["warnings"],
                "moderation_actions": stats["moderation_actions"],
                "user_events": stats["user_events"],
                "commands": stats["total_logs"],
                "restarts": sum(
                    1
                    for log in recent_logs
                    if log["category"] == "SYSTEM"
                    and log["action"] in ["STARTUP", "RESTART"]
                ),
                "errors": sum(
                    1
                    for log in recent_logs
                    if log["category"] == "SYSTEM" and "ERROR" in log["action"].upper()
                ),
                "memory": f"{get_system_info().get('memory_used_mb', 'Unknown')} MB",
                "db_size": system_helper.get_file_size(
                    settings.DATABASE_URL.replace("sqlite:///", "")
                ),
            }

            # Create digest embed
            embed = create_embed(
                title="🧩 MalaBoT Daily Digest",
                description=f"Summary for {digest_data['date']}",
                color=discord.Color.blue(),
            )

            embed.add_field(name="🕐 Uptime", value=digest_data["uptime"], inline=True)
            embed.add_field(
                name="🧠 Memory", value=f"{digest_data['memory']}", inline=True
            )
            embed.add_field(
                name="📈 XP Gained", value=str(digest_data["total_xp"]), inline=True
            )
            embed.add_field(
                name="🎂 Birthdays", value=str(digest_data["birthdays"]), inline=True
            )
            embed.add_field(
                name="♻️ Restarts", value=str(digest_data["restarts"]), inline=True
            )
            embed.add_field(
                name="⚙️ Errors", value=str(digest_data["errors"]), inline=True
            )
            embed.add_field(name="🔢 Version", value=settings.BOT_VERSION, inline=True)
            embed.add_field(
                name="💾 DB Size", value=digest_data["db_size"], inline=True
            )

            embed.set_footer(
                text=f"Report generated automatically • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            # Send to owner(s)
            for owner_id in settings.OWNER_IDS:
                owner = self.get_user(owner_id)
                if owner:
                    try:
                        await owner.send(embed=embed)
                    except discord.Forbidden:
                        self.logger.warning(f"Cannot send DM to owner {owner_id}")

            # Log digest
            log_system("Daily digest sent successfully")

        except Exception as e:
            self.logger.error(f"Error sending daily digest: {e}")

    async def on_ready(self):
        """Called when the bot is ready."""
        # Sync slash commands
        await self._sync_commands()

        # Log ready message
        startup_message = f"🟢 MalaBoT is now Locked in! — Locked in as {self.user} (ID: {self.user.id})"
        self.logger.info(startup_message)

        if self.safe_mode:
            self.logger.warning("⚠️ Running in Safe Mode - limited functionality")

        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="your server • /help"
            )
        )

    async def _sync_commands(self):
        """Sync slash commands to Discord (instant in debug guilds)."""
        try:
            # If DEBUG_GUILDS is set, ONLY sync to those guilds (local development)
            # This prevents duplicate commands (guild + global)
            if settings.DEBUG_GUILDS:
                self.logger.info(
                    "🔧 DEBUG MODE: Syncing only to debug guilds (no global sync)"
                )

                for guild_id in settings.DEBUG_GUILDS:
                    try:
                        guild = discord.Object(id=guild_id)
                        # Copy global commands to guild first
                        self.tree.copy_global_to(guild=guild)
                        # Debug: Check what commands are registered
                        guild_commands = self.tree.get_commands(guild=guild)
                        self.logger.info(
                            f"Commands in tree: {[cmd.name for cmd in guild_commands]}"
                        )
                        synced = await self.tree.sync(guild=guild)
                        self.logger.info(
                            f"✅ Synced {len(synced)} commands to debug guild: {guild_id}"
                        )
                    except Exception as e:
                        self.logger.error(
                            f"❌ Failed to sync to debug guild {guild_id}: {e}"
                        )
            else:
                # No DEBUG_GUILDS set = Production mode = Global sync only
                self.logger.info("🌐 PRODUCTION MODE: Syncing globally")
                synced = await self.tree.sync()
                self.logger.info(f"✅ Synced {len(synced)} global commands")

        except Exception as e:
            self.logger.error(f"❌ Command sync failed: {e}")

    async def on_guild_join(self, guild: discord.Guild):
        """Called when bot joins a new guild."""
        self.logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")

        # Log event to database
        if self.db_manager:
            await self.db_manager.log_event(
                category="SYSTEM",
                action="GUILD_JOIN",
                guild_id=guild.id,
                details=f"Joined guild: {guild.name}",
            )

    async def on_guild_remove(self, guild: discord.Guild):
        """Called when bot leaves a guild."""
        self.logger.info(f"Left guild: {guild.name} (ID: {guild.id})")

        # Log event to database
        if self.db_manager:
            await self.db_manager.log_event(
                category="SYSTEM",
                action="GUILD_LEAVE",
                guild_id=guild.id,
                details=f"Left guild: {guild.name}",
            )

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        """Global command error handler."""
        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.MissingPermissions):
            embed = embed_helper.error_embed(
                title="Permission Denied",
                description="You don't have permission to use this command.",
            )
            await safe_send_message(ctx.channel, embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.CommandOnCooldown):
            embed = embed_helper.error_embed(
                title="Command on Cooldown",
                description=f"Please wait {error.retry_after:.1f} seconds before using this command again.",
            )
            await safe_send_message(ctx.channel, embed=embed, ephemeral=True)
            return

        # Log unexpected errors
        self.logger.error(f"Command error in {ctx.command}: {error}")
        log_critical(f"Command error in {ctx.command}", error)

        embed = embed_helper.error_embed(
            title="Command Error",
            description="An unexpected error occurred. Please try again later.",
        )
        await safe_send_message(ctx.channel, embed=embed, ephemeral=True)

    async def shutdown(self):
        """Graceful shutdown."""
        self.logger.info("Initiating graceful shutdown...")

        try:
            # Log shutdown event first (before closing database)
            if self.db_manager:
                try:
                    await self.db_manager.log_event(
                        category="SYSTEM",
                        action="SHUTDOWN",
                        details="Graceful shutdown initiated",
                    )
                except Exception as e:
                    self.logger.warning(f"Could not log shutdown event: {e}")

            # Shutdown scheduler
            if self.scheduler:
                try:
                    self.scheduler.shutdown(wait=False)
                    self.logger.info("Scheduler shutdown complete")
                except Exception as e:
                    self.logger.warning(f"Error shutting down scheduler: {e}")

            # Close Discord connection
            try:
                await self.close()
                self.logger.info("Discord connection closed")
            except Exception as e:
                self.logger.warning(f"Error closing Discord connection: {e}")

            # Close database connection (do this last to ensure all operations complete)
            if self.db_manager:
                try:
                    await self.db_manager.close()
                    self.logger.info("Database connection closed")
                except Exception as e:
                    self.logger.warning(f"Error closing database: {e}")

            self.logger.info("Graceful shutdown completed")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

        finally:
            # Force exit if needed
            sys.exit(0)

    async def health_check(self) -> dict:
        """Return bot health status for monitoring"""
        return {
            "status": "healthy" if self.is_ready() else "starting",
            "uptime": (
                (datetime.now() - self.start_time).total_seconds()
                if self.start_time
                else 0
            ),
            "latency_ms": round(self.latency * 1000),
            "guilds": len(self.guilds),
            "users": sum(g.member_count for g in self.guilds),
            "cogs_loaded": len(self.cogs),
            "database": self.db_manager is not None,
            "version": settings.BOT_VERSION,
        }


def main():
    """Main entry point."""
    # Validate settings
    errors = settings.validate()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    # Create and run bot
    bot = MalaBoT()

    try:
        bot.run(settings.DISCORD_TOKEN)
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
