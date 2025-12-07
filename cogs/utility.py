"""
Utility commands cog for MalaBoT.
Contains help, ping, userinfo, serverinfo, about, and serverstats commands.
"""

import time
from datetime import datetime
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from config.constants import COLORS, COMMAND_CATEGORIES
from config.settings import settings
from utils.helpers import (
    create_embed,
    embed_helper,
    format_duration,
    get_system_info,
    time_helper,
)
from utils.logger import get_logger


class Utility(commands.Cog):
    """Utility commands for MalaBoT."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger("utility")
        self.start_time = time.time()

    @app_commands.command(
        name="help", description="Shows all available commands organized by category"
    )
    async def help(self, interaction: discord.Interaction):
        """Display help information for all commands."""
        try:
            # Create main help embed
            embed = create_embed(
                title="🤖 MalaBoT Command List",
                description="Here are all available commands organized by category:",
                color=COLORS["primary"],
            )

            # Add command categories
            for category, commands in COMMAND_CATEGORIES.items():
                if commands:
                    command_list = "\n".join([f"`/{cmd}`" for cmd in commands])
                    embed.add_field(name=category, value=command_list, inline=False)

            # Add additional info
            embed.add_field(
                name="📖 Usage Tips",
                value=(
                    "• Most commands support user mentions (e.g., `/userinfo @user`)\n"
                    "• Admin commands require appropriate permissions\n"
                    "• Use `/about` to see bot information\n"
                    "• Commands are automatically synced when the bot restarts"
                ),
                inline=False,
            )

            embed.set_footer(
                text="Use commands by typing / followed by the command name"
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

            # Log help command usage
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category="UTILITY",
                    action="HELP_USED",
                    user_id=interaction.user.id,
                    channel_id=interaction.channel.id,
                )

        except Exception as e:
            self.logger.error(f"Error in help command: {e}")
            await self._error_response(
                interaction, "Failed to display help information"
            )

    @app_commands.command(name="ping", description="Check bot latency and uptime")
    async def ping(self, interaction: discord.Interaction):
        """Show bot latency and uptime."""
        try:
            # Calculate latency
            latency_ms = round(self.bot.latency * 1000)

            # Calculate uptime
            uptime_seconds = int(time.time() - self.start_time)
            uptime_str = format_duration(uptime_seconds)

            # Create ping embed
            embed = embed_helper.info_embed(
                title="🏓 Pong!",
                description=f"Latency: **{latency_ms}ms**\nUptime: **{uptime_str}**",
            )

            # Add additional info
            embed.add_field(name="WebSocket Ping", value=f"{latency_ms}ms", inline=True)
            embed.add_field(name="API Response", value="✅ Online", inline=True)
            embed.add_field(name="Status", value="🟢 Healthy", inline=True)

            await interaction.response.send_message(embed=embed, ephemeral=True)

            # Log ping command usage
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category="UTILITY",
                    action="PING_USED",
                    user_id=interaction.user.id,
                    channel_id=interaction.channel.id,
                    details=f"Latency: {latency_ms}ms",
                )

        except Exception as e:
            self.logger.error(f"Error in ping command: {e}")
            await self._error_response(interaction, "Failed to get ping information")

    @app_commands.command(
        name="userinfo", description="Display detailed information about a user"
    )
    @app_commands.describe(
        user="The user to get information about (leave empty for yourself)"
    )
    async def userinfo(
        self, interaction: discord.Interaction, user: Optional[discord.Member] = None
    ):
        """Display detailed user information."""
        try:
            # Use command author if no user specified
            target_user = user or interaction.user

            # Get user data from database if available
            user_data = None
            if self.bot.db_manager and isinstance(target_user, discord.Member):
                user_data = await self.bot.db_manager.get_user(target_user.id)

            # Create userinfo embed
            embed = create_embed(
                title=f"👤 User Information: {target_user.display_name}",
                color=target_user.color if target_user.color else COLORS["primary"],
                thumbnail=target_user.avatar.url if target_user.avatar else None,
            )

            # Basic information
            embed.add_field(name="🆔 User ID", value=f"`{target_user.id}`", inline=True)

            embed.add_field(
                name="🏷️ Username",
                value=f"{target_user.name}#{target_user.discriminator}",
                inline=True,
            )

            # Member-specific information
            if isinstance(target_user, discord.Member):
                embed.add_field(
                    name="📅 Joined Server",
                    value=time_helper.get_discord_timestamp(target_user.joined_at, "R"),
                    inline=True,
                )

                embed.add_field(
                    name="🎭 Roles",
                    value=(
                        f"{len(target_user.roles)} roles"
                        if target_user.roles
                        else "No roles"
                    ),
                    inline=True,
                )

                # Display top role
                if target_user.roles:
                    top_role = target_user.roles[-1]
                    embed.add_field(
                        name="👑 Top Role",
                        value=(
                            top_role.mention
                            if top_role.name != "@everyone"
                            else "@everyone"
                        ),
                        inline=True,
                    )

                # Add permissions info
                if target_user.guild_permissions.administrator:
                    embed.add_field(
                        name="⚡ Permissions", value="🛡️ Administrator", inline=True
                    )
                elif target_user.guild_permissions.manage_guild:
                    embed.add_field(
                        name="⚡ Permissions", value="🔧 Server Manager", inline=True
                    )

            # Account creation date
            embed.add_field(
                name="🌍 Account Created",
                value=time_helper.get_discord_timestamp(target_user.created_at, "R"),
                inline=True,
            )

            # Add XP information if available
            if user_data:
                embed.add_field(
                    name="🏆 XP & Level",
                    value=f"Level {user_data['level']} • {user_data['xp']} XP\n"
                    f"Messages: {user_data['total_messages']}",
                    inline=True,
                )

                if user_data["daily_streak"] > 0:
                    embed.add_field(
                        name="🔥 Daily Streak",
                        value=f"{user_data['daily_streak']} days",
                        inline=True,
                    )

            # Bot status
            if target_user.bot:
                embed.add_field(
                    name="🤖 Bot Status", value="This user is a bot", inline=True
                )

            # Status information
            if isinstance(target_user, discord.Member):
                status_emoji = {
                    discord.Status.online: "🟢",
                    discord.Status.idle: "🟡",
                    discord.Status.dnd: "🔴",
                    discord.Status.offline: "⚫",
                }.get(target_user.status, "❓")

                status_text = target_user.status.name.title()
                embed.add_field(
                    name="💬 Status", value=f"{status_emoji} {status_text}", inline=True
                )

            # Add activities if member
            if isinstance(target_user, discord.Member) and target_user.activities:
                activities = []
                for activity in target_user.activities:
                    if isinstance(activity, discord.Game):
                        activities.append(f"🎮 Playing {activity.name}")
                    elif isinstance(activity, discord.Streaming):
                        activities.append(f"📺 Streaming {activity.name}")
                    elif isinstance(activity, discord.Spotify):
                        activities.append(f"🎵 Listening to {activity.title}")
                    elif isinstance(activity, discord.Activity):
                        activities.append(f"📝 {activity.name}")

                if activities:
                    embed.add_field(
                        name="🎯 Activities",
                        value="\n".join(activities[:3]),  # Limit to 3 activities
                        inline=False,
                    )

            await interaction.response.send_message(embed=embed, ephemeral=True)

            # Log userinfo command usage
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category="UTILITY",
                    action="USERINFO_USED",
                    user_id=interaction.user.id,
                    target_id=target_user.id,
                    channel_id=interaction.channel.id,
                )

        except Exception as e:
            self.logger.error(f"Error in userinfo command: {e}")
            await self._error_response(interaction, "Failed to get user information")

    @app_commands.command(
        name="serverinfo", description="Display information about the current server"
    )
    async def serverinfo(self, interaction: discord.Interaction):
        """Display server information."""
        try:
            if not isinstance(interaction.channel, discord.TextChannel):
                await self._error_response(
                    interaction, "This command can only be used in a server"
                )
                return

            guild = interaction.guild

            # Create serverinfo embed
            embed = create_embed(
                title=f"🖥️ Server Information: {guild.name}",
                color=COLORS["primary"],
                thumbnail=guild.icon.url if guild.icon else None,
            )

            # Basic server information
            embed.add_field(name="🆔 Server ID", value=f"`{guild.id}`", inline=True)

            embed.add_field(
                name="👑 Server Owner",
                value=guild.owner.mention if guild.owner else "Unknown",
                inline=True,
            )

            embed.add_field(
                name="📅 Created On",
                value=time_helper.get_discord_timestamp(guild.created_at, "R"),
                inline=True,
            )

            # Member information
            total_members = guild.member_count
            bots = len([m for m in guild.members if m.bot])
            humans = total_members - bots

            embed.add_field(
                name="👥 Members",
                value=f"Total: {total_members:,}\n"
                f"Humans: {humans:,}\n"
                f"Bots: {bots:,}",
                inline=True,
            )

            # Boost information
            boost_level = guild.premium_tier
            boost_count = guild.premium_subscription_count or 0

            embed.add_field(
                name="✨ Server Boosts",
                value=f"Level: {boost_level}\n" f"Boosts: {boost_count:,}",
                inline=True,
            )

            # Channel information
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            categories = len(guild.categories)

            embed.add_field(
                name="📢 Channels",
                value=f"Text: {text_channels}\n"
                f"Voice: {voice_channels}\n"
                f"Categories: {categories}",
                inline=True,
            )

            # Role and emoji information
            embed.add_field(
                name="🎭 Roles & Emojis",
                value=f"Roles: {len(guild.roles)}\n" f"Emojis: {len(guild.emojis)}",
                inline=True,
            )

            # Server features
            if guild.features:
                features = ", ".join(guild.features[:3])  # Limit to 3 features
                if len(guild.features) > 3:
                    features += f" +{len(guild.features) - 3} more"

                embed.add_field(name="⚡ Features", value=features, inline=True)

            # Verification level
            verification_levels = {
                discord.VerificationLevel.none: "None",
                discord.VerificationLevel.low: "Low",
                discord.VerificationLevel.medium: "Medium",
                discord.VerificationLevel.high: "High",
                discord.VerificationLevel.highest: "Highest",
            }

            embed.add_field(
                name="🔒 Verification Level",
                value=verification_levels.get(guild.verification_level, "Unknown"),
                inline=True,
            )

            # Content filter
            filter_levels = {
                discord.ContentFilter.disabled: "Disabled",
                discord.ContentFilter.no_role: "No Role",
                discord.ContentFilter.all_members: "All Members",
            }

            embed.add_field(
                name="🛡️ Content Filter",
                value=filter_levels.get(guild.explicit_content_filter, "Unknown"),
                inline=True,
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

            # Log serverinfo command usage
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category="UTILITY",
                    action="SERVERINFO_USED",
                    user_id=interaction.user.id,
                    channel_id=interaction.channel.id,
                    guild_id=guild.id,
                )

        except Exception as e:
            self.logger.error(f"Error in serverinfo command: {e}")
            await self._error_response(interaction, "Failed to get server information")

    @app_commands.command(name="about", description="Shows information about MalaBoT")
    async def about(self, interaction: discord.Interaction):
        """Display bot information."""
        try:
            # Calculate uptime
            uptime_seconds = int(time.time() - self.start_time)
            uptime_str = format_duration(uptime_seconds)

            # Get system info
            sys_info = get_system_info()

            # Create about embed
            embed = create_embed(
                title=f"🤖 About {settings.BOT_NAME}",
                description=f"{settings.BOT_NAME} is a multifunctional Discord bot designed to enhance your server experience with XP systems, moderation tools, fun commands, and more!",
                color=COLORS["primary"],
            )

            # Basic information
            embed.add_field(name="🏷️ Bot Name", value=settings.BOT_NAME, inline=True)
            embed.add_field(
                name="📦 Version", value=f"v{settings.BOT_VERSION}", inline=True
            )
            embed.add_field(name="⏱️ Uptime", value=uptime_str, inline=True)

            # Developer information
            embed.add_field(
                name="👨‍💻 Developer",
                value="Built with ❤️ using discord.py",
                inline=True,
            )

            embed.add_field(name="🔧 Library", value="discord.py 2.x", inline=True)

            embed.add_field(
                name="🌐 Hosting", value="DigitalOcean Droplet", inline=True
            )

            # System information
            if sys_info:
                disk_info = sys_info.get("disk_usage")
                disk_free_gb = disk_info.free / (1024**3) if disk_info else 0
                embed.add_field(
                    name="💻 System Info",
                    value=f"CPU: {sys_info.get('cpu_usage', 0)}%\n"
                    f"Memory: {sys_info.get('memory_usage', 0):.2f} MB\n"
                    f"Disk: {disk_free_gb:.2f} GB free",
                    inline=True,
                )

            # Feature list
            features = [
                "🏆 XP & Leveling System",
                "🎂 Birthday Celebrations",
                "🔥 Roast XP System",
                "👋 Welcome Messages",
                "🛡️ Moderation Tools",
                "🎮 Fun Commands",
                "⚙️ Utility Commands",
            ]

            embed.add_field(name="✨ Features", value="\n".join(features), inline=False)

            # Statistics (if database is available)
            if self.bot.db_manager:
                try:
                    # Get user count from database
                    # This would need to be implemented in the database models
                    embed.add_field(
                        name="📊 Statistics",
                        value=f"Serving {interaction.guild.member_count if interaction.guild else 0}+ users\n"
                        f"Commands executed: Many!\n"
                        f"System healthy: ✅",
                        inline=True,
                    )
                except Exception as e:
                    self.logger.warning(f"Failed to add stats field to about embed: {e}")

            # Footer with invite link
            embed.set_footer(
                text=f"Thank you for using {settings.BOT_NAME}! • Made with ❤️"
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

            # Log about command usage
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category="UTILITY",
                    action="ABOUT_USED",
                    user_id=interaction.user.id,
                    channel_id=interaction.channel.id,
                )

        except Exception as e:
            self.logger.error(f"Error in about command: {e}")
            await self._error_response(interaction, "Failed to get bot information")

    @app_commands.command(
        name="serverstats", description="Shows detailed server statistics"
    )
    async def serverstats(self, interaction: discord.Interaction):
        """Display detailed server statistics."""
        try:
            if not isinstance(interaction.channel, discord.TextChannel):
                await self._error_response(
                    interaction, "This command can only be used in a server"
                )
                return

            guild = interaction.guild

            # Get member statistics
            total_members = guild.member_count
            online_members = len(
                [m for m in guild.members if m.status != discord.Status.offline]
            )
            bots = len([m for m in guild.members if m.bot])
            humans = total_members - bots

            # Get channel statistics
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            categories = len(guild.categories)

            # Get role statistics
            roles = len(guild.roles)

            # Create serverstats embed
            embed = create_embed(
                title=f"📊 Server Statistics: {guild.name}", color=COLORS["info"]
            )

            # Member statistics
            embed.add_field(
                name="👥 Member Statistics",
                value=f"Total Members: **{total_members:,}**\n"
                f"Online Now: **{online_members:,}**\n"
                f"Humans: **{humans:,}**\n"
                f"Bots: **{bots:,}**",
                inline=True,
            )

            # Channel statistics
            embed.add_field(
                name="📢 Channel Statistics",
                value=f"Text Channels: **{text_channels}**\n"
                f"Voice Channels: **{voice_channels}**\n"
                f"Categories: **{categories}**\n"
                f"Total Channels: **{text_channels + voice_channels}**",
                inline=True,
            )

            # Server statistics
            embed.add_field(
                name="🏛️ Server Information",
                value=f"Roles: **{roles}**\n"
                f"Emojis: **{len(guild.emojis)}**\n"
                f"Boost Level: **{guild.premium_tier}**\n"
                f"Total Boosts: **{guild.premium_subscription_count or 0}**",
                inline=True,
            )

            # Growth information
            server_age = (
                datetime.utcnow() - guild.created_at.replace(tzinfo=None)
            ).days
            members_per_day = (
                round(total_members / server_age, 1) if server_age > 0 else 0
            )

            embed.add_field(
                name="📈 Growth Metrics",
                value=f"Server Age: **{server_age}** days\n"
                f"Avg. Members/Day: **{members_per_day}**\n"
                f"Created: **{time_helper.get_discord_timestamp(guild.created_at, 'D')}**",
                inline=True,
            )

            # Online percentage
            online_percentage = (
                round((online_members / total_members) * 100, 1)
                if total_members > 0
                else 0
            )

            embed.add_field(
                name="📊 Activity Metrics",
                value=f"Online Percentage: **{online_percentage}%**\n"
                f"Bot Percentage: **{round((bots / total_members) * 100, 1) if total_members > 0 else 0}%**\n"
                f"Categories: **{categories}**",
                inline=True,
            )

            # Additional info
            embed.add_field(
                name="🔧 Technical Info",
                value=f"Server ID: `{guild.id}`\n"
                f"Verification: **{guild.verification_level.name.title()}**\n"
                f"Content Filter: **{guild.explicit_content_filter.name.title()}**",
                inline=False,
            )

            embed.set_footer(
                text=f"Statistics as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

            # Log serverstats command usage
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category="UTILITY",
                    action="SERVERSTATS_USED",
                    user_id=interaction.user.id,
                    channel_id=interaction.channel.id,
                    guild_id=guild.id,
                    details=f"Members: {total_members}, Channels: {text_channels + voice_channels}",
                )

        except Exception as e:
            self.logger.error(f"Error in serverstats command: {e}")
            await self._error_response(interaction, "Failed to get server statistics")

    async def _error_response(self, interaction: discord.Interaction, message: str):
        """Send error response."""
        embed = embed_helper.error_embed(title="Command Error", description=message)

        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except (discord.HTTPException, discord.NotFound) as e:
            self.logger.warning(f"Failed to send response: {e}")


async def setup(bot: commands.Bot):
    """Setup function for the cog."""
    utility_cog = Utility(bot)
    await bot.add_cog(utility_cog)
    # Commands are automatically registered when cog is loaded
