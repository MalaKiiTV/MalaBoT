"""
Advanced logging system for MalaBoT with colorized output, rotation, and multiple log files.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional

import colorlog

from config.settings import settings


class MalaBotLogger:
    """Advanced logging system with colorized output and rotation."""

    def __init__(self):
        self.loggers = {}
        self.setup_logging()

    def setup_logging(self):
        """Set up all logging handlers and formatters."""
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

        # Set up colorlog formatter for console
        color_formatter = colorlog.ColoredFormatter(
            '%(log_color)s[%(asctime)s][%(name)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={},
            style='%'
        )

        # Set up file formatter
        file_formatter = logging.Formatter(
            '[%(asctime)s][%(name)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

        # Console handler with colors
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setFormatter(color_formatter)
        root_logger.addHandler(console_handler)

        # Main bot log file with rotation
        bot_handler = logging.handlers.RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        bot_handler.setFormatter(file_formatter)
        root_logger.addHandler(bot_handler)

        # System log file for critical events
        system_log_path = settings.LOG_FILE.replace('bot.log', 'system.log')
        system_handler = logging.handlers.RotatingFileHandler(
            system_log_path,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        system_handler.setFormatter(file_formatter)

        # Create system logger
        system_logger = logging.getLogger('system')
        system_logger.addHandler(system_handler)
        system_logger.setLevel(logging.INFO)
        self.loggers['system'] = system_logger

        # Moderation log file
        mod_log_path = settings.LOG_FILE.replace('bot.log', 'moderation.log')
        mod_handler = logging.handlers.RotatingFileHandler(
            mod_log_path,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        mod_handler.setFormatter(file_formatter)

        # Create moderation logger
        mod_logger = logging.getLogger('moderation')
        mod_logger.addHandler(mod_handler)
        mod_logger.setLevel(logging.INFO)
        self.loggers['moderation'] = mod_logger

        # Latest log file (live output)
        latest_log_path = settings.LOG_FILE.replace('bot.log', 'latest.log')
        latest_handler = logging.FileHandler(
            latest_log_path,
            mode='w',  # Overwrite each session
            encoding='utf-8'
        )
        latest_handler.setFormatter(file_formatter)

        # Create latest logger
        latest_logger = logging.getLogger('latest')
        latest_logger.addHandler(latest_handler)
        latest_logger.setLevel(logging.DEBUG)
        self.loggers['latest'] = latest_logger

        # Also add latest handler to root logger for complete capture
        root_logger.addHandler(latest_handler)

        # Suppress noisy third-party loggers
        logging.getLogger('discord').setLevel(logging.WARNING)
        logging.getLogger('websockets').setLevel(logging.WARNING)
        logging.getLogger('asyncio').setLevel(logging.WARNING)

    def get_logger(self, name: str = 'bot') -> logging.Logger:
        """Get a logger instance with the specified name."""
        if name in self.loggers:
            return self.loggers[name]
        return logging.getLogger(name)

    def log_system_event(self, message: str, level: str = 'info'):
        """Log a system event to system.log."""
        logger = self.loggers['system']
        getattr(logger, level)(message)

    def log_moderation_event(self, message: str, level: str = 'info'):
        """Log a moderation event to moderation.log."""
        logger = self.loggers['moderation']
        getattr(logger, level)(message)

    def log_critical_error(self, message: str, exception: Optional[Exception] = None):
        """Log a critical error to all log files."""
        self.get_logger('system').critical(message)
        self.get_logger('bot').critical(message)

        if exception:
            self.get_logger('system').critical(f"Exception details: {str(exception)}")
            self.get_logger('bot').critical(f"Exception details: {str(exception)}")

    def create_startup_log(self) -> str:
        """Create startup log entry with system info."""
        startup_info = f"""
{'='*60}
MalaBoT Startup Report
{'='*60}
Version: {settings.BOT_VERSION}
Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Log Level: {settings.LOG_LEVEL}
Database: {settings.DATABASE_URL}
Owner IDs: {settings.OWNER_IDS}
Debug Guilds: {settings.DEBUG_GUILDS}
Features Enabled:
  - Music: {settings.ENABLE_MUSIC}
  - Moderation: {settings.ENABLE_MODERATION}
  - Fun: {settings.ENABLE_FUN}
  - Utility: {settings.ENABLE_UTILITY}
  - Safe Mode: {settings.ENABLE_SAFE_MODE}
  - Health Monitor: {settings.ENABLE_HEALTH_MONITOR}
  - Watchdog: {settings.ENABLE_WATCHDOG}
{'='*60}
"""
        self.log_system_event(startup_info, 'info')
        return startup_info

    def create_shutdown_log(self, uptime: str = "Unknown"):
        """Create shutdown log entry."""
        shutdown_info = f"""
{'='*60}
MalaBoT Shutdown Report
{'='*60}
Shutdown Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Uptime: {uptime}
Status: Clean Shutdown
{'='*60}
"""
        self.log_system_event(shutdown_info, 'info')

    def log_crash_report(self, error_details: str, restart_reason: str = "Unknown"):
        """Create crash report log."""
        crash_info = f"""
{'!'*60}
CRASH REPORT - MALABOT UNEXPECTED SHUTDOWN
{'!'*60}
Crash Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Restart Reason: {restart_reason}
Error Details:
{error_details}
{'!'*60}
"""
        self.log_system_event(crash_info, 'critical')
        self.get_logger('bot').critical(crash_info)

        # Create crash report file
        crash_file_path = settings.LOG_FILE.replace('bot.log', f'crash_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        try:
            with open(crash_file_path, 'w', encoding='utf-8') as f:
                f.write(crash_info)
        except Exception as e:
            self.get_logger('system').error(f"Failed to create crash report file: {e}")

    def log_startup_verification(self, verification_results: dict):
        """Log startup verification results."""
        from config.constants import SYSTEM_MESSAGES
        verification_info = f"""
{SYSTEM_MESSAGES['startup_verification']}
Environment Check: {'✅ PASS' if verification_results.get('environment') else '❌ FAIL'}
Directory Check: {'✅ PASS' if verification_results.get('directories') else '❌ FAIL'}
Log File Check: {'✅ PASS' if verification_results.get('log_files') else '❌ FAIL'}
Database Check: {'✅ PASS' if verification_results.get('database') else '❌ FAIL'}
Details: {verification_results.get('details', 'No additional details')}
Verification Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
        self.log_system_event(verification_info, 'info')

    def log_daily_digest(self, digest_data: dict):
        """Log daily digest report."""
        from config.constants import SYSTEM_MESSAGES
        digest_info = f"""
{SYSTEM_MESSAGES['daily_digest']}
Digest Date: {digest_data.get('date', 'Unknown')}
Uptime: {digest_data.get('uptime', 'Unknown')}
Users Active: {digest_data.get('active_users', 0)}
XP Gained: {digest_data.get('total_xp', 0)}
Birthdays: {digest_data.get('birthdays', 0)}
Commands Run: {digest_data.get('commands', 0)}
Restarts: {digest_data.get('restarts', 0)}
Errors: {digest_data.get('errors', 0)}
Memory Usage: {digest_data.get('memory', 'Unknown MB')}
DB Size: {digest_data.get('db_size', 'Unknown MB')}
Version: {settings.BOT_VERSION}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
        self.log_system_event(digest_info, 'info')

    def log_watchdog_event(self, event_type: str, details: str):
        """Log watchdog events."""
        from config.constants import SYSTEM_MESSAGES
        watchdog_info = f"""
{SYSTEM_MESSAGES['watchdog_report']}
Event Type: {event_type}
Details: {details}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
        self.log_system_event(watchdog_info, 'warning')

    def log_health_check(self, check_type: str, status: str, value: float = None, details: str = None):
        """Log health check results."""
        health_info = f"[HEALTH] {check_type}: {status}"
        if value is not None:
            health_info += f" (Value: {value})"
        if details:
            health_info += f" - {details}"

        if status == "CRITICAL":
            self.log_system_event(health_info, 'critical')
        elif status == "WARNING":
            self.log_system_event(health_info, 'warning')
        else:
            self.log_system_event(health_info, 'info')

# Global logger instance
logger_manager = MalaBotLogger()

# Convenience functions
def get_logger(name: str = 'bot') -> logging.Logger:
    """Get logger instance."""
    return logger_manager.get_logger(name)

def log_system(message: str, level: str = 'info'):
    """Log to system log."""
    logger_manager.log_system_event(message, level)

def log_moderation(message: str, level: str = 'info'):
    """Log to moderation log."""
    logger_manager.log_moderation_event(message, level)

def log_critical(message: str, exception: Optional[Exception] = None):
    """Log critical error."""
    logger_manager.log_critical_error(message, exception)

def log_startup_verification(results: dict):
    """Log startup verification."""
    logger_manager.log_startup_verification(results)

def log_daily_digest(data: dict):
    """Log daily digest."""
    logger_manager.log_daily_digest(data)

def log_watchdog(event_type: str, details: str):
    """Log watchdog event."""
    logger_manager.log_watchdog_event(event_type, details)

def log_health_check(check_type: str, status: str, value: float = None, details: str = None):
    """Log health check."""
    logger_manager.log_health_check(check_type, status, value, details)

def log_xp(message: str):
    """Log XP-related actions."""
    logger_manager.get_logger('bot').info(f"[XP] {message}")

def log_birthday(message: str):
    """Log birthday-related actions."""
    logger_manager.get_logger('bot').info(f"[BIRTHDAY] {message}")
