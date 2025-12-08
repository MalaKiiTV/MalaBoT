"""
Birthday system cog for MalaBoT.
Handles user birthday tracking and celebrations.
"""

from datetime import datetime, timedelta

import discord
import pytz
from discord import app_commands
from discord.ext import commands, tasks

from utils.helpers import create_embed
from utils.logger import get_logger


class BirthdayReminderView(discord.ui.View):
    """Persistent view for birthday reminder button"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Set Your Birthday", style=discord.ButtonStyle.primary, emoji="🎂", custom_id="birthday_reminder_button")
    async def set_birthday_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle birthday button click"""
        modal = BirthdayModal(interaction.client)
        await interaction.response.send_modal(modal)


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
                (2, 30),
                (2, 31),  # February (29 is valid for leap years)
                (4, 31),
                (6, 31),
                (9, 31),
                (11, 31),  # 30-day months
            ]
            if (month, day) in invalid_dates:
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
                # Remove Birthday Pending role if user has it
                
                guild_id = interaction.guild.id if interaction.guild else None
                if guild_id:
                    birthday_pending_role_id = await self.bot.db_manager.get_setting("birthday_pending_role", guild_id)
                    if birthday_pending_role_id:
                        birthday_pending_role = discord.utils.get(interaction.guild.roles, id=int(birthday_pending_role_id))
                        if birthday_pending_role and birthday_pending_role in interaction.user.roles:
                            try:
                                await interaction.user.remove_roles(birthday_pending_role, reason="Birthday set")
                                get_logger("birthdays").info(f"Removed Birthday Pending role from {interaction.user.name}")
                            except discord.Forbidden:
                                get_logger("birthdays").error(f"Missing permissions to remove Birthday Pending role from {interaction.user.name}")
                    
                # Award XP for setting birthday
                xp_earned = 0
                birthday_xp = await self.bot.db_manager.get_setting("birthday_set_xp", guild_id)
                if birthday_xp:
                    try:
                        xp_amount = int(birthday_xp)
                        # Use the proper add_xp method
                        new_xp, new_level = await self.bot.db_manager.add_xp(
                            interaction.user.id, guild_id, xp_amount
                        )
                        xp_earned = xp_amount
                        get_logger("birthdays").info(f"Awarded {xp_amount} XP to {interaction.user.name} for setting birthday (Total: {new_xp}, Level: {new_level})")
                    except (ValueError, TypeError) as e:
                        get_logger("birthdays").error(f"Invalid birthday_set_xp value: {birthday_xp}, error: {e}")
                    except Exception as e:
                        get_logger("birthdays").error(f"Error awarding XP for birthday: {e}")

                # Create success message with XP info if applicable
                success_description = f"Your birthday has been set to {birthday_str}. You'll receive a special message on your birthday!"
                if xp_earned > 0:
                    success_description += f"\n\nYou earned **{xp_earned} XP** for setting your birthday!"
                
                await interaction.response.send_message(
                    embed=create_embed(
                        "🎂 Birthday Set!",
                        success_description,
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
        except Exception as e:
            get_logger("birthdays").error(f"Unexpected error in birthday modal: {e}", exc_info=True)
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
        self.db = bot.db_manager  # type: ignore
            @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Clean up user data when they leave the server."""
        try:
            # Remove birthday data
            await self.bot.db_manager.remove_user_birthday(member.id)
            self.logger.info(f"Removed birthday data for {member.name} ({member.id}) who left guild {member.guild.id}")
            
            # Remove XP data for this guild
            async with self.bot.pool.acquire() as conn:
                await conn.execute(
                    "DELETE FROM user_xp WHERE user_id = $1 AND guild_id = $2",
                    member.id,
                    member.guild.id
                )
            self.logger.info(f"Removed XP data for {member.name} ({member.id}) in guild {member.guild.id}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up data for user {member.id} leaving guild {member.guild.id}: {e}")


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
                
                # Validate month range before indexing
                if not (1 <= month <= 12):
                    self.logger.error(f"Invalid month {month} for user {interaction.user.id}")
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
                    except (discord.NotFound, discord.HTTPException):
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

    async def _remove_birthday(self, interaction: discord.Interaction):
        """Remove your birthday."""
        try:
            success = await self.bot.db_manager.remove_user_birthday(interaction.user.id)  # type: ignore
            
            if success:
                await interaction.response.send_message(
                    embed=create_embed(
                        "✅ Birthday Removed",
                        "Your birthday has been removed from the system.",
                        discord.Color.green(),
                    ),
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    embed=create_embed(
                        "❌ No Birthday Set",
                        "You don't have a birthday set.",
                        discord.Color.red(),
                    ),
                    ephemeral=True,
                )
        except Exception as e:
            self.logger.error(f"Error removing birthday for user {interaction.user.id}: {e}")
            await interaction.response.send_message(
                embed=create_embed(
                    "❌ Error",
                    "There was an error removing your birthday. Please try again.",
                    discord.Color.red(),
                ),
                ephemeral=True,
            )

    # Daily birthday check task


    @tasks.loop(hours=24)
    async def check_birthdays(self):
        """Check for today's birthdays and send celebration messages."""
        try:
            # Check each guild's birthday settings
            for guild in self.bot.guilds:
                guild_id = guild.id
                
                # Check if birthday announcements are enabled
                announcements_enabled = await self.bot.db_manager.get_setting("birthday_announcements_enabled", guild_id)
                
                # Skip if disabled (default to enabled if not set)
                if announcements_enabled == "false":
                    continue
                
                # Get birthday settings
                birthday_channel_id = await self.bot.db_manager.get_setting("birthday_channel", guild_id)
                birthday_time = await self.bot.db_manager.get_setting("birthday_time", guild_id)
                birthday_message = await self.bot.db_manager.get_setting("birthday_message", guild_id)
                timezone_str = await self.bot.db_manager.get_setting("timezone", guild_id)
                
                if not birthday_channel_id:
                    continue
                
                # Get birthday channel
                channel = guild.get_channel(int(birthday_channel_id))
                if not channel:
                    self.logger.warning(f"Birthday channel {birthday_channel_id} not found in guild {guild_id}")
                    continue
                
                # Get current time in the guild's timezone
                try:
                    if timezone_str:
                        tz = pytz.timezone(timezone_str)
                    else:
                        tz = pytz.UTC
                    now = datetime.now(tz)
                except Exception as e:
                    self.logger.error(f"Invalid timezone {timezone_str} for guild {guild_id}: {e}")
                    now = datetime.now(pytz.UTC)
                
                # Get today's unannounced birthdays (in the guild's timezone)
                today_birthdays = await self.bot.db_manager.get_unannounced_birthdays(now.year)
                
                if not today_birthdays:
                    continue
                
                for user_data in today_birthdays:
                    user_id = user_data[0]
                    
                    try:
                        # Get member from guild
                        member = guild.get_member(user_id)
                        if not member:
                            continue
                        
                        # Format message
                        message = birthday_message or "🎂 Happy Birthday {member}! Have a great day!"
                        message = message.replace("{member}", member.mention)
                        
                        # Send birthday message
                        embed = create_embed(
                            "🎉 Happy Birthday! 🎂",
                            message,
                            discord.Color.magenta(),
                        )
                        embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else None)
                        
                        await channel.send(embed=embed)
                        
                        # Mark as announced for this year
                        await self.bot.db_manager.mark_birthday_announced(user_id, now.year)
                        
                        self.logger.info(f"Sent birthday message for user {user_id} in guild {guild_id} at {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                        
                    except Exception as e:
                        self.logger.error(f"Error processing birthday for user {user_id}: {e}")
                
        except Exception as e:
            self.logger.error(f"Error in birthday check: {e}")

    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        """Wait until bot is ready and schedule for configured time."""
        await self.bot.wait_until_ready()
        
        # Get the first guild's birthday time and timezone settings (or use defaults)
        birthday_time = "09:00"
        timezone_str = "UTC"
        
        if self.bot.guilds:
            guild_id = self.bot.guilds[0].id
            stored_time = await self.bot.db_manager.get_setting("birthday_time", guild_id)
            stored_timezone = await self.bot.db_manager.get_setting("timezone", guild_id)
            
            if stored_time:
                birthday_time = stored_time
            if stored_timezone:
                timezone_str = stored_timezone
        
        # Parse the time
        try:
            hour, minute = map(int, birthday_time.split(":"))
        except ValueError:
            self.logger.error(f"Invalid birthday time format: {birthday_time}, using 09:00")
            hour, minute = 9, 0
        
        # Get timezone
        try:
            tz = pytz.timezone(timezone_str)
        except Exception as e:
            self.logger.error(f"Invalid timezone {timezone_str}: {e}, using UTC")
            tz = pytz.UTC
        
        # Calculate next occurrence of that time in the guild's timezone
        now = datetime.now(tz)
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If target time already passed today, schedule for tomorrow
        if target_time <= now:
            target_time += timedelta(days=1)
        
        self.logger.info(f"Birthday check scheduled for {target_time.strftime('%Y-%m-%d %H:%M:%S %Z')} (timezone: {timezone_str})")
        
        # Sleep until target time
        await discord.utils.sleep_until(target_time)

    async def cog_load(self):
        """Start the birthday check task when cog loads."""
        self.check_birthdays.start()
        # Register persistent view for birthday reminders
        self.bot.add_view(BirthdayReminderView())

    async def cog_unload(self):
        """Stop the birthday check task when cog unloads."""
        self.check_birthdays.cancel()
    
    async def setup_birthday_reminder_message(self, guild_id: int, channel: discord.TextChannel):
        """Setup persistent birthday reminder message in channel"""
        try:
            # Create embed
            embed = discord.Embed(
                title="🎂 Set Your Birthday!",
                description=(
                    "Click the button below to set your birthday!\n\n"
                    "**Why set your birthday?**\n"
                    "• Get a special birthday announcement\n"
                    "• Receive birthday wishes from the community\n"
                    "• Unlock full server access\n\n"
                    "**Privacy:** Only the month and day are stored, not your birth year."
                ),
                color=discord.Color.gold(),
            )
            embed.set_footer(text="Your birthday will be celebrated on your special day!")
            
            # Send message with persistent view
            view = BirthdayReminderView()
            message = await channel.send(embed=embed, view=view)
            
            # Store message ID
            await self.bot.db_manager.set_setting("birthday_reminder_message_id", str(message.id), guild_id)
            
            self.logger.info(f"Birthday reminder message setup in channel {channel.id} for guild {guild_id}")
            
        except Exception as e:
            self.logger.error(f"Error setting up birthday reminder message: {e}")
            raise

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Handle member leaves - delete birthday data."""
        try:
            if not self.bot.db_manager:
                return
            
            # Delete birthday data for user who left
            await self.bot.db_manager.execute_query(
                "DELETE FROM birthdays WHERE user_id = ?",
                (member.id,)
            )
            
            self.logger.info(f"Deleted birthday data for user {member.name} ({member.id}) who left {member.guild.name}")
            
        except Exception as e:
            self.logger.error(f"Error deleting birthday data for member {member.name}: {e}")


async def setup(bot: commands.Bot):
    """Setup function for the birthdays cog."""
    await bot.add_cog(Birthdays(bot))
