"""
Moderation system cog for MalaBoT.
Handles message deletion, channel management, and moderation logging.
"""

import discord
import asyncio
from discord import app_commands
from discord.ext import commands
from typing import Optional

from utils.logger import get_logger, log_moderation
from utils.helpers import (
    embed_helper, is_owner, safe_send_message, create_embed
)
from config.constants import COLORS, DELETE_LOG_LIMIT
from config.settings import settings

class Moderation(commands.Cog):
    """Moderation tools and logging."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger('moderation')
    
    @app_commands.command(name="delete", description="Message deletion commands (Owner only)")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(action="What deletion action would you like to perform?")
    @app_commands.choices(action=[
        app_commands.Choice(name="last10", value="last10"),
        app_commands.Choice(name="last50", value="last50"),
        app_commands.Choice(name="all", value="all"),
        app_commands.Choice(name="logs", value="logs")
    ])
    async def delete(self, interaction: discord.Interaction, action: str):
        """Message deletion commands."""
        try:
            # Check if user is in a guild
            if not interaction.guild:
                embed = embed_helper.error_embed(
                    title="Invalid Context",
                    description="This command can only be used in a server."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Check if user is owner, admin, or staff
            from utils.helpers import is_staff
            is_bot_owner = is_owner(interaction.user)
            has_admin_perm = (interaction.user.guild_permissions.administrator or 
                             interaction.user.guild_permissions.manage_guild)
            has_staff_role = await is_staff(interaction, self.db)
            
            if not (is_bot_owner or has_admin_perm or has_staff_role):
                embed = embed_helper.error_embed(
                    title="🚫 Permission Denied",
                    description=f"This command is only available to:\n\n"
                               f"• Bot Owners\n"
                               f"• Server Administrators\n"
                               f"• Staff Members (configured role)\n\n"
                               f"Your current permissions:\n"
                               f"• Bot Owner: {'✅' if is_bot_owner else '❌'}\n"
                               f"• Administrator: {'✅' if interaction.user.guild_permissions.administrator else '❌'}\n"
                               f"• Staff Role: {'✅' if has_staff_role else '❌'}"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                self.logger.warning(f"Unauthorized moderation command attempt by {interaction.user.name} ({interaction.user.id})")
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
            
            await interaction.response.defer(ephemeral=True)
            
            deleted = await channel.purge(limit=10)
            
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
            
            embed = embed_helper.success_embed(
                title="✅ Messages Deleted",
                description=f"Successfully deleted {len(deleted)} messages."
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            log_moderation(f"🗑 {interaction.user.name} deleted {len(deleted)} messages in #{channel.name}")
            
            if self.bot.db_manager:
                mod_log_channel_id = await self.bot.db_manager.get_setting('moderation_log_channel_id')
                if mod_log_channel_id:
                    mod_log_channel = self.bot.get_channel(mod_log_channel_id)
                    if mod_log_channel:
                        log_embed = create_embed(
                            title="🗑 Messages Deleted",
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
            
            await interaction.response.defer(ephemeral=True)
            
            deleted = await channel.purge(limit=50)
            
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
            
            embed = embed_helper.success_embed(
                title="✅ Messages Deleted",
                description=f"Successfully deleted {len(deleted)} messages."
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            log_moderation(f"🗑 {interaction.user.name} deleted {len(deleted)} messages in #{channel.name}")
            
            if self.bot.db_manager:
                mod_log_channel_id = await self.bot.db_manager.get_setting('moderation_log_channel_id')
                if mod_log_channel_id:
                    mod_log_channel = self.bot.get_channel(mod_log_channel_id)
                    if mod_log_channel:
                        log_embed = create_embed(
                            title="🗑 Messages Deleted",
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
            
            await interaction.response.defer(ephemeral=True)
            
            new_channel = await channel.clone(reason=f"Channel purge by {interaction.user.name}")
            await new_channel.edit(position=channel.position)
            await channel.delete(reason=f"Channel purge by {interaction.user.name}")
            
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
            
            embed = embed_helper.warning_embed(
                title="⚠️ Channel Purged",
                description=f"This channel was purged by {interaction.user.mention}.\n\n"
                           f"All previous messages have been deleted."
            )
            
            await safe_send_message(new_channel, embed=embed)
            
            log_moderation(f"🗑 {interaction.user.name} purged channel #{new_channel.name}")
            
            if self.bot.db_manager:
                mod_log_channel_id = await self.bot.db_manager.get_setting('moderation_log_channel_id')
                if mod_log_channel_id:
                    mod_log_channel = self.bot.get_channel(mod_log_channel_id)
                    if mod_log_channel:
                        log_embed = create_embed(
                            title="🗑 Channel Purged",
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
            
            logs = await self.bot.db_manager.get_recent_moderation_logs(DELETE_LOG_LIMIT)
            
            if not logs:
                embed = embed_helper.info_embed(
                    title="📋 Moderation Logs",
                    description="No moderation actions have been logged yet."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            embed = create_embed(
                title="📋 Recent Moderation Logs",
                description=f"Showing last {len(logs)} moderation actions",
                color=COLORS["info"]
            )
            
            for log in logs[:10]:
                moderator_id = log['moderator_id']
                action = log['action']
                channel_id = log['channel_id']
                message_count = log['message_count']
                timestamp = log['timestamp']
                
                try:
                    moderator = self.bot.get_user(moderator_id) or await self.bot.fetch_user(moderator_id)
                    mod_name = moderator.display_name if moderator else f"User {moderator_id}"
                except:
                    mod_name = f"User {moderator_id}"
                
                channel = self.bot.get_channel(channel_id)
                channel_name = channel.mention if channel else f"Channel {channel_id}"
                
                action_text = action.replace('_', ' ').title()
                
                field_value = f"**Moderator:** {mod_name}\n"
                field_value += f"**Channel:** {channel_name}\n"
                if message_count:
                    field_value += f"**Messages:** {message_count}\n"
                field_value += f"**Time:** {timestamp}"
                
                embed.add_field(
                    name=f"🔸 {action_text}",
                    value=field_value,
                    inline=False
                )
            
            embed.set_footer(text="Moderation logs are stored permanently")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            self.logger.error(f"Error showing moderation logs: {e}")
            raise
    
    @app_commands.command(name="kick", description="Kick a user from the server (Owner only)")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(user="The user to kick", reason="Reason for kick")
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        """Kick a user from the server."""
        try:
            # Check if user is owner, admin, or staff
            from utils.helpers import is_staff
            is_bot_owner = is_owner(interaction.user)
            has_admin_perm = (interaction.user.guild_permissions.administrator or 
                             interaction.user.guild_permissions.kick_members)
            has_staff_role = await is_staff(interaction, self.db)
            
            if not (is_bot_owner or has_admin_perm or has_staff_role):
                embed = embed_helper.error_embed(
                    title="⛔ Permission Denied",
                    description=f"This command is only available to:\n\n"
                               f"• Bot Owners\n"
                               f"• Server Administrators\n"
                               f"• Staff Members (configured role)\n\n"
                               f"Your current permissions:\n"
                               f"• Bot Owner: {'✅' if is_bot_owner else '❌'}\n"
                               f"• Administrator: {'✅' if interaction.user.guild_permissions.administrator else '❌'}\n"
                               f"• Staff Role: {'✅' if has_staff_role else '❌'}"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                self.logger.warning(f"Unauthorized kick command attempt by {interaction.user.name} ({interaction.user.id})")
                return
            
            # Check if user is trying to kick themselves
            if user.id == interaction.user.id:
                embed = embed_helper.error_embed(
                    title="Invalid Action",
                    description="You cannot kick yourself!"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Check if user has higher or equal role
            if user.top_role >= interaction.user.top_role and interaction.user.id not in settings.OWNER_IDS:
                embed = embed_helper.error_embed(
                    title="Permission Denied",
                    description="You cannot kick a user with an equal or higher role!"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Kick the user
            await user.kick(reason=f"{reason} | Kicked by {interaction.user.name}")
            
            # Create success embed
            embed = embed_helper.success_embed(
                title="👢 User Kicked",
                description=f"{user.mention} has been kicked from the server.\n**Reason:** {reason}"
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Log the action
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category='MOD',
                    action='KICK',
                    user_id=interaction.user.id,
                    target_id=user.id,
                    guild_id=interaction.guild.id,
                    details=f"Kicked {user.name}#{user.discriminator} - Reason: {reason}"
                )
            
            log_moderation(f"👢 {interaction.user.name} kicked {user.name}#{user.discriminator} - Reason: {reason}")
            
        except discord.Forbidden:
            embed = embed_helper.error_embed(
                title="Permission Error",
                description="I don't have permission to kick this user."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            self.logger.error(f"Error in kick command: {e}")
            await self._error_response(interaction, "Failed to kick user")

    @app_commands.command(name="ban", description="Ban a user from the server (Owner only)")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(user="The user to ban", reason="Reason for ban")
    async def ban(self, interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
        """Ban a user from the server."""
        try:
            # Check if user is owner, admin, or staff
            from utils.helpers import is_staff
            is_bot_owner = is_owner(interaction.user)
            has_admin_perm = (interaction.user.guild_permissions.administrator or 
                             interaction.user.guild_permissions.ban_members)
            has_staff_role = await is_staff(interaction, self.db)
            
            if not (is_bot_owner or has_admin_perm or has_staff_role):
                embed = embed_helper.error_embed(
                    title="⛔ Permission Denied",
                    description=f"This command is only available to:\n\n"
                               f"• Bot Owners\n"
                               f"• Server Administrators\n"
                               f"• Staff Members (configured role)\n\n"
                               f"Your current permissions:\n"
                               f"• Bot Owner: {'✅' if is_bot_owner else '❌'}\n"
                               f"• Administrator: {'✅' if interaction.user.guild_permissions.administrator else '❌'}\n"
                               f"• Staff Role: {'✅' if has_staff_role else '❌'}"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                self.logger.warning(f"Unauthorized ban command attempt by {interaction.user.name} ({interaction.user.id})")
                return
            
            # Check if user is trying to ban themselves
            if user.id == interaction.user.id:
                embed = embed_helper.error_embed(
                    title="Invalid Action",
                    description="You cannot ban yourself!"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Check if user has higher or equal role (if member)
            if isinstance(user, discord.Member) and user.top_role >= interaction.user.top_role and interaction.user.id not in settings.OWNER_IDS:
                embed = embed_helper.error_embed(
                    title="Permission Denied",
                    description="You cannot ban a user with an equal or higher role!"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Ban the user
            await interaction.guild.ban(user, reason=f"{reason} | Banned by {interaction.user.name}")
            
            # Create success embed
            embed = embed_helper.success_embed(
                title="🔨 User Banned",
                description=f"{user.mention} has been banned from the server.\n**Reason:** {reason}"
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Log the action
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category='MOD',
                    action='BAN',
                    user_id=interaction.user.id,
                    target_id=user.id,
                    guild_id=interaction.guild.id,
                    details=f"Banned {user.name}#{user.discriminator} - Reason: {reason}"
                )
            
            log_moderation(f"🔨 {interaction.user.name} banned {user.name}#{user.discriminator} - Reason: {reason}")
            
        except discord.Forbidden:
            embed = embed_helper.error_embed(
                title="Permission Error",
                description="I don't have permission to ban this user."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            self.logger.error(f"Error in ban command: {e}")
            await self._error_response(interaction, "Failed to ban user")

    @app_commands.command(name="mute", description="Mute a user in the server (Owner only)")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(user="The user to mute", duration="Mute duration in minutes", reason="Reason for mute")
    async def mute(self, interaction: discord.Interaction, user: discord.Member, duration: int = 10, reason: str = "No reason provided"):
        """Mute a user in the server."""
        try:
            # Check if user is owner, admin, or staff
            from utils.helpers import is_staff
            is_bot_owner = is_owner(interaction.user)
            has_admin_perm = (interaction.user.guild_permissions.administrator or 
                             interaction.user.guild_permissions.moderate_members)
            has_staff_role = await is_staff(interaction, self.db)
            
            if not (is_bot_owner or has_admin_perm or has_staff_role):
                embed = embed_helper.error_embed(
                    title="⛔ Permission Denied",
                    description=f"This command is only available to:\n\n"
                               f"• Bot Owners\n"
                               f"• Server Administrators\n"
                               f"• Staff Members (configured role)\n\n"
                               f"Your current permissions:\n"
                               f"• Bot Owner: {'✅' if is_bot_owner else '❌'}\n"
                               f"• Administrator: {'✅' if interaction.user.guild_permissions.administrator else '❌'}\n"
                               f"• Staff Role: {'✅' if has_staff_role else '❌'}"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                self.logger.warning(f"Unauthorized mute command attempt by {interaction.user.name} ({interaction.user.id})")
                return
            
            # Check if user is trying to mute themselves
            if user.id == interaction.user.id:
                embed = embed_helper.error_embed(
                    title="Invalid Action",
                    description="You cannot mute yourself!"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Check if user has higher or equal role
            if user.top_role >= interaction.user.top_role and interaction.user.id not in settings.OWNER_IDS:
                embed = embed_helper.error_embed(
                    title="Permission Denied",
                    description="You cannot mute a user with an equal or higher role!"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Get or create muted role
            muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
            if not muted_role:
                muted_role = await interaction.guild.create_role(name="Muted", reason="Muted role for moderation")
                
                # Update channel permissions for the muted role
                for channel in interaction.guild.channels:
                    if isinstance(channel, discord.TextChannel):
                        await channel.set_permissions(muted_role, send_messages=False, add_reactions=False)
                    elif isinstance(channel, discord.VoiceChannel):
                        await channel.set_permissions(muted_role, connect=False, speak=False)
            
            # Mute the user
            await user.add_roles(muted_role, reason=f"{reason} | Muted by {interaction.user.name}")
            
            # Create success embed
            embed = embed_helper.success_embed(
                title="🔇 User Muted",
                description=f"{user.mention} has been muted for {duration} minutes.\n**Reason:** {reason}"
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Log the action
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category='MOD',
                    action='MUTE',
                    user_id=interaction.user.id,
                    target_id=user.id,
                    guild_id=interaction.guild.id,
                    details=f"Muted {user.name}#{user.discriminator} for {duration} minutes - Reason: {reason}"
                )
            
            log_moderation(f"🔇 {interaction.user.name} muted {user.name}#{user.discriminator} for {duration} minutes - Reason: {reason}")
            
            # Schedule unmute
            await asyncio.sleep(duration * 60)
            if muted_role in user.roles:
                await user.remove_roles(muted_role, reason="Temporary mute expired")
                try:
                    await user.send(f"You have been unmuted in {interaction.guild.name}")
                except:
                    pass  # Can't send DM, that's okay
            
        except discord.Forbidden:
            embed = embed_helper.error_embed(
                title="Permission Error",
                description="I don't have permission to mute this user."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            self.logger.error(f"Error in mute command: {e}")
            await self._error_response(interaction, "Failed to mute user")

    @app_commands.command(name="unmute", description="Unmute a user in the server (Owner only)")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(user="The user to unmute", reason="Reason for unmute")
    async def unmute(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        """Unmute a user in the server."""
        try:
            # Check if user is owner, admin, or staff
            from utils.helpers import is_staff
            is_bot_owner = is_owner(interaction.user)
            has_admin_perm = (interaction.user.guild_permissions.administrator or 
                             interaction.user.guild_permissions.moderate_members)
            has_staff_role = await is_staff(interaction, self.db)
            
            if not (is_bot_owner or has_admin_perm or has_staff_role):
                embed = embed_helper.error_embed(
                    title="⛔ Permission Denied",
                    description=f"This command is only available to:\n\n"
                               f"• Bot Owners\n"
                               f"• Server Administrators\n"
                               f"• Staff Members (configured role)\n\n"
                               f"Your current permissions:\n"
                               f"• Bot Owner: {'✅' if is_bot_owner else '❌'}\n"
                               f"• Administrator: {'✅' if interaction.user.guild_permissions.administrator else '❌'}\n"
                               f"• Staff Role: {'✅' if has_staff_role else '❌'}"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                self.logger.warning(f"Unauthorized unmute command attempt by {interaction.user.name} ({interaction.user.id})")
                return
            
            # Get muted role
            muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
            if not muted_role:
                embed = embed_helper.error_embed(
                    title="Role Not Found",
                    description="Muted role doesn't exist. User may not be muted."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Check if user has muted role
            if muted_role not in user.roles:
                embed = embed_helper.error_embed(
                    title="User Not Muted",
                    description="This user is not currently muted."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Unmute the user
            await user.remove_roles(muted_role, reason=f"{reason} | Unmuted by {interaction.user.name}")
            
            # Create success embed
            embed = embed_helper.success_embed(
                title="🔊 User Unmuted",
                description=f"{user.mention} has been unmuted.\n**Reason:** {reason}"
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Log the action
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category='MOD',
                    action='UNMUTE',
                    user_id=interaction.user.id,
                    target_id=user.id,
                    guild_id=interaction.guild.id,
                    details=f"Unmuted {user.name}#{user.discriminator} - Reason: {reason}"
                )
            
            log_moderation(f"🔊 {interaction.user.name} unmuted {user.name}#{user.discriminator} - Reason: {reason}")
            
        except discord.Forbidden:
            embed = embed_helper.error_embed(
                title="Permission Error",
                description="I don't have permission to unmute this user."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            self.logger.error(f"Error in unmute command: {e}")
            await self._error_response(interaction, "Failed to unmute user")

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
    cog = Moderation(bot)
    await bot.add_cog(cog)
    # Register slash commands with the tree
    bot.tree.add_command(cog.delete, override=True)
    bot.tree.add_command(cog.kick, override=True)
    bot.tree.add_command(cog.ban, override=True)
    bot.tree.add_command(cog.mute, override=True)
    bot.tree.add_command(cog.unmute, override=True)
