"""
Birthday Cog for MalaBoT.
Handles setting, viewing, and announcing birthdays.
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

from utils.logger import get_logger
from utils.helpers import create_embed
from config.constants import COLORS

class BirthdayModal(discord.ui.Modal, title="Set Your Birthday"):
    """Modal for users to set their birthday."""
    
    date_input = discord.ui.TextInput(
        label="Birthday (MM-DD format)",
        placeholder="e.g., 09-16",
        required=True,
        min_length=5,
        max_length=5,
    )

    year_input = discord.ui.TextInput(
        label="Year of Birth (Optional)",
        placeholder="e.g., 1999",
        required=False,
        min_length=4,
        max_length=4,
    )

    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission."""
        try:
            # Validate date format
            bday_date = datetime.strptime(self.date_input.value, "%m-%d").date()
            
            # Validate year if provided
            year = None
            if self.year_input.value:
                try:
                    year_val = int(self.year_input.value)
                    if not (1900 < year_val < datetime.now().year):
                        raise ValueError
                    year = str(year_val)
                except ValueError:
                    await interaction.response.send_message(
                        embed=create_embed("Invalid Year", "Please enter a valid year (e.g., 1999).", COLORS["error"]),
                        ephemeral=True,
                    )
                    return
            
            await self.cog.db.set_birthday(interaction.user.id, bday_date.strftime('%m-%d'), year)
            
            display_date = f"{bday_date.strftime('%B %d')}, {year}" if year else bday_date.strftime('%B %d')

            await interaction.response.send_message(
                embed=create_embed("Birthday Set!", f"Your birthday is now set to **{display_date}**.", COLORS["success"]),
                ephemeral=True,
            )

        except ValueError:
            await interaction.response.send_message(
                embed=create_embed("Invalid Date Format", "Please use `MM-DD` format (e.g., 09-16).", COLORS["error"]),
                ephemeral=True,
            )
        except Exception as e:
            self.cog.logger.error(f"Error in birthday modal: {e}")
            await interaction.response.send_message(
                embed=create_embed("Error", "An unexpected error occurred.", COLORS["error"]),
                ephemeral=True,
            )


class BirthdayGroup(app_commands.Group):
    """Birthday command group."""
    def __init__(self, cog):
        super().__init__(name="bday", description="Birthday related commands")
        self.cog = cog

    @app_commands.command(name="set", description="Set your birthday")
    async def set(self, interaction: discord.Interaction):
        """Opens a modal for the user to set their birthday."""
        modal = BirthdayModal(self.cog)
        await interaction.response.send_modal(modal)

    @app_commands.command(name="view", description="View a user's birthday")
    async def view(self, interaction: discord.Interaction, user: discord.Member = None):
        """View your own or another user's birthday."""
        target = user or interaction.user
        try:
            birthday_data = await self.cog.db.get_birthday(target.id)
            if birthday_data:
                # Correct tuple indices: (id, user_id, birthday, year, timezone, announced_year, created_at)
                bday_str = birthday_data[2]
                year_str = birthday_data[3]

                bday_date = datetime.strptime(bday_str, '%m-%d')
                display_date = f"{bday_date.strftime('%B %d')}, {year_str}" if year_str else bday_date.strftime('%B %d')
                
                embed = create_embed(f"🎂 {target.display_name}'s Birthday", f"Their birthday is on **{display_date}**.", COLORS["info"])
            else:
                embed = create_embed(f"🎂 {target.display_name}'s Birthday", "They haven't set their birthday yet.", COLORS["warning"])
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            self.cog.logger.error(f"Error in bday view: {e}")
            await interaction.response.send_message(
                embed=create_embed("Error", "Could not retrieve birthday information.", COLORS["error"]),
                ephemeral=True,
            )

    @app_commands.command(name="list", description="List all upcoming birthdays")
    async def list(self, interaction: discord.Interaction):
        """Lists all birthdays in the server."""
        try:
            all_birthdays = await self.cog.db.get_all_birthdays()
            if not all_birthdays:
                await interaction.response.send_message(
                    embed=create_embed("No Birthdays Set", "No one has set their birthday in this server yet.", COLORS["info"]),
                    ephemeral=True,
                )
                return

            description = "Here are the upcoming birthdays:\n\n"
            sorted_bdays = sorted(all_birthdays, key=lambda row: datetime.strptime(row[2], '%m-%d').strftime('%m%d'))
            
            for row in sorted_bdays:
                # Correct tuple indices: (id, user_id, birthday, year, ...)
                user_id = row[1]
                bday_str = row[2]
                bday_date = datetime.strptime(bday_str, '%m-%d')
                
                user = interaction.guild.get_member(user_id)
                if user:
                    description += f"• **{bday_date.strftime('%B %d')}** - {user.mention}\n"
            
            embed = create_embed("🎂 Birthday List", description, COLORS["primary"])
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            self.cog.logger.error(f"Error in bday list: {e}")
            await interaction.response.send_message(
                embed=create_embed("Error", "Could not retrieve the birthday list.", COLORS["error"]),
                ephemeral=True,
            )

    @app_commands.command(name="next", description="Show the next upcoming birthday")
    async def next(self, interaction: discord.Interaction):
        """Shows the next upcoming birthday."""
        try:
            all_birthdays = await self.cog.db.get_all_birthdays()
            if not all_birthdays:
                await interaction.response.send_message(
                    embed=create_embed("No Birthdays Set", "No one has set their birthday yet.", COLORS["info"]),
                    ephemeral=True,
                )
                return

            today = datetime.now().date()
            today_str = today.strftime('%m%d')

            sorted_bdays = sorted(all_birthdays, key=lambda row: datetime.strptime(row[2], '%m-%d').strftime('%m%d'))
            
            next_bday = None
            for row in sorted_bdays:
                bday_date_str = datetime.strptime(row[2], '%m-%d').strftime('%m%d')
                if bday_date_str >= today_str:
                    next_bday = row
                    break
            
            if next_bday is None and sorted_bdays:
                next_bday = sorted_bdays[0]

            if next_bday:
                user_id = next_bday[1]
                bday_str = next_bday[2]
                bday_date = datetime.strptime(bday_str, '%m-%d')
                
                user = interaction.guild.get_member(user_id)
                if user:
                    embed = create_embed("🎉 Next Birthday", f"The next birthday is for {user.mention} on **{bday_date.strftime('%B %d')}**!", COLORS["info"])
                else:
                    embed = create_embed("🎉 Next Birthday", "Could not find the next user.", COLORS["warning"])
            else:
                 embed = create_embed("No Birthdays Set", "No birthdays have been set.", COLORS["warning"])

            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            self.cog.logger.error(f"Error in bday next: {e}")
            await interaction.response.send_message(
                embed=create_embed("Error", "Could not determine the next birthday.", COLORS["error"]),
                ephemeral=True,
            )


class Birthdays(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db_manager
        self.logger = get_logger('birthdays')
        self._bday_group = BirthdayGroup(self)

    async def cog_load(self):
        """Add the command group to the bot's command tree."""
        self.bot.tree.add_command(self._bday_group)

    async def cog_unload(self):
        """Remove the command group from the bot's command tree."""
        self.bot.tree.remove_command(self._bday_group.name)


async def setup(bot: commands.Bot):
    await bot.add_cog(Birthdays(bot))