"""
Birthday system cog for MalaBoT.
Handles birthday tracking, celebrations, and automatic role assignment.
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from typing import Optional

from utils.logger import get_logger
from utils.helpers import (
    embed_helper, time_helper, is_admin,
    create_embed, safe_send_message
)
from config.constants import COLORS, BIRTHDAY_ROLE_NAME
from config.settings import settings

class Birthdays(commands.Cog):
    """Birthday tracking and celebration system."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger('birthdays')
    
    @app_commands.command(name="bday", description="Birthday commands")
    @app_commands.describe(
        action="What birthday action would you like to perform?"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="set", value="set"),
        app_commands.Choice(name="view", value="view"),
        app_commands.Choice(name="check", value="check"),
        app_commands.Choice(name="list", value="list"),
        app_commands.Choice(name="next", value="next")
    ])
    async def bday(self, interaction: discord.Interaction, action: str):
        """Birthday system main command."""
        try:
            if action == "set":
                await self._bday_set(interaction)
            elif action == "view":
                await self._bday_view(interaction)
            elif action == "check":
                await self._bday_check(interaction)
            elif action == "list":
                await self._bday_list(interaction)
            elif action == "next":
                await self._bday_next(interaction)
            else:
                embed = embed_helper.error_embed(
                    title="Unknown Action",
                    description="The specified birthday action is not available."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            self.logger.error(f"Error in bday command: {e}")
            await self._error_response(interaction, "Failed to process birthday command")
    
    async def _bday_set(self, interaction: discord.Interaction):
        """Set user's birthday (requires modal input)."""
        try:
            # For now, provide instructions
            embed = embed_helper.info_embed(
                title="🎂 Set Your Birthday",
                description="To set your birthday, please use the format: MM-DD\n\n"
                           "Example: `01-15` for January 15th\n\n"
                           "Note: This is a placeholder. Full implementation requires a modal form."
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            self.logger.error(f"Error in bday set: {e}")
            raise
    
    async def _bday_view(self, interaction: discord.Interaction):
        """View user's own birthday."""
        try:
            if not self.bot.db_manager:
                embed = embed_helper.error_embed(
                    title="Database Error",
                    description="Birthday system is currently unavailable."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            birthday = await self.bot.db_manager.get_birthday(interaction.user.id)
            
            if not birthday:
                embed = embed_helper.info_embed(
                    title="🎂 No Birthday Set",
                    description="You haven't set your birthday yet!\nUse `/bday set` to add your birthday."
                )
            else:
                # Parse birthday
                month, day = birthday.split('-')
                birthday_str = datetime.strptime(birthday, "%m-%d").strftime("%B %d")
                
                # Calculate days until birthday
                days_until = time_helper.get_next_birthday_days(birthday)
                
                embed = embed_helper.birthday_embed(
                    title="🎂 Your Birthday",
                    description=f"Your birthday is set to: **{birthday_str}**\n\n"
                               f"Days until your birthday: **{days_until} days**",
                    user=interaction.user
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            self.logger.error(f"Error in bday view: {e}")
            raise
    
    async def _bday_check(self, interaction: discord.Interaction):
        """Check another user's birthday (requires user parameter)."""
        try:
            embed = embed_helper.info_embed(
                title="🎂 Check Birthday",
                description="To check another user's birthday, mention them in the command.\n\n"
                           "Note: This requires additional command parameters."
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            self.logger.error(f"Error in bday check: {e}")
            raise
    
    async def _bday_list(self, interaction: discord.Interaction):
        """List all birthdays in the server."""
        try:
            if not isinstance(interaction.channel, discord.TextChannel):
                await self._error_response(interaction, "This command can only be used in a server")
                return
            
            if not self.bot.db_manager:
                embed = embed_helper.error_embed(
                    title="Database Error",
                    description="Birthday system is currently unavailable."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Get all birthdays
            all_birthdays = await self.bot.db_manager.get_all_birthdays()
            
            if not all_birthdays:
                embed = embed_helper.info_embed(
                    title="🎂 Birthday List",
                    description="No birthdays have been set yet!"
                )
                await interaction.response.send_message(embed=embed)
                return
            
            # Sort by next upcoming birthday
            today = datetime.now()
            birthday_list = []
            
            for bday_data in all_birthdays:
                user_id = bday_data['user_id']
                birthday = bday_data['birthday']
                
                try:
                    user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
                    user_name = user.display_name if user else f"User {user_id}"
                    
                    # Calculate days until birthday
                    days_until = time_helper.get_next_birthday_days(birthday)
                    
                    # Parse birthday for display
                    birthday_str = datetime.strptime(birthday, "%m-%d").strftime("%B %d")
                    
                    birthday_list.append({
                        'name': user_name,
                        'date': birthday_str,
                        'days': days_until
                    })
                except:
                    continue
            
            # Sort by days until birthday
            birthday_list.sort(key=lambda x: x['days'])
            
            # Create embed
            embed = embed_helper.birthday_embed(
                title=f"🎂 Birthday List - {interaction.guild.name}",
                description=f"Upcoming birthdays (Total: {len(birthday_list)})"
            )
            
            # Add birthdays to embed (limit to 25 fields)
            for i, bday in enumerate(birthday_list[:25], 1):
                embed.add_field(
                    name=f"{i}. {bday['name']}",
                    value=f"📅 {bday['date']}\n⏰ In {bday['days']} days",
                    inline=True
                )
            
            if len(birthday_list) > 25:
                embed.set_footer(text=f"Showing 25 of {len(birthday_list)} birthdays")
            
            await interaction.response.send_message(embed=embed)
        
        except Exception as e:
            self.logger.error(f"Error in bday list: {e}")
            raise
    
    async def _bday_next(self, interaction: discord.Interaction):
        """Show next upcoming birthdays this month."""
        try:
            if not isinstance(interaction.channel, discord.TextChannel):
                await self._error_response(interaction, "This command can only be used in a server")
                return
            
            if not self.bot.db_manager:
                embed = embed_helper.error_embed(
                    title="Database Error",
                    description="Birthday system is currently unavailable."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Get all birthdays
            all_birthdays = await self.bot.db_manager.get_all_birthdays()
            
            if not all_birthdays:
                embed = embed_helper.info_embed(
                    title="🎂 Next Birthdays",
                    description="No birthdays have been set yet!"
                )
                await interaction.response.send_message(embed=embed)
                return
            
            # Filter for next 30 days
            upcoming = []
            
            for bday_data in all_birthdays:
                user_id = bday_data['user_id']
                birthday = bday_data['birthday']
                
                days_until = time_helper.get_next_birthday_days(birthday)
                
                if days_until <= 30:
                    try:
                        user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
                        user_name = user.display_name if user else f"User {user_id}"
                        
                        birthday_str = datetime.strptime(birthday, "%m-%d").strftime("%B %d")
                        
                        upcoming.append({
                            'name': user_name,
                            'date': birthday_str,
                            'days': days_until
                        })
                    except:
                        continue
            
            if not upcoming:
                embed = embed_helper.info_embed(
                    title="🎂 Next Birthdays",
                    description="No birthdays in the next 30 days!"
                )
                await interaction.response.send_message(embed=embed)
                return
            
            # Sort by days until birthday
            upcoming.sort(key=lambda x: x['days'])
            
            # Create embed
            embed = embed_helper.birthday_embed(
                title="🎂 Upcoming Birthdays (Next 30 Days)",
                description=f"Found {len(upcoming)} upcoming birthdays!"
            )
            
            # Add to embed
            for i, bday in enumerate(upcoming[:10], 1):
                emoji = "🎉" if bday['days'] == 0 else "🎂"
                status = "TODAY!" if bday['days'] == 0 else f"In {bday['days']} days"
                
                embed.add_field(
                    name=f"{emoji} {bday['name']}",
                    value=f"📅 {bday['date']}\n⏰ {status}",
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed)
        
        except Exception as e:
            self.logger.error(f"Error in bday next: {e}")
            raise
    
    async def _error_response(self, interaction: discord.Interaction, message: str):
        """Send error response."""
        embed = embed_helper.error_embed(
            title="Birthday System Error",
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
    await bot.add_cog(Birthdays(bot))