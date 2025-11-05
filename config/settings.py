"""
Configuration settings loader for MalaBoT.
Handles environment variables and provides centralized configuration access.
"""

import os
from typing import Optional

from dotenv import load_dotenv


class Settings:
    """Centralized settings management for MalaBoT."""

    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Discord Configuration
        self.DISCORD_TOKEN: str = os.getenv('DISCORD_TOKEN', '')
        self.BOT_PREFIX: str = os.getenv('BOT_PREFIX', '/')
        self.BOT_NAME: str = os.getenv('BOT_NAME', 'MalaBoT')
        self.BOT_VERSION: str = os.getenv('BOT_VERSION', '1.0.0')
        self.OWNER_IDS: list[int] = self._parse_int_list(os.getenv('OWNER_IDS', ''))
        self.DEVELOPER_IDS: list[int] = self._parse_int_list(os.getenv('DEVELOPER_IDS', ''))
        self.DEBUG_GUILDS: list[int] = self._parse_int_list(os.getenv('DEBUG_GUILDS', ''))
        self.DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///data/bot.db')

        # Logging Configuration
        self.LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE: str = os.getenv('LOG_FILE', 'data/logs/bot.log')
        self.ENABLE_STARTUP_VERIFICATION: bool = self._parse_bool(os.getenv('ENABLE_STARTUP_VERIFICATION', 'true'))
        self.ENABLE_AUTO_REPAIR: bool = self._parse_bool(os.getenv('ENABLE_AUTO_REPAIR', 'true'))

        # Feature Flags
        self.ENABLE_MUSIC: bool = self._parse_bool(os.getenv('ENABLE_MUSIC', 'false'))
        self.ENABLE_MODERATION: bool = self._parse_bool(os.getenv('ENABLE_MODERATION', 'true'))
        self.ENABLE_FUN: bool = self._parse_bool(os.getenv('ENABLE_FUN', 'true'))
        self.ENABLE_UTILITY: bool = self._parse_bool(os.getenv('ENABLE_UTILITY', 'true'))
        self.ENABLE_SAFE_MODE: bool = self._parse_bool(os.getenv('ENABLE_SAFE_MODE', 'true'))

        # Owner Notifications
        self.OWNER_ALERTS_ENABLED: bool = self._parse_bool(os.getenv('OWNER_ALERTS_ENABLED', 'true'))
        self.OWNER_DAILY_DIGEST_ENABLED: bool = self._parse_bool(os.getenv('OWNER_DAILY_DIGEST_ENABLED', 'true'))
        self.OWNER_DAILY_DIGEST_TIME: str = os.getenv('OWNER_DAILY_DIGEST_TIME', '00:00')
        self.OWNER_STATUS_CHANNEL_ID: Optional[int] = self._parse_int(os.getenv('OWNER_STATUS_CHANNEL_ID'))

        # Health & Monitoring
        self.ENABLE_HEALTH_MONITOR: bool = self._parse_bool(os.getenv('ENABLE_HEALTH_MONITOR', 'true'))
        self.ENABLE_WATCHDOG: bool = self._parse_bool(os.getenv('ENABLE_WATCHDOG', 'true'))
        self.WATCHDOG_INTERVAL: int = int(os.getenv('WATCHDOG_INTERVAL', '60'))
        self.WATCHDOG_RESTART_DELAY: int = int(os.getenv('WATCHDOG_RESTART_DELAY', '5'))

        # API Keys
        self.WEATHER_API_KEY: str = os.getenv('WEATHER_API_KEY', '')
        self.YOUTUBE_API_KEY: str = os.getenv('YOUTUBE_API_KEY', '')
        self.REDDIT_API_KEY: str = os.getenv('REDDIT_API_KEY', '')

    def _parse_bool(self, value: str) -> bool:
        """Parse string to boolean."""
        return value.lower() in ('true', '1', 'yes', 'on')

    def _parse_int(self, value: str) -> Optional[int]:
        """Parse string to integer, return None if invalid."""
        try:
            return int(value) if value else None
        except ValueError:
            return None

    def _parse_int_list(self, value: str) -> list[int]:
        """Parse comma-separated string to list of integers."""
        if not value:
            return []
        try:
            return [int(x.strip()) for x in value.split(',') if x.strip()]
        except ValueError:
            return []

    def validate(self) -> list[str]:
        """Validate critical settings and return list of errors."""
        errors = []

        if not self.DISCORD_TOKEN:
            errors.append("DISCORD_TOKEN is required")

        if not self.OWNER_IDS:
            errors.append("OWNER_IDS must contain at least one owner ID")

        return errors

# Global settings instance
settings = Settings()
