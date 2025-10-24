"""
Moderation system cog for MalaBoT.
Handles message deletion, channel management, and moderation logging.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from utils.logger import get_logger, log_moderation
from utils.helpers import (
    embed_helper, is_admin, safe_send_message, create_embed
)
from config.constants import COLORS, DELETE_LOG_LIMIT
from config.settings import settings

class Moderation(commands.Cog):
    """Moderation tools and logging."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger('moderation')
    
    @app_commands.command(name="delete", description="Message deletion commands (Admin only)")
    @app_commands.describe(
        action="What deletion action would you like to perform?"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="last10", value="last10"),
        app_commands.Choice(name="last50", value="last50"),
        app_commands.Choice(name="all", value="all"),
        app_commands.Choice(name="logs", value="logs")
    ])
    async def delete(self, interaction: discord.Interaction, action: str):
        """Message deletion commands."""
        try:
            # Check permissions
            if not is_admin(interaction.user):
                embed = embed_helper.error_embed(
                    title="Permission Denied",
                    description="This command is only available to administrators."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if not isinstance(interaction.channel, discord.TextChannel):
                embed = embed_helper.error_embed(
                    title="Invalid Channel",
                    description="This command can only be used in text channels."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if action == "last10":
                await self._delete_last10(interaction)
            elif action == "last50":
                await self._delete_last50(interaction)
            elif action == "all":
                await self._delete_all(interaction)
            elif action == "logs":
                await self._delete_logs(interaction)
            else:
                embed = embed_helper.error_embed(
                    title="Unknown Action",
                    description="The specified deletion action is not available."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            self.logger.error(f"Error in delete command: {e}")
            await self._error_response(interaction, "Failed to process deletion command")
    
    async def _delete_last10(self, interaction: discord.Interaction):
        """Delete last 10 messages."""
        try:
            channel = interaction.channel
            
            # Defer response since deletion might take time
            await interaction.response.defer(ephemeral=True)
            
            # Delete messages
            deleted = await channel.purge(limit=10)
            
            # Log moderation action
            if self.bot.db_manager:
                await self.bot.db_manager.log_moderation_action(
                    moderator_id=interaction.user.id,
                    action="DELETE_LAST10",
                    channel_id=channel.id,
                    message_count=len(deleted),
                    details=f"Deleted {len(deleted)} messages"
                )
                
                await self.bot.db_manager.log_event(
                    category='MOD',
                    action='DELETE',
                    user_id=interaction.user.id,
                    channel_id=channel.id,
                    guild_id=interaction.guild.id,
                    details=f"Deleted {len(deleted)} messages"
                )
            
            # Send confirmation
            embed = embed_helper.success_embed(
                title="✅ Messages Deleted",
                description=f"Successfully deleted {len(deleted)} messages."
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Log to moderation log
            log_moderation(f"🧹 {interaction.user.name} deleted {len(deleted)} messages in #{channel.name}")
            
            # Send public log if moderation log channel is set
            if self.bot.db_manager:
                mod_log_channel_id = await self.bot.db_manager.get_setting('moderation_log_channel_id')
                if mod_log_channel_id:
                    mod_log_channel = self.bot.get_channel(mod_log_channel_id)
                    if mod_log_channel:
                        log_embed = create_embed(
                            title="🧹 Messages Deleted",
                            description=f"**Moderator:** {interaction.user.mention}\n"
                                      f"**Channel:** {channel.mention}\n"
                                      f"**Messages Deleted:** {len(deleted)}",
                            color=COLORS["warning"]
                        )
                        await safe_send_message(mod_log_channel, embed=log_embed)
        
        except discord.Forbidden:
            embed = embed_helper.error_embed(
                title="Permission Error",
                description="I don't have permission to delete messages in this channel."
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            self.logger.error(f"Error deleting last 10 messages: {e}")
            raise
    
    async def _delete_last50(self, interaction: discord.Interaction):
        """Delete last 50 messages."""
        try:
            channel = interaction.channel
            
            # Defer response since deletion might take time
            await interaction.response.defer(ephemeral=True)
            
            # Delete messages
            deleted = await channel.purge(limit=50)
            
            # Log moderation action
            if self.bot.db_manager:
                await self.bot.db_manager.log_moderation_action(
                    moderator_id=interaction.user.id,
                    action="DELETE_LAST50",
                    channel_id=channel.id,
                    message_count=len(deleted),
                    details=f"Deleted {len(deleted)} messages"
                )
                
                await self.bot.db_manager.log_event(
                    category='MOD',
                    action='DELETE',
                    user_id=interaction.user.id,
                    channel_id=channel.id,
                    guild_id=interaction.guild.id,
                    details=f"Deleted {len(deleted)} messages"
                )
            
            # Send confirmation
            embed = embed_helper.success_embed(
                title="✅ Messages Deleted",
                description=f"Successfully deleted {len(deleted)} messages."
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Log to moderation log
            log_moderation(f"🧹 {interaction.user.name} deleted {len(deleted)} messages in #{channel.name}")
            
            # Send public log if moderation log channel is set
            if self.bot.db_manager:
                mod_log_channel_id = await self.bot.db_manager.get_setting('moderation_log_channel_id')
                if mod_log_channel_id:
                    mod_log_channel = self.bot.get_channel(mod_log_channel_id)
                    if mod_log_channel:
                        log_embed = create_embed(
                            title="🧹 Messages Deleted",
                            description=f"**Moderator:** {interaction.user.mention}\n"
                                      f"**Channel:** {channel.mention}\n"
                                      f"**Messages Deleted:** {len(deleted)}",
                            color=COLORS["warning"]
                        )
                        await safe_send_message(mod_log_channel, embed=log_embed)
        
        except discord.Forbidden:
            embed = embed_helper.error_embed(
                title="Permission Error",
                description="I don't have permission to delete messages in this channel."
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            self.logger.error(f"Error deleting last 50 messages: {e}")
            raise
    
    async def _delete_all(self, interaction: discord.Interaction):
        """Delete all messages by cloning channel."""
        try:
            channel = interaction.channel
            
            # Defer response
            await interaction.response.defer(ephemeral=True)
            
            # Clone channel
            new_channel = await channel.clone(reason=f"Channel purge by {interaction.user.name}")
            
            # Move new channel to same position
            await new_channel.edit(position=channel.position)
            
            # Delete old channel
            await channel.delete(reason=f"Channel purge by {interaction.user.name}")
            
            # Log moderation action
            if self.bot.db_manager:
                await self.bot.db_manager.log_moderation_action(
                    moderator_id=interaction.user.id,
                    action="DELETE_ALL",
                    channel_id=new_channel.id,
                    message_count=None,
                    details=f"Channel purged and recreated"
                )
                
                await self.bot.db_manager.log_event(
                    category='MOD',
                    action='PURGE',
                    user_id=interaction.user.id,
                    channel_id=new_channel.id,
                    guild_id=interaction.guild.id,
                    details="Channel purged and recreated"
                )
            
            # Send confirmation in new channel
            embed = embed_helper.warning_embed(
                title="⚠️ Channel Purged",
                description=f"This channel was purged by {interaction.user.mention}.\n\n"
                           "All previous messages have been deleted."
            )
            
            await safe_send_message(new_channel, embed=embed)
            
            # Log to moderation log
            log_moderation(f"🧹 {interaction.user.name} purged channel #{new_channel.name}")
            
            # Send public log if moderation log channel is set
            if self.bot.db_manager:
                mod_log_channel_id = await self.bot.db_manager.get_setting('moderation_log_channel_id')
                if mod_log_channel_id:
                    mod_log_channel = self.bot.get_channel(mod_log_channel_id)
                    if mod_log_channel:
                        log_embed = create_embed(
                            title="🧹 Channel Purged",
                            description=f"**Moderator:** {interaction.user.mention}\n"
                                      f"**Channel:** {new_channel.mention}\n"
                                      f"**Action:** Full channel purge (all messages deleted)",
                            color=COLORS["error"]
                        )
                        await safe_send_message(mod_log_channel, embed=log_embed)
        
        except discord.Forbidden:
            embed = embed_helper.error_embed(
                title="Permission Error",
                description="I don't have permission to manage channels."
            )
            try:
                await interaction.followup.send(embed=embed, ephemeral=True)
            except:
                pass
        except Exception as e:
            self.logger.error(f"Error purging channel: {e}")
            raise
    
    async def _delete_logs(self, interaction: discord.Interaction):
        """Show deletion logs."""
        try:
            if not self.bot.db_manager:
                embed = embed_helper.error_embed(
                    title="Database Error",
                    description="Moderation logs are currently unavailable."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Get recent moderation logs
            logs = await self.bot.db_manager.get_recent_moderation_logs(DELETE_LOG_LIMIT)
            
            if not logs:
                embed = embed_helper.info_embed(
                    title="🗂️ Moderation Logs",
                    description="No moderation actions have been logged yet."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Create logs embed
            embed = create_embed(
                title="🗂️ Recent Moderation Logs",
                description=f"Showing last {len(logs)} moderation actions",
                color=COLORS["info"]
            )
            
            # Add log entries
            for log in logs[:10]:  # Limit to 10 entries
                moderator_id = log['moderator_id']
                action = log['action']
                channel_id = log['channel_id']
                message_count = log['message_count']
                timestamp = log['timestamp']
                
                # Get moderator
                try:
                    moderator = self.bot.get_user(moderator_id) or await self.bot.fetch_user(moderator_id)
                    mod_name = moderator.display_name if moderator else f"User {moderator_id}"
                except:
                    mod_name = f"User {moderator_id}"
                
                # Get channel
                channel = self.bot.get_channel(channel_id)
                channel_name = channel.mention if channel else f"Channel {channel_id}"
                
                # Format action
                action_text = action.replace('_', ' ').title()
                
                # Create field value
                field_value = f"**Moderator:** {mod_name}\n"
                field_value += f"**Channel:** {channel_name}\n"
                if message_count:
                    field_value += f"**Messages:** {message_count}\n"
                field_value += f"**Time:** {timestamp}"
                
                embed.add_field(
                    name=f"🔹 {action_text}",
                    value=field_value,
                    inline=False
                )
            
            embed.set_footer(text="Moderation logs are stored permanently")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            self.logger.error(f"Error showing moderation logs: {e}")
            raise
    
    async def _error_response(self, interaction: discord.Interaction, message: str):
        """Send error response."""
        embed = embed_helper.error_embed(
            title="Moderation Error",
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
    await bot.add_cog(Moderation(bot))