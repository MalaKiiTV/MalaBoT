"""
Welcome system cog for MalaBoT.
Handles welcome messages for new members with customizable embeds.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from utils.logger import get_logger
from utils.helpers import (
    embed_helper, is_admin, safe_send_message, create_embed
)
from config.constants import COLORS, DEFAULT_WELCOME_TITLE, DEFAULT_WELCOME_MESSAGE, DEFAULT_WELCOME_IMAGE
from config.settings import settings

class Welcome(commands.Cog):
    """Welcome system for new members."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger('welcome')
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Handle new member joins."""
        try:
            if not self.bot.db_manager:
                return
            
            # Get welcome settings
            welcome_channel_id = await self.bot.db_manager.get_setting('welcome_channel_id')
            welcome_title = await self.bot.db_manager.get_setting('welcome_title', DEFAULT_WELCOME_TITLE)
            welcome_message = await self.bot.db_manager.get_setting('welcome_message', DEFAULT_WELCOME_MESSAGE)
            welcome_image = await self.bot.db_manager.get_setting('welcome_image', DEFAULT_WELCOME_IMAGE)
            
            if not welcome_channel_id:
                return
            
            channel = self.bot.get_channel(welcome_channel_id)
            if not channel:
                return
            
            # Format welcome message
            formatted_message = welcome_message.replace('{member.mention}', member.mention)
            formatted_message = formatted_message.replace('{member.name}', member.name)
            formatted_message = formatted_message.replace('{server.name}', member.guild.name)
            
            # Create welcome embed
            embed = embed_helper.welcome_embed(
                title=welcome_title,
                description=formatted_message,
                user=member,
                image_url=welcome_image
            )
            
            # Add member count
            embed.add_field(
                name="👥 Member Count",
                value=f"You are member #{member.guild.member_count}!",
                inline=False
            )
            
            # Send welcome message
            await safe_send_message(channel, embed=embed)
            
            # Check for birthday catch-up
            await self._check_birthday_catchup(member)
            
            # Log welcome
            await self.bot.db_manager.log_event(
                category='WELCOME',
                action='MEMBER_JOINED',
                user_id=member.id,
                guild_id=member.guild.id,
                details=f"Member: {member.name}"
            )
        
        except Exception as e:
            self.logger.error(f"Error in on_member_join: {e}")
    
    async def _check_birthday_catchup(self, member: discord.Member):
        """Check if new member has birthday today."""
        try:
            if not self.bot.db_manager:
                return
            
            # Get member's birthday
            birthday = await self.bot.db_manager.get_birthday(member.id)
            
            if not birthday:
                return
            
            # Check if today is their birthday
            from utils.helpers import time_helper
            if time_helper.is_today(birthday):
                # Get birthday channel
                birthday_channel_id = await self.bot.db_manager.get_setting('birthday_channel_id')
                
                if birthday_channel_id:
                    channel = self.bot.get_channel(birthday_channel_id)
                    if channel:
                        embed = embed_helper.birthday_embed(
                            title="🎂 Birthday Catch-up!",
                            description=f"Happy birthday to our new member {member.mention}! 🎉🎈",
                            user=member
                        )
                        
                        embed.set_footer(text="Birthday detected on join • Welcome to the server!")
                        
                        await safe_send_message(channel, embed=embed)
                        
                        # Log birthday catch-up
                        await self.bot.db_manager.log_event(
                            category='BDAY',
                            action='CATCHUP',
                            user_id=member.id,
                            guild_id=member.guild.id,
                            details="Birthday catch-up on member join"
                        )
        
        except Exception as e:
            self.logger.error(f"Error in birthday catch-up: {e}")
    
    @app_commands.command(name="welcome", description="Welcome system configuration (Admin only)")
    @app_commands.describe(
        action="What welcome action would you like to perform?"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="setchannel", value="setchannel"),
        app_commands.Choice(name="settitle", value="settitle"),
        app_commands.Choice(name="setmessage", value="setmessage"),
        app_commands.Choice(name="setimage", value="setimage")
    ])
    async def welcome(self, interaction: discord.Interaction, action: str):
        """Welcome system configuration commands."""
        try:
            # Check permissions
            if not is_admin(interaction.user):
                embed = embed_helper.error_embed(
                    title="Permission Denied",
                    description="This command is only available to administrators."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if not self.bot.db_manager:
                embed = embed_helper.error_embed(
                    title="Database Error",
                    description="Welcome system is currently unavailable."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if action == "setchannel":
                await self._welcome_setchannel(interaction)
            elif action == "settitle":
                await self._welcome_settitle(interaction)
            elif action == "setmessage":
                await self._welcome_setmessage(interaction)
            elif action == "setimage":
                await self._welcome_setimage(interaction)
            else:
                embed = embed_helper.error_embed(
                    title="Unknown Action",
                    description="The specified welcome action is not available."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            self.logger.error(f"Error in welcome command: {e}")
            await self._error_response(interaction, "Failed to process welcome command")
    
    async def _welcome_setchannel(self, interaction: discord.Interaction):
        """Set welcome channel."""
        try:
            channel_id = interaction.channel.id
            
            await self.bot.db_manager.set_setting('welcome_channel_id', channel_id)
            
            embed = embed_helper.success_embed(
                title="✅ Welcome Channel Set",
                description=f"This channel ({interaction.channel.mention}) has been set as the welcome channel.\n\n"
                           "New members will receive welcome messages here."
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Log admin action
            await self.bot.db_manager.log_event(
                category='ADMIN',
                action='WELCOME_CHANNEL_SET',
                user_id=interaction.user.id,
                channel_id=channel_id,
                guild_id=interaction.guild.id,
                details=f"Welcome channel set to {channel_id}"
            )
        
        except Exception as e:
            self.logger.error(f"Error setting welcome channel: {e}")
            raise
    
    async def _welcome_settitle(self, interaction: discord.Interaction):
        """Set welcome title (requires text input)."""
        try:
            embed = embed_helper.info_embed(
                title="👋 Set Welcome Title",
                description="To set a custom welcome title, use this command with a title parameter.\n\n"
                           "Example: `/welcome settitle Welcome to our server!`\n\n"
                           "Note: This is a placeholder. Full implementation requires additional parameters."
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            self.logger.error(f"Error in welcome settitle: {e}")
            raise
    
    async def _welcome_setmessage(self, interaction: discord.Interaction):
        """Set welcome message (requires text input)."""
        try:
            embed = embed_helper.info_embed(
                title="👋 Set Welcome Message",
                description="To set a custom welcome message, use this command with a message parameter.\n\n"
                           "Available placeholders:\n"
                           "• `{member.mention}` - Mentions the new member\n"
                           "• `{member.name}` - Member's username\n"
                           "• `{server.name}` - Server name\n\n"
                           "Example: `Welcome {member.mention} to {server.name}!`\n\n"
                           "Note: This is a placeholder. Full implementation requires additional parameters."
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            self.logger.error(f"Error in welcome setmessage: {e}")
            raise
    
    async def _welcome_setimage(self, interaction: discord.Interaction):
        """Set welcome image (requires URL input)."""
        try:
            embed = embed_helper.info_embed(
                title="👋 Set Welcome Image",
                description="To set a custom welcome image, use this command with an image URL parameter.\n\n"
                           "Example: `/welcome setimage https://example.com/image.png`\n\n"
                           "Note: This is a placeholder. Full implementation requires additional parameters."
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            self.logger.error(f"Error in welcome setimage: {e}")
            raise
    
    async def _error_response(self, interaction: discord.Interaction, message: str):
        """Send error response."""
        embed = embed_helper.error_embed(
            title="Welcome System Error",
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
    await bot.add_cog(Welcome(bot))