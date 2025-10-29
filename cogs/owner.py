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
from config.constants import COLORS
from config.settings import settings

class Owner(commands.Cog):
    """Owner-only commands for bot administration."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger('owner')
    
    async def cog_check(self, interaction: discord.Interaction) -> bool:
        """Check if user is bot owner."""
        user_id = interaction.user.id
        owner_ids = settings.OWNER_IDS
        self.logger.info(f"Owner check: User {user_id}, Owner IDs: {owner_ids}")
        return user_id in owner_ids
    
    @app_commands.command(name="owner", description="Owner-only control panel (Bot Owner only)")
    @app_commands.describe(
        action="What action would you like to perform?"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="status", value="status"),
        app_commands.Choice(name="restart", value="restart"),
        app_commands.Choice(name="shutdown", value="shutdown"),
        app_commands.Choice(name="clearcrash", value="clearcrash"),
        app_commands.Choice(name="setonline", value="setonline")
    ])
    async def owner(self, interaction: discord.Interaction, action: str):
        """Owner control panel for various administrative actions."""
        try:
            user_id = interaction.user.id
            owner_ids = settings.OWNER_IDS
            
            if user_id not in owner_ids:
                self.logger.error(f"Access denied: User {user_id} not in owner list {owner_ids}")
                embed = embed_helper.error_embed(
                    title="Access Denied",
                    description=f"This command is only available to the bot owner.\nYour ID: {user_id}\nOwner IDs: {owner_ids}"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            self.logger.info(f"Owner command access granted to user {user_id} for action: {action}")
            
            if action == "status":
                await self._owner_status(interaction)
            elif action == "restart":
                await self._owner_restart(interaction)
            elif action == "shutdown":
                await self._owner_shutdown(interaction)
            elif action == "clearcrash":
                await self._owner_clearcrash(interaction)
            elif action == "setonline":
                await self._owner_setonline(interaction)
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
            sys_info = get_system_info()
            
            start_time = getattr(self.bot, 'start_time', time.time())
            if isinstance(start_time, datetime):
                uptime_seconds = int(time.time() - start_time.timestamp())
            else:
                uptime_seconds = int(time.time() - start_time)
            uptime_str = self._format_duration(uptime_seconds)
            
            embed = embed_helper.create_embed(
                title="🔧 Bot Status Report",
                description="Bot status information",
                color=COLORS["info"]
            )
            
            embed.add_field(
                name="🤖 Bot Information",
                value=f"Name: {self.bot.user}\n"
                      f"ID: {self.bot.user.id}\n"
                      f"Version: {settings.BOT_VERSION}\n"
                      f"Uptime: {uptime_str}\n"
                      f"Latency: {round(self.bot.latency * 1000)}ms",
                inline=True
            )
            
            if sys_info:
                embed.add_field(
                    name="💻 System Resources",
                    value=f"CPU: {sys_info.get('cpu_percent', 0)}%\n"
                          f"Memory: {sys_info.get('memory_used_mb', 0)} MB ({sys_info.get('memory_percent', 0)}%)\n"
                          f"Disk: {sys_info.get('disk_free_gb', 0)} GB free\n"
                          f"Processes: {sys_info.get('process_count', 0)}",
                    inline=True
                )
            
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
            
            embed.set_footer(text=f"Status requested by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            self.logger.info(f"Status command executed by owner {interaction.user.id}")
            
        except Exception as e:
            self.logger.error(f"Error in owner status: {e}")
            await self._error_response(interaction, "Failed to get bot status")
    
    async def _owner_restart(self, interaction: discord.Interaction):
        """Restart the bot."""
        try:
            embed = embed_helper.warning_embed(
                title="🔄 Restarting Bot",
                description="The bot will restart now. This may take up to 60 seconds."
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            self.logger.info(f"Bot restart requested by owner {interaction.user.id}")
            
            await asyncio.sleep(2)
            
            try:
                subprocess.run(["./update.sh", "manual"], check=True)
            except:
                os.execv(sys.executable, [sys.executable] + sys.argv)
                
        except Exception as e:
            self.logger.error(f"Error in owner restart: {e}")
            await self._error_response(interaction, "Failed to restart bot")
    
    async def _owner_shutdown(self, interaction: discord.Interaction):
        """Shutdown the bot."""
        try:
            embed = embed_helper.error_embed(
                title="🛑 Shutting Down Bot",
                description="The bot will shutdown now."
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            self.logger.info(f"Bot shutdown requested by owner {interaction.user.id}")
            
            await asyncio.sleep(2)
            
            await self.bot.close()
            
        except Exception as e:
            self.logger.error(f"Error in owner shutdown: {e}")
            await self._error_response(interaction, "Failed to shutdown bot")
    
    async def _owner_clearcrash(self, interaction: discord.Interaction):
        """Clear crash flags."""
        try:
            if self.bot.db_manager:
                await self.bot.db_manager.clear_flag('crash_detected')
                
                embed = embed_helper.success_embed(
                    title="🧹 Crash Flags Cleared",
                    description="All crash flags have been cleared."
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                self.logger.info(f"Crash flags cleared by owner {interaction.user.id}")
            else:
                embed = embed_helper.error_embed(
                    title="Database Error",
                    description="Database is not available to clear crash flags."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            self.logger.error(f"Error clearing crash flags: {e}")
            await self._error_response(interaction, "Failed to clear crash flags")
    
    async def _owner_setonline(self, interaction: discord.Interaction):
        """Set online message configuration."""
        try:
            all_channels = []
            for guild in self.bot.guilds:
                for channel in guild.text_channels:
                    all_channels.append({
                        'id': channel.id,
                        'name': f"{guild.name} - #{channel.name}",
                        'guild_id': guild.id
                    })
            
            if not all_channels:
                embed = embed_helper.error_embed(
                    title="No Channels Found",
                    description="No text channels found in any servers."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            class OnlineChannelSelectView(discord.ui.View):
                def __init__(self, cog_instance):
                    super().__init__(timeout=60)
                    self.cog = cog_instance
                    self.selected_channel = None
                    
                @discord.ui.select(
                    placeholder="Select channel for online message",
                    options=[
                        discord.SelectOption(
                            label=channel['name'],
                            value=str(channel['id']),
                            description=f"Channel ID: {channel['id']}"
                        ) for channel in all_channels[:25]
                    ]
                )
                async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
                    self.selected_channel = int(select.values[0])
                    self.stop()
                    
                    modal = OnlineMessageModal(self.cog, self.selected_channel)
                    await interaction.response.send_modal(modal)
            
            class OnlineMessageModal(discord.ui.Modal, title="Set Online Message"):
                def __init__(self, cog_instance, channel_id):
                    super().__init__()
                    self.cog = cog_instance
                    self.channel_id = channel_id
                    
                message = discord.ui.TextInput(
                    label="Online Message",
                    placeholder="Enter the message to send when bot comes online...",
                    style=discord.TextStyle.paragraph,
                    max_length=1000,
                    required=True
                )
                
                async def on_submit(self, interaction: discord.Interaction):
                    try:
                        await self.cog.bot.db_manager.set_setting('online_channel_id', str(self.channel_id))
                        await self.cog.bot.db_manager.set_setting('online_message', self.message.value)
                        
                        channel = self.cog.bot.get_channel(self.channel_id)
                        if channel:
                            embed = embed_helper.success_embed(
                                title="🟢 Bot Online Message Set",
                                description=self.message.value
                            )
                            await channel.send(embed=embed)
                            
                            embed = embed_helper.success_embed(
                                title="✅ Online Message Configured",
                                description=f"Message will be sent to {channel.mention} whenever the bot starts up."
                            )
                            await interaction.response.send_message(embed=embed, ephemeral=True)
                        else:
                            embed = embed_helper.error_embed(
                                title="Channel Not Found",
                                description="Could not find the selected channel."
                            )
                            await interaction.response.send_message(embed=embed, ephemeral=True)
                            
                    except Exception as e:
                        embed = embed_helper.error_embed(
                            title="Error",
                            description=f"Failed to save online message: {e}"
                        )
                        await interaction.response.send_message(embed=embed, ephemeral=True)
            
            view = OnlineChannelSelectView(self)
            embed = embed_helper.info_embed(
                title="📢 Select Online Message Channel",
                description="Select the channel where the online message should be sent when the bot starts."
            )
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            self.logger.error(f"Error setting online message: {e}")
            await self._error_response(interaction, "Failed to set online message")
    
    async def send_online_message(self):
        """Send online message if configured."""
        try:
            if not self.bot.db_manager:
                return
            
            # Try to get guild-specific settings first
            for guild in self.bot.guilds:
                guild_id = guild.id
                online_channel_id = await self.bot.db_manager.get_setting(f'online_message_channel_{guild_id}')
                online_message = await self.bot.db_manager.get_setting(f'online_message_{guild_id}')
                
                if online_channel_id and online_message:
                    channel = self.bot.get_channel(int(online_channel_id))
                    if channel:
                        embed = embed_helper.success_embed(
                            title="🟢 Bot Online",
                            description=online_message
                        )
                        await channel.send(embed=embed)
                        self.logger.info(f"Sent online message to channel {online_channel_id} in guild {guild.name}")
                    
        except Exception as e:
            self.logger.error(f"Error sending online message: {e}")
    
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