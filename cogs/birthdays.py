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
            app_commands.Choice(name="List All Birthdays", value="list"),
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
                birthday_str = str(
                    birthday_data[2]
                )  # birthday is at index 2 (0=id, 1=user_id, 2=birthday)

                # Check if birthday data is corrupted (doesn't contain a dash)
                if "-" not in birthday_str or birthday_str.isdigit():
                    # Corrupted data - remove and notify user
                    await self.bot.db_manager.remove_user_birthday(interaction.user.id)  # type: ignore
                    await interaction.response.send_message(
                        embed=create_embed(
                            "🔧 Data Corruption Fixed",
                            "We found corrupted birthday data and cleaned it up. Please set your birthday again using `/bday set`.",
                            discord.Color.orange(),
                        ),
                        ephemeral=True,
                    )
                    return

                # Format the birthday string to be more readable
                # Defensive programming: ensure proper MM-DD format
                if "-" not in birthday_str:
                    msg = f"Birthday data not in expected MM-DD format: {birthday_str}"
                    raise ValueError(msg)

                parts = birthday_str.split("-")
                if len(parts) != 2:
                    msg = f"Birthday data malformed, expected 2 parts got {len(parts)}: {birthday_str}"
                    raise ValueError(msg)

                month, day = map(int, parts)
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
        """List all birthdays sorted by who's next."""
        try:
            # Get all birthdays from database
            all_birthdays = await self.bot.db_manager.get_all_birthdays()  # type: ignore

            if not all_birthdays:
                embed = create_embed(
                    "🎂 No Birthdays Set",
                    "No one has set their birthday yet! 🎈\n\nUse `/bday set` to add yours!",
                    discord.Color.blue(),
                )
                await interaction.response.send_message(embed=embed)
                return

            # Get current date
            from datetime import datetime
            now = datetime.now()

            # Parse and sort birthdays by days until next occurrence
            birthday_data = []
            for bday_row in all_birthdays:
                # bday_row = (id, user_id, birthday, timezone, announced_year, created_at)
                user_id = bday_row[1]
                birthday_str = str(bday_row[2])

                # Skip corrupted data
                if "-" not in birthday_str:
                    continue

                try:
                    month, day = map(int, birthday_str.split("-"))
                    
                    # Calculate days until next birthday
                    # Create datetime for this year's birthday
                    this_year_bday = datetime(now.year, month, day)
                    
                    # If birthday already passed this year, use next year
                    if this_year_bday.date() < now.date():
                        next_bday = datetime(now.year + 1, month, day)
                    else:
                        next_bday = this_year_bday
                    
                    days_until = (next_bday.date() - now.date()).days
                    
                    # Fetch user info
                    try:
                        user = await self.bot.fetch_user(user_id)
                        display_name = user.display_name if user else f"User {user_id}"
                    except:
                        display_name = f"User {user_id}"
                    
                    # Format date
                    month_names = [
                        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
                    ]
                    formatted_date = f"{month_names[month-1]} {day}"
                    
                    birthday_data.append({
                        "name": display_name,
                        "date": formatted_date,
                        "days_until": days_until,
                    })
                    
                except (ValueError, IndexError):
                    continue

            # Sort by days until birthday
            birthday_data.sort(key=lambda x: x["days_until"])

            # Build leaderboard-style list
            birthday_list = []
            for i, bday in enumerate(birthday_data[:25], 1):
                days = bday["days_until"]
                
                if days == 0:
                    status = "🎉 **TODAY!**"
                elif days == 1:
                    status = "Tomorrow"
                elif days <= 7:
                    status = f"In {days} days"
                else:
                    status = f"In {days} days"
                
                # Format: #1 • Name • Date • Status
                birthday_list.append(f"`#{i:2d}` • **{bday['name']}** • {bday['date']} • {status}")
            
            # Build embed with list
            description = "\n".join(birthday_list)
            
            embed = create_embed(
                "🎂 Upcoming Birthdays",
                description,
                discord.Color.magenta(),
            )

            if len(birthday_data) > 25:
                embed.set_footer(text=f"Showing first 25 of {len(birthday_data)} birthdays")
            else:
                embed.set_footer(text=f"Total: {len(birthday_data)} birthday{'s' if len(birthday_data) != 1 else ''} • Use /bday set to add yours!")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"Error listing birthdays: {e}")
            await interaction.response.send_message(
                embed=create_embed(
                    "❌ Error",
                    "There was an error retrieving birthdays. Please try again.",
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
