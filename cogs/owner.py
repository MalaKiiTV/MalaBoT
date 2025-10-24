"""
Owner commands cog for MalaBoT.
Contains administrative commands for bot owners only.
"""

import discord
from discord import app_commands
from discord.ext import commands
import sys
import subprocess
import time
import asyncio
import os
from datetime import datetime
from typing import Optional

from utils.logger import get_logger, log_system
from utils.helpers import (
    embed_helper, is_owner, safe_send_message, 
    create_embed, get_system_info
)
from config.constants import COLORS, ROAST_TITLES
from config.settings import settings

class Owner(commands.Cog):
    """Owner-only commands for bot administration."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger('owner')
    
    def cog_check(self, interaction: discord.Interaction) -> bool:
        """Check if user is bot owner."""
        return is_owner(interaction.user)
    
    @app_commands.command(name="owner", description="Owner-only control panel (Bot Owner only)")
    @app_commands.describe(
        action="What action would you like to perform?"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="status", value="status"),
        app_commands.Choice(name="restart", value="restart"),
        app_commands.Choice(name="shutdown", value="shutdown"),
        app_commands.Choice(name="eval", value="eval"),
        app_commands.Choice(name="announce", value="announce"),
        app_commands.Choice(name="dm", value="dm"),
        app_commands.Choice(name="setstatus", value="setstatus"),
        app_commands.Choice(name="setactivity", value="setactivity"),
        app_commands.Choice(name="clearcrash", value="clearcrash"),
        app_commands.Choice(name="digest", value="digest"),
        app_commands.Choice(name="setroasttitle", value="setroasttitle"),
        app_commands.Choice(name="togglerestart", value="togglerestart")
    ])
    async def owner(self, interaction: discord.Interaction, action: str):
        """Owner control panel for various administrative actions."""
        try:
            if not is_owner(interaction.user):
                embed = embed_helper.error_embed(
                    title="Access Denied",
                    description="This command is only available to the bot owner."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Route to appropriate handler
            if action == "status":
                await self._owner_status(interaction)
            elif action == "restart":
                await self._owner_restart(interaction)
            elif action == "shutdown":
                await self._owner_shutdown(interaction)
            elif action == "eval":
                await self._owner_eval(interaction)
            elif action == "announce":
                await self._owner_announce(interaction)
            elif action == "dm":
                await self._owner_dm(interaction)
            elif action == "setstatus":
                await self._owner_setstatus(interaction)
            elif action == "setactivity":
                await self._owner_setactivity(interaction)
            elif action == "clearcrash":
                await self._owner_clearcrash(interaction)
            elif action == "digest":
                await self._owner_digest(interaction)
            elif action == "setroasttitle":
                await self._owner_setroasttitle(interaction)
            elif action == "togglerestart":
                await self._owner_togglerestart(interaction)
            else:
                embed = embed_helper.error_embed(
                    title="Unknown Action",
                    description="The specified action is not recognized."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            self.logger.error(f"Error in owner command: {e}")
            await self._error_response(interaction, f"Failed to execute owner command: {action}")
    
    async def _owner_status(self, interaction: discord.Interaction):
        """Show detailed bot status."""
        try:
            # Get system info
            sys_info = get_system_info()
            
            # Calculate uptime
            uptime_seconds = int(time.time() - getattr(self.bot, 'start_time', time.time()))
            uptime_str = self._format_duration(uptime_seconds)
            
            # Create status embed
            embed = create_embed(
                title="🔧 Bot Status Report",
                color=COLORS["info"]
            )
            
            # Basic information
            embed.add_field(
                name="🤖 Bot Information",
                value=f"Name: {self.bot.user}\n"
                      f"ID: {self.bot.user.id}\n"
                      f"Version: {settings.BOT_VERSION}\n"
                      f"Uptime: {uptime_str}\n"
                      f"Latency: {round(self.bot.latency * 1000)}ms",
                inline=True
            )
            
            # System information
            if sys_info:
                embed.add_field(
                    name="💻 System Resources",
                    value=f"CPU: {sys_info.get('cpu_percent', 0)}%\n"
                          f"Memory: {sys_info.get('memory_used_mb', 0)} MB ({sys_info.get('memory_percent', 0)}%)\n"
                          f"Disk: {sys_info.get('disk_free_gb', 0)} GB free\n"
                          f"Processes: {sys_info.get('process_count', 0)}",
                    inline=True
                )
            
            # Bot statistics
            total_guilds = len(self.bot.guilds)
            total_users = sum(guild.member_count for guild in self.bot.guilds)
            total_channels = sum(len(guild.channels) for guild in self.bot.guilds)
            
            embed.add_field(
                name="📊 Bot Statistics",
                value=f"Servers: {total_guilds}\n"
                      f"Total Users: {total_users:,}\n"
                      f"Total Channels: {total_channels:,}\n"
                      f"Cogs Loaded: {len(self.bot.cogs)}",
                inline=True
            )
            
            # Feature status
            features_status = []
            features_status.append(f"Safe Mode: {'🔴' if getattr(self.bot, 'safe_mode', False) else '🟢'}")
            features_status.append(f"Health Monitor: {'🟢' if settings.ENABLE_HEALTH_MONITOR else '🔴'}")
            features_status.append(f"Watchdog: {'🟢' if settings.ENABLE_WATCHDOG else '🔴'}")
            
            embed.add_field(
                name="⚙️ Feature Status",
                value="\n".join(features_status),
                inline=True
            )
            
            # Database status
            db_status = "🟢 Connected" if self.bot.db_manager else "🔴 Disconnected"
            embed.add_field(
                name="💾 Database",
                value=f"Status: {db_status}\n"
                      f"Path: {settings.DATABASE_URL}",
                inline=True
            )
            
            embed.set_footer(text=f"Status requested by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Log status command usage
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category='OWNER',
                    action='STATUS_CHECK',
                    user_id=interaction.user.id
                )
        
        except Exception as e:
            self.logger.error(f"Error in owner status: {e}")
            raise
    
    async def _owner_restart(self, interaction: discord.Interaction):
        """Restart the bot."""
        try:
            embed = embed_helper.warning_embed(
                title="🔄 Restarting Bot",
                description="The bot will restart now. This may take up to 60 seconds."
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Log restart command
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category='SYSTEM',
                    action='RESTART',
                    user_id=interaction.user.id,
                    details="Manual restart requested by owner"
                )
            
            log_system(f"Bot restart requested by owner {interaction.user.id}")
            
            # Set crash flag for recovery
            if self.bot.db_manager:
                await self.bot.db_manager.set_flag('crash_detected', 'manual_restart')
            
            # Give time for message to send
            await asyncio.sleep(2)
            
            # Restart using the update script or direct restart
            try:
                # Try to use update script
                subprocess.run(["./update.sh", "manual"], check=True)
            except:
                # Fallback to direct restart
                os.execv(sys.executable, [sys.executable] + sys.argv)
        
        except Exception as e:
            self.logger.error(f"Error in owner restart: {e}")
            raise
    
    async def _owner_shutdown(self, interaction: discord.Interaction):
        """Shutdown the bot."""
        try:
            embed = embed_helper.error_embed(
                title="🛑 Shutting Down Bot",
                description="The bot will shutdown now. Use the update script to restart."
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Log shutdown command
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category='SYSTEM',
                    action='SHUTDOWN',
                    user_id=interaction.user.id,
                    details="Manual shutdown requested by owner"
                )
            
            log_system(f"Bot shutdown requested by owner {interaction.user.id}")
            
            # Give time for message to send
            await asyncio.sleep(2)
            
            # Graceful shutdown
            await self.bot.shutdown()
        
        except Exception as e:
            self.logger.error(f"Error in owner shutdown: {e}")
            raise
    
    async def _owner_eval(self, interaction: discord.Interaction):
        """Evaluate Python code (owner only)."""
        try:
            # This is a simplified version - in production, you'd want more security
            await interaction.response.send_message(
                "Eval command requires code input. This is a placeholder for security reasons.",
                ephemeral=True
            )
        
        except Exception as e:
            self.logger.error(f"Error in owner eval: {e}")
            raise
    
    async def _owner_announce(self, interaction: discord.Interaction):
        """Send announcement to all servers."""
        try:
            await interaction.response.send_message(
                "Announce command requires message content. This is a placeholder.",
                ephemeral=True
            )
        
        except Exception as e:
            self.logger.error(f"Error in owner announce: {e}")
            raise
    
    async def _owner_dm(self, interaction: discord.Interaction):
        """Send DM to a user."""
        try:
            await interaction.response.send_message(
                "DM command requires user ID and message. This is a placeholder.",
                ephemeral=True
            )
        
        except Exception as e:
            self.logger.error(f"Error in owner dm: {e}")
            raise
    
    async def _owner_setstatus(self, interaction: discord.Interaction):
        """Set bot status."""
        try:
            await interaction.response.send_message(
                "Set status command requires status text. This is a placeholder.",
                ephemeral=True
            )
        
        except Exception as e:
            self.logger.error(f"Error in owner setstatus: {e}")
            raise
    
    async def _owner_setactivity(self, interaction: discord.Interaction):
        """Set bot activity."""
        try:
            await interaction.response.send_message(
                "Set activity command requires activity type and text. This is a placeholder.",
                ephemeral=True
            )
        
        except Exception as e:
            self.logger.error(f"Error in owner setactivity: {e}")
            raise
    
    async def _owner_clearcrash(self, interaction: discord.Interaction):
        """Clear crash flags."""
        try:
            if self.bot.db_manager:
                await self.bot.db_manager.clear_flag('crash_detected')
                
                embed = embed_helper.success_embed(
                    title="🧹 Crash Flags Cleared",
                    description="All crash flags have been cleared. The bot will start normally on next restart."
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
                # Log crash flag clearing
                await self.bot.db_manager.log_event(
                    category='OWNER',
                    action='CRASH_FLAGS_CLEARED',
                    user_id=interaction.user.id
                )
            
            else:
                embed = embed_helper.error_embed(
                    title="Database Error",
                    description="Database is not available to clear crash flags."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            self.logger.error(f"Error clearing crash flags: {e}")
            raise
    
    async def _owner_digest(self, interaction: discord.Interaction):
        """Trigger daily digest manually."""
        try:
            # This would trigger the daily digest function
            await interaction.response.send_message(
                "Daily digest manual trigger - This is a placeholder.",
                ephemeral=True
            )
        
        except Exception as e:
            self.logger.error(f"Error in owner digest: {e}")
            raise
    
    async def _owner_setroasttitle(self, interaction: discord.Interaction):
        """Set custom final roast title."""
        try:
            await interaction.response.send_message(
                "Set roast title command requires title text. This is a placeholder.",
                ephemeral=True
            )
        
        except Exception as e:
            self.logger.error(f"Error in owner setroasttitle: {e}")
            raise
    
    async def _owner_togglerestart(self, interaction: discord.Interaction):
        """Toggle auto-restart feature."""
        try:
            await interaction.response.send_message(
                "Toggle restart command - This is a placeholder.",
                ephemeral=True
            )
        
        except Exception as e:
            self.logger.error(f"Error in owner togglerestart: {e}")
            raise
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to human-readable string."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m {seconds % 60}s"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"
    
    async def _error_response(self, interaction: discord.Interaction, message: str):
        """Send error response."""
        embed = embed_helper.error_embed(
            title="Owner Command Error",
            description=message
        )
        
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            pass

async def setup(bot: commands.Bot):
    """Setup function for the cog."""
    await bot.add_cog(Owner(bot))