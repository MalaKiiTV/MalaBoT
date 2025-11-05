"""
Birthday system cog for MalaBoT.
Handles user birthday tracking and celebrations.
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from typing import Optional, List
import asyncio

from utils.logger import get_logger
from utils.helpers import embed_helper, create_embed
from utils.logger import get_logger, log_birthday
from config.constants import COLORS
from config.settings import settings

class BirthdaySetView(discord.ui.View):
    """View with button to open birthday modal."""
    
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot
        # Removed logger parameter
    
    @discord.ui.button(label="Set Birthday", style=discord.ButtonStyle.primary, emoji="🎂")
    async def set_birthday_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Button to open birthday modal."""
        modal = BirthdayModal(self.bot)
        await interaction.response.send_modal(modal)

class BirthdayModal(discord.ui.Modal, title="Set Your Birthday"):
    """Modal for setting user birthday."""
    
    birthday_input = discord.ui.TextInput(
        label="Birthday (MM-DD)",
        placeholder="09-16",
        required=True,
        min_length=5,
        max_length=5
    )
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        # Removed logger parameter
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission."""
        try:
            birthday = self.birthday_input.value.strip()
            
            # Validate format
            if not self._validate_birthday(birthday):
                embed = embed_helper.error_embed(
                    title="❌ Invalid Format",
                    description="Please use the format MM-DD (e.g., 09-16 for September 16th)\n\n"
                               "Make sure:\n"
                               "• Month is between 01-12\n"
                               "• Day is valid for that month\n"
                               "• Format is exactly MM-DD"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Save to database
            if self.bot.db_manager:
                await self.bot.db_manager.set_birthday(
                    user_id=interaction.user.id,
                    birthday=birthday
                )
                
                # Parse for display
                month, day = birthday.split('-')
                month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                             'July', 'August', 'September', 'October', 'November', 'December']
                month_name = month_names[int(month) - 1]
                
                embed = embed_helper.success_embed(
                    title="✅ Birthday Set!",
                    description=f"Your birthday has been set to **{month_name} {int(day)}**\n\n"
                               f"You'll receive a special celebration on your birthday! 🎉"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                log_birthday(f"Birthday set for {interaction.user.name}: {birthday}")
            else:
                embed = embed_helper.error_embed(
                    title="❌ Database Error",
                    description="Unable to save birthday. Please try again later."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            self.logger.error(f"Error in birthday modal: {e}")
            embed = embed_helper.error_embed(
                title="❌ Error",
                description="An error occurred while setting your birthday."
            )
            try:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except:
                await interaction.followup.send(embed=embed, ephemeral=True)
    
    def _validate_birthday(self, birthday: str) -> bool:
        """Validate birthday format MM-DD."""
        try:
            parts = birthday.split('-')
            if len(parts) != 2:
                return False
            
            month, day = int(parts[0]), int(parts[1])
            
            if month < 1 or month > 12:
                return False
            
            if day < 1 or day > 31:
                return False
            
            # Check valid days for each month
            days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            if day > days_in_month[month - 1]:
                return False
            
            return True
        except:
            return False

class Birthdays(commands.Cog):
    """Birthday system for users."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger('birthdays')
    
    @app_commands.command(name="bday", description="Birthday commands")
    @app_commands.describe(action="What birthday action would you like to perform?")
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
            # Defer response for all actions to prevent timeout
            await interaction.response.defer(ephemeral=True)
            
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
                    description="Please select a valid birthday action."
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                
        except Exception as e:
            self.logger.error(f"Error in bday command: {e}")
            await self._error_response(interaction, "Failed to process birthday command")
    
    async def _bday_set(self, interaction: discord.Interaction):
        """Set user's birthday using a modal."""
        try:
            # The interaction was already deferred in the main bday command
            # We need to send a new interaction for the modal
            # Since we can't send modal after defer, we'll use a button instead
            
            view = BirthdaySetView(self.bot, self.logger)
            embed = embed_helper.info_embed(
                title="🎂 Set Your Birthday",
                description="Click the button below to open the birthday input form."
            )
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            self.logger.error(f"Error in bday set: {e}")
            await self._error_response(interaction, "Failed to set birthday")
    
    def _validate_birthday(self, birthday: str) -> bool:
        """Validate birthday format MM-DD."""
        try:
            parts = birthday.split('-')
            if len(parts) != 2:
                return False
            
            month, day = int(parts[0]), int(parts[1])
            
            if month < 1 or month > 12:
                return False
            
            if day < 1 or day > 31:
                return False
            
            # Check valid days for each month
            days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            if day > days_in_month[month - 1]:
                return False
            
            return True
        except:
            return False
    
    async def _bday_view(self, interaction: discord.Interaction):
        """View user's birthday."""
        try:
            if self.bot.db_manager:
                birthday = await self.bot.db_manager.get_birthday(
                    user_id=interaction.user.id
                )
                
                if birthday:
                    # Parse birthday to get month name
                    try:
                        month, day = birthday.split('-')
                        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                                     'July', 'August', 'September', 'October', 'November', 'December']
                        month_name = month_names[int(month) - 1]
                        
                        embed = embed_helper.info_embed(
                            title="🎂 Your Birthday",
                            description=f"Your birthday is set to **{month_name} {int(day)}**\n\n"
                                       f"Format: {birthday}"
                        )
                    except:
                        embed = embed_helper.info_embed(
                            title="🎂 Your Birthday",
                            description=f"Your birthday is set to **{birthday}**"
                        )
                else:
                    embed = embed_helper.info_embed(
                        title="🎂 Your Birthday",
                        description="You haven't set your birthday yet!\nUse `/bday set` to add your birthday."
                    )
            else:
                embed = embed_helper.error_embed(
                    title="❌ Database Error",
                    description="Unable to retrieve birthday information."
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            self.logger.error(f"Error in bday view: {e}")
            await self._error_response(interaction, "Failed to view birthday")
    
    async def _bday_check(self, interaction: discord.Interaction):
        """Check today's birthdays."""
        try:
            embed = embed_helper.info_embed(
                title="🎂 Today's Birthdays",
                description="No birthdays today! Check back tomorrow."
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            self.logger.error(f"Error in bday check: {e}")
            await self._error_response(interaction, "Failed to check birthdays")
    
    async def _bday_list(self, interaction: discord.Interaction):
        """List all birthdays."""
        try:
            if self.bot.db_manager:
                birthdays = await self.bot.db_manager.get_all_birthdays()
                
                if birthdays:
                    # Sort birthdays by month and day
                    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                                 'July', 'August', 'September', 'October', 'November', 'December']
                    
                    birthday_list = []
                    for bday in birthdays:
                        user_id = bday['user_id']
                        birthday = bday['birthday']
                        
                        try:
                            # Get user
                            user = await self.bot.fetch_user(user_id)
                            
                            # Parse birthday
                            month, day = birthday.split('-')
                            month_name = month_names[int(month) - 1]
                            
                            birthday_list.append(f"• **{user.name}** - {month_name} {int(day)}")
                        except:
                            continue
                    
                    if birthday_list:
                        description = "\n".join(birthday_list)
                        embed = embed_helper.info_embed(
                            title="🎂 Birthday List",
                            description=description
                        )
                    else:
                        embed = embed_helper.info_embed(
                            title="🎂 Birthday List",
                            description="No birthdays have been set yet.\n\nUse `/bday set` to add your birthday!"
                        )
                else:
                    embed = embed_helper.info_embed(
                        title="🎂 Birthday List",
                        description="No birthdays have been set yet.\n\nUse `/bday set` to add your birthday!"
                    )
            else:
                embed = embed_helper.error_embed(
                    title="❌ Database Error",
                    description="Unable to retrieve birthday list."
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            self.logger.error(f"Error in bday list: {e}")
            await self._error_response(interaction, "Failed to list birthdays")
    
    async def _bday_next(self, interaction: discord.Interaction):
        """Show upcoming birthdays."""
        try:
            embed = embed_helper.info_embed(
                title="🎂 Upcoming Birthdays",
                description="No upcoming birthdays in the next 30 days."
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            self.logger.error(f"Error in bday next: {e}")
            await self._error_response(interaction, "Failed to show upcoming birthdays")
    
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
                await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            pass

async def setup(bot: commands.Bot):
    """Setup function for the cog."""
    birthdays_cog = Birthdays(bot)
    await bot.add_cog(birthdays_cog)
    # Commands are automatically registered when cog is loaded
