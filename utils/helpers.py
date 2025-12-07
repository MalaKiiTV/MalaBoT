"""
Helper utilities for MalaBoT
Provides various helper classes and functions for common operations
"""

import os
import platform
from datetime import UTC, datetime, timedelta
from typing import Any

import discord
import psutil

from config.constants import COLORS
from utils.logger import get_logger

logger = get_logger(__name__)


class EmbedHelper:
    """Helper class for creating consistent embeds."""

    @staticmethod
    def create_embed(
        title: str,
        description: str | None = None,
        color: int = COLORS["info"],
        thumbnail: str | None = None,
        **kwargs,
    ) -> discord.Embed:
        """Create a standardized embed with consistent formatting."""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now(UTC),
        )

        # Add thumbnail if provided
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

        # Add any additional fields from kwargs
        if "footer" in kwargs:
            embed.set_footer(text=kwargs["footer"])
        if "image" in kwargs:
            embed.set_image(url=kwargs["image"])
        if "author" in kwargs:
            embed.set_author(name=kwargs["author"])

        return embed

    @staticmethod
    def error_embed(title: str, description: str) -> discord.Embed:
        """Create an error embed with red color."""
        return EmbedHelper.create_embed(title, description, COLORS["error"])

    @staticmethod
    def success_embed(title: str, description: str) -> discord.Embed:
        """Create a success embed with green color."""
        return EmbedHelper.create_embed(title, description, COLORS["success"])

    @staticmethod
    def info_embed(title: str, description: str) -> discord.Embed:
        """Create an info embed with blue color."""
        return EmbedHelper.create_embed(title, description, COLORS["info"])

    @staticmethod
    def warning_embed(title: str, description: str) -> discord.Embed:
        """Create a warning embed with orange color."""
        return EmbedHelper.create_embed(title, description, COLORS["warning"])

    @staticmethod
    def roast_embed(title: str, description: str) -> discord.Embed:
        """Create a roast embed with orange color."""
        return EmbedHelper.create_embed(title, description, COLORS["warning"])


class TimeHelper:
    """Helper class for time-related operations."""

    @staticmethod
    def format_duration(td) -> str:
        """Format duration (timedelta or seconds) to human-readable string."""
        # If it's a timedelta object, convert to seconds
        if isinstance(td, datetime):
            # If a datetime object is passed, calculate difference from now
            td = datetime.now(UTC) - td
        if hasattr(td, "total_seconds"):
            seconds = int(td.total_seconds())
        else:
            # If already an integer/float, use as seconds
            seconds = int(td)

        if seconds < 60:
            return f"{seconds}s"
        if seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m {seconds % 60}s"
        if seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        return f"{days}d {hours}h {minutes}m"

    @staticmethod
    def get_discord_timestamp(dt: datetime, style: str = "R") -> str:
        """
        Convert datetime to Discord timestamp format.
        Styles: t (short time), T (long time), d (short date), D (long date),
                f (short datetime), F (long datetime), R (relative)
        """
        if dt is None:
            return "Unknown"

        timestamp = int(dt.timestamp())
        return f"<t:{timestamp}:{style}>"


class PermissionHelper:
    """Helper class for permission-related operations."""

    @staticmethod
    def is_owner(user: discord.User) -> bool:
        """Check if user is a bot owner."""
        from config.settings import settings

        return str(user.id) in settings.OWNER_IDS

    @staticmethod
    def is_admin(member: discord.Member) -> bool:
        """Check if member has administrator permissions."""
        return member.guild_permissions.administrator


class CooldownHelper:
    """Helper class for cooldown management."""

    def __init__(self):
        self.cooldowns = {}

    def is_on_cooldown(self, user_id: int, command: str) -> bool:
        """Check if user is on cooldown for a command."""
        key = f"{user_id}_{command}"
        if key in self.cooldowns:
            return datetime.now(UTC) < self.cooldowns[key]
        return False

    def set_cooldown(self, user_id: int, command: str, seconds: int | None = None):
        """Set a cooldown for a user on a command."""
        if seconds is None:
            # Import here to avoid circular dependency
            from config.constants import COMMAND_COOLDOWNS

            seconds = COMMAND_COOLDOWNS.get(command, 5)

        key = f"{user_id}_{command}"
        self.cooldowns[key] = datetime.now(UTC) + timedelta(seconds=seconds)

    def get_remaining_cooldown(self, user_id: int, command: str) -> int:
        """Get remaining cooldown time in seconds."""
        key = f"{user_id}_{command}"
        if key in self.cooldowns:
            remaining = (self.cooldowns[key] - datetime.now(UTC)).total_seconds()
            return max(0, int(remaining))
        return 0

    def check_cooldown(self, user_id: int, command: str, cooldown_seconds: int) -> bool:
        """
        Check if user can use a command (not on cooldown).
        If not on cooldown, automatically sets the cooldown.
        Returns True if command can be used, False if on cooldown.
        """
        if self.is_on_cooldown(user_id, command):
            return False

        # Not on cooldown, set it now
        self.set_cooldown(user_id, command, cooldown_seconds)
        return True


class SystemHelper:
    """Helper class for system-related operations."""

    @staticmethod
    def get_system_info() -> dict[str, Any]:
        """Get system information."""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()

        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "platform_release": platform.release(),
            "cpu_count": psutil.cpu_count(),
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": memory_info.rss / 1024 / 1024,  # MB
            "memory_percent": process.memory_percent(),
            "disk_usage": psutil.disk_usage("/"),
            "boot_time": datetime.fromtimestamp(psutil.boot_time(), tz=UTC).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

    @staticmethod
    def sanitize_input(text: str, max_length: int = 200) -> str:
        """Sanitize user input by removing potentially harmful characters and limiting length."""
        if not text:
            return ""

        # Remove null bytes and other control characters
        text = "".join(char for char in text if ord(char) >= 32 or char in "\n\r\t")

        # Limit length
        if len(text) > max_length:
            text = text[:max_length]

        # Strip leading/trailing whitespace
        text = text.strip()

        return text


# Convenience instances
embed_helper = EmbedHelper()
time_helper = TimeHelper()
permission_helper = PermissionHelper()
cooldown_helper = CooldownHelper()
system_helper = SystemHelper()


# Convenience functions
def create_embed(*args, **kwargs) -> discord.Embed:
    return embed_helper.create_embed(*args, **kwargs)


def format_duration(seconds) -> str:
    return time_helper.format_duration(seconds)


def is_owner(user: discord.User) -> bool:
    return permission_helper.is_owner(user)


def is_admin(member: discord.Member) -> bool:
    return permission_helper.is_admin(member)


def get_system_info() -> dict[str, Any]:
    return system_helper.get_system_info()


async def is_mod(
    interaction: discord.Interaction,
    db_manager,
    specific_mod_role_key: str | None = None,
) -> bool:
    """
    Check if user has mod permissions.

    Args:
        interaction: The Discord interaction
        db_manager: Database manager instance
        specific_mod_role_key: Optional specific mod role key (e.g., 'verification_mod_role')
                               If provided, checks this role first, then falls back to general mod role

    Returns:
        bool: True if user is bot owner, server owner, administrator, or has mod role
    """
    # Bot owner always has access
    if is_owner(interaction.user):
        return True

    guild_id = interaction.guild_id
    if not guild_id:
        return False

    # Server owner always has access
    if interaction.guild.owner_id == interaction.user.id:
        return True

    # Administrator always has access
    if interaction.user.guild_permissions.administrator:
        return True

    # Check specific mod role first if provided
    if specific_mod_role_key:
        specific_role_id = await db_manager.get_setting(
            f"{specific_mod_role_key}_{guild_id}"
        )
        if specific_role_id:
            specific_role = interaction.guild.get_role(int(specific_role_id))
            if specific_role and specific_role in interaction.user.roles:
                return True

    # Fall back to general mod role
    mod_role_id = await db_manager.get_setting(f"mod_role_{guild_id}")
    if not mod_role_id:
        return False

    mod_role = interaction.guild.get_role(int(mod_role_id))
    if not mod_role:
        return False

    return mod_role in interaction.user.roles


async def check_mod_permission(
    interaction: discord.Interaction,
    db_manager,
    specific_mod_role_key: str | None = None,
) -> bool:
    """
    Check mod permission and send error message if denied.

    Args:
        interaction: The Discord interaction
        db_manager: Database manager instance
        specific_mod_role_key: Optional specific mod role key

    Returns:
        bool: True if user has permission, False otherwise (and sends error message)
    """
    if await is_mod(interaction, db_manager, specific_mod_role_key):
        return True

    # Get role names for error message
    role_names = []
    guild_id = interaction.guild_id

    if specific_mod_role_key:
        specific_role_id = await db_manager.get_setting(
            f"{specific_mod_role_key}_{guild_id}"
        )
        if specific_role_id:
            specific_role = interaction.guild.get_role(int(specific_role_id))
            if specific_role:
                role_names.append(specific_role.name)

    mod_role_id = await db_manager.get_setting(f"mod_role_{guild_id}")
    if mod_role_id:
        mod_role = interaction.guild.get_role(int(mod_role_id))
        if mod_role:
            role_names.append(mod_role.name)

    role_list = (
        "\n".join([f"• {name}" for name in role_names])
        if role_names
        else "• No mod role configured"
    )

    is_server_owner = interaction.guild.owner_id == interaction.user.id
    is_administrator = interaction.user.guild_permissions.administrator

    embed = embed_helper.error_embed(
        title="🚫 Permission Denied",
        description=f"This command is only available to:\n\n"
        f"• Bot Owners\n"
        f"• Server Owner\n"
        f"• Administrators\n"
        f"• Users with mod role:\n{role_list}\n\n"
        f"Your current permissions:\n"
        f"• Bot Owner: {'✅' if is_owner(interaction.user) else '❌'}\n"
        f"• Server Owner: {'✅' if is_server_owner else '❌'}\n"
        f"• Administrator: {'✅' if is_administrator else '❌'}",
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
    return False


async def safe_send_message(
    channel, content=None, embed=None, ephemeral=False, **kwargs
):
    """Safely send a message to a channel with error handling."""
    try:
        if hasattr(channel, "send"):  # Regular channel
            return await channel.send(content=content, embed=embed, **kwargs)
        if hasattr(channel, "followup"):  # Interaction followup
            return await channel.followup.send(
                content=content, embed=embed, ephemeral=ephemeral, **kwargs
            )
        # Assume it's an interaction
        if ephemeral:
            return await channel.response.send_message(
                content=content, embed=embed, ephemeral=True, **kwargs
            )
        return await channel.response.send_message(
            content=content, embed=embed, **kwargs
        )
    except discord.Forbidden:
        # Bot doesn't have permission to send messages in this channel
        logger.warning(f"Missing permissions to send message in {channel}")
        return None
    except discord.HTTPException as e:
        # Other Discord API errors
        logger.error(f"Failed to send message: {e}")
        return None
    except Exception as e:
        # Any other errors
        logger.exception(f"Unexpected error when sending message: {e}")
        return None


async def is_staff(interaction: discord.Interaction, db_manager) -> bool:
    """Check if user has staff permissions (alias for is_mod)."""
    return await is_mod(interaction, db_manager)


async def check_staff_permission(interaction: discord.Interaction, db_manager) -> bool:
    """Check staff permission and send error message if denied."""
    return await check_mod_permission(interaction, db_manager)


def is_mod_decorator(specific_mod_role_key: str | None = None):
    """
    Decorator for checking mod permissions.

    Args:
        specific_mod_role_key: Optional specific mod role key to check first

    Usage:
        @app_commands.command()
        @is_mod_decorator()
        async def my_command(interaction: discord.Interaction):
            await interaction.response.send_message("You have mod permissions!")

        @app_commands.command()
        @is_mod_decorator('verification_mod_role')
        async def verification_command(interaction: discord.Interaction):
            await interaction.response.send_message("You have verification mod permissions!")
    """

    def decorator(func):
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            # Get the bot instance from the interaction
            bot = interaction.client
            if not hasattr(bot, "db_manager"):
                await interaction.response.send_message(
                    embed=embed_helper.error_embed(
                        "❌ Database Error", "Database manager not available."
                    ),
                    ephemeral=True,
                )
                return

            if await is_mod(interaction, bot.db_manager, specific_mod_role_key):
                return await func(interaction, *args, **kwargs)
            await check_mod_permission(
                interaction, bot.db_manager, specific_mod_role_key
            )
            return

        return wrapper

    return decorator


def is_staff_decorator():
    """
    Decorator for checking staff permissions (alias for is_mod).

    Usage:
        @app_commands.command()
        @is_staff_decorator()
        async def my_command(interaction: discord.Interaction):
            await interaction.response.send_message("You have staff permissions!")
    """
    return is_mod_decorator()


def xp_helper(xp: int) -> dict:
    """Helper function for XP calculations."""
    from config.constants import XP_TABLE

    # Find current level based on XP
    level = 1
    for lvl in sorted(XP_TABLE.keys()):
        if xp >= XP_TABLE[lvl]:
            level = lvl
        else:
            break

    # Get XP thresholds
    current_level_xp = XP_TABLE.get(level, 0)
    next_level = level + 1

    # Find next level in table
    while next_level not in XP_TABLE and next_level <= max(XP_TABLE.keys()):
        next_level += 1

    next_level_xp = XP_TABLE.get(next_level, current_level_xp)
    xp_needed = max(0, next_level_xp - xp)
    xp_progress = xp - current_level_xp
    xp_total_for_level = next_level_xp - current_level_xp

    return {
        "level": level,
        "current_level_xp": current_level_xp,
        "next_level_xp": next_level_xp,
        "xp_needed": xp_needed,
        "xp_progress": xp_progress,
        "xp_total_for_level": xp_total_for_level,
        "xp_percentage": (
            (xp_progress / xp_total_for_level * 100) if xp_total_for_level > 0 else 100
        ),
    }
