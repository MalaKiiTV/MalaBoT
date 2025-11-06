"""
Birthday system cog for MalaBoT.
Handles user birthday tracking and celebrations.
"""

from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from utils.helpers import create_embed
from utils.logger import get_logger


class BirthdayModal(discord.ui.Modal, title="Set Your Birthday"):
    """Modal for users to set their birthday."""

    birthday = discord.ui.TextInput(
        label="Your Birthday (MM-DD format)",
        placeholder="12-25",
        required=True,
        min_length=5,
        max_length=5,
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        """Handle birthday submission."""
        try:
            # Parse birthday input
            birthday_str = self.birthday.value.strip()
            month, day = map(int, birthday_str.split("-"))

            # Validate date
            if month < 1 or month > 12 or day < 1 or day > 31:
                await interaction.response.send_message(
                    embed=create_embed(
                        "❌ Invalid Date",
                        "Please enter a valid date in MM-DD format.",
                        discord.Color.red(),
                    ),
                    ephemeral=True,
                )
                return

            # Check for February 30th, April 31st, etc.
            invalid_dates = [
                (2, 29),
                (2, 30),
                (2, 31),  # February
                (4, 31),
                (6, 31),
                (9, 31),
                (11, 31),  # 30-day months
            ]

            if (month, day) in invalid_dates:
                # Special case for Feb 29 - allow it but handle leap years
                if not (month == 2 and day == 29):
                    await interaction.response.send_message(
                        embed=create_embed(
                            "❌ Invalid Date",
                            "That date doesn't exist. Please enter a valid date.",
                            discord.Color.red(),
                        ),
                        ephemeral=True,
                    )
                    return

            # Store in database
            success = await self.bot.db_manager.set_user_birthday(  # type: ignore
                interaction.user.id, birthday_str
            )

            if success:
                await interaction.response.send_message(
                    embed=create_embed(
                        "🎂 Birthday Set!",
                        f"Your birthday has been set to {birthday_str}. "
                        "You'll receive a special message on your birthday!",
                        discord.Color.green(),
                    ),
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    embed=create_embed(
                        "❌ Database Error",
                        "There was an error saving your birthday. Please try again.",
                        discord.Color.red(),
                    ),
                    ephemeral=True,
                )

        except ValueError:
            await interaction.response.send_message(
                embed=create_embed(
                    "❌ Invalid Format",
                    "Please use MM-DD format (e.g., 12-25 for December 25th).",
                    discord.Color.red(),
                ),
                ephemeral=True,
            )
        except Exception:
            await interaction.response.send_message(
                embed=create_embed(
                    "❌ Error",
                    "An unexpected error occurred. Please try again.",
                    discord.Color.red(),
                ),
                ephemeral=True,
            )


class Birthdays(commands.Cog):
    """Birthday system for users."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger("birthdays")
        # Type ignore to handle MyPy Bot class attribute issue
        self.db = bot.db_manager  # type: ignore  # type: ignore  # type: ignore

    @app_commands.command(name="bday", description="Birthday commands")
    @app_commands.describe(action="What birthday action would you like to perform?")
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Set Birthday", value="set"),
            app_commands.Choice(name="View Birthday", value="view"),
            app_commands.Choice(name="List Today's Birthdays", value="list"),
            app_commands.Choice(name="Remove Birthday", value="remove"),
        ]
    )
    async def birthday(self, interaction: discord.Interaction, action: str):
        """Main birthday command handler."""

        if action == "set":
            modal = BirthdayModal(self.bot)
            await interaction.response.send_modal(modal)

        elif action == "view":
            await self._view_birthday(interaction)

        elif action == "list":
            await self._list_birthdays(interaction)

        elif action == "remove":
            await self._remove_birthday(interaction)

    async def _view_birthday(self, interaction: discord.Interaction):
        """View your birthday."""
        try:
            birthday_data = await self.bot.db_manager.get_user_birthday(interaction.user.id)  # type: ignore

            if birthday_data:
                birthday_str = birthday_data[1]  # birthday is at index 1
                # Format the birthday string to be more readable
                month, day = map(int, birthday_str.split("-"))
                month_names = [
                    "January",
                    "February",
                    "March",
                    "April",
                    "May",
                    "June",
                    "July",
                    "August",
                    "September",
                    "October",
                    "November",
                    "December",
                ]
                formatted_date = (
                    f"{month_names[month-1]} {day}{self._get_ordinal_suffix(day)}"
                )

                embed = create_embed(
                    "🎂 Your Birthday",
                    f"Your birthday is set to **{formatted_date}** ({birthday_str})",
                    discord.Color.blue(),
                )
                embed.add_field(
                    name="Want to change it?",
                    value="Use `/bday set` to update your birthday.",
                    inline=False,
                )
            else:
                embed = create_embed(
                    "❌ No Birthday Set",
                    "You haven't set your birthday yet!\n\n"
                    "Use `/bday set` to set your birthday and get special messages on your special day!",
                    discord.Color.orange(),
                )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            self.logger.error(
                f"Error viewing birthday for user {interaction.user.id}: {e}"
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "❌ Error",
                    "There was an error retrieving your birthday. Please try again.",
                    discord.Color.red(),
                ),
                ephemeral=True,
            )

    async def _list_birthdays(self, interaction: discord.Interaction):
        """List today's birthdays."""
        try:
            today = datetime.now().strftime("%m-%d")
            today_birthdays = await self.bot.db_manager.get_today_birthdays(today)  # type: ignore

            if today_birthdays:
                # Format the list
                birthday_list = []
                for user_data in today_birthdays:
                    user_id = user_data[0]
                    try:
                        user = await self.bot.fetch_user(user_id)
                        if user:
                            # Get user's display name
                            display_name = user.display_name
                            birthday_list.append(f"🎉 {display_name}")
                    except:
                        birthday_list.append(f"🎉 User {user_id}")

                embed = create_embed(
                    "🎂 Today's Birthdays!",
                    "\n".join(birthday_list),
                    discord.Color.magenta(),
                )
                embed.set_footer(text="🎊 Wish them a happy birthday!")
            else:
                embed = create_embed(
                    "🎂 Today's Birthdays",
                    "No birthdays today! 🎈",
                    discord.Color.blue(),
                )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"Error listing birthdays: {e}")
            await interaction.response.send_message(
                embed=create_embed(
                    "❌ Error",
                    "There was an error retrieving today's birthdays. Please try again.",
                    discord.Color.red(),
                ),
                ephemeral=True,
            )

    async def _remove_birthday(self, interaction: discord.Interaction):
        """Remove your birthday."""
        try:
            success = await self.bot.db_manager.remove_user_birthday(interaction.user.id)  # type: ignore

            if success:
                embed = create_embed(
                    "🗑️ Birthday Removed",
                    "Your birthday has been removed from the system.\n"
                    "You can set it again anytime with `/bday set`.",
                    discord.Color.orange(),
                )
            else:
                embed = create_embed(
                    "❌ No Birthday Found",
                    "You don't have a birthday set in the system.",
                    discord.Color.red(),
                )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            self.logger.error(
                f"Error removing birthday for user {interaction.user.id}: {e}"
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "❌ Error",
                    "There was an error removing your birthday. Please try again.",
                    discord.Color.red(),
                ),
                ephemeral=True,
            )

    def _get_ordinal_suffix(self, day: int) -> str:
        """Get ordinal suffix for day (1st, 2nd, 3rd, 4th, etc.)."""
        if 11 <= day <= 13:
            return "th"
        return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    # Daily birthday check task
    async def check_birthdays(self):
        """Check for today's birthdays and send celebration messages."""
        try:
            # Get today's date in MM-DD format
            today = datetime.now().strftime("%m-%d")
            today_birthdays = await self.bot.db_manager.get_today_birthdays(today)  # type: ignore

            for user_data in today_birthdays:
                user_id = user_data[0]
                try:
                    # Try to fetch user
                    user = await self.bot.fetch_user(user_id)
                    if user:
                        # Send birthday message
                        embed = create_embed(
                            "🎂 Happy Birthday! 🎉",
                            f"Happy birthday to **{user.display_name}**! 🎊\n\n"
                            "Hope you have an amazing day filled with joy and celebration! 🎈",
                            discord.Color.magenta(),
                        )
                        embed.set_thumbnail(
                            url=user.display_avatar.url if user.display_avatar else None
                        )

                        # Try to send to a configured birthday channel or DM
                        # For now, we'll try to DM the user
                        try:
                            await user and user.send(embed=embed)
                            self.logger.info(f"Sent birthday message to user {user_id}")
                        except discord.Forbidden:
                            self.logger.warning(
                                f"Could not DM user {user_id} for birthday"
                            )

                except discord.NotFound:
                    self.logger.warning(f"User {user_id} not found for birthday check")
                except Exception as e:
                    self.logger.error(
                        f"Error processing birthday for user {user_id}: {e}"
                    )

        except Exception as e:
            self.logger.error(f"Error in birthday check: {e}")


async def setup(bot: commands.Bot):
    """Setup function for the birthdays cog."""
    await bot.add_cog(Birthdays(bot))
