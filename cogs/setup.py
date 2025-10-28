"""
Setup Cog for MalaBoT
Unified configuration system for all bot features
Command: /setup
"""

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View, Modal, TextInput, Button
from typing import Optional

from utils.helpers import create_embed, safe_send_message
from utils.logger import log_system
from config.constants import COLORS


class VerificationSetupView(View):
    def __init__(self, db_manager, guild_id: int):
        super().__init__(timeout=300)
        self.db = db_manager
        self.guild_id = guild_id

    @discord.ui.button(label="Set Review Channel", style=discord.ButtonStyle.primary, emoji="📋")
    async def set_channel(self, interaction: discord.Interaction, button: Button):
        """Set the review channel"""
        modal = ReviewChannelModal(self.db, self.guild_id)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Set Verified Role", style=discord.ButtonStyle.success, emoji="✅")
    async def set_role(self, interaction: discord.Interaction, button: Button):
        """Set the verified role"""
        modal = VerifiedRoleModal(self.db, self.guild_id)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="View Current Config", style=discord.ButtonStyle.secondary, emoji="👁️")
    async def view_config(self, interaction: discord.Interaction, button: Button):
        """View current verification configuration"""
        verify_channel_id = await self.db.get_setting(f"verify_channel_{self.guild_id}")
        verify_role_id = await self.db.get_setting(f"verify_role_{self.guild_id}")

        config_text = ""
        if verify_channel_id:
            config_text += f"**Review Channel:** <#{verify_channel_id}>\n"
        else:
            config_text += "**Review Channel:** Not configured\n"

        if verify_role_id:
            config_text += f"**Verified Role:** <@&{verify_role_id}>\n"
        else:
            config_text += "**Verified Role:** Not configured\n"

        embed = discord.Embed(
            title="Current Verification Configuration",
            description=config_text,
            color=COLORS["info"],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class ReviewChannelModal(Modal, title="Set Review Channel"):
    channel_id = TextInput(
        label="Channel ID",
        placeholder="Right-click channel → Copy Channel ID",
        required=True,
        max_length=20,
    )

    def __init__(self, db_manager, guild_id: int):
        super().__init__()
        self.db = db_manager
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            channel_id = int(self.channel_id.value)
            channel = interaction.guild.get_channel(channel_id)
            
            if not channel:
                await interaction.response.send_message(
                    embed=create_embed(
                        "Error",
                        "Channel not found. Make sure you copied the correct Channel ID.",
                        COLORS["error"],
                    ),
                    ephemeral=True,
                )
                return

            await self.db.set_setting(f"verify_channel_{self.guild_id}", channel_id)
            await self.db.log_event(
                category="VERIFY",
                action="SETUP_CHANNEL",
                user_id=interaction.user.id,
                details=f"Set review channel to #{channel.name}",
                guild_id=self.guild_id,
            )

            await interaction.response.send_message(
                embed=create_embed(
                    "Review Channel Set",
                    f"✅ Verification submissions will be posted to {channel.mention}",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except ValueError:
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Invalid Channel ID. Please enter numbers only.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting review channel: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set review channel. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class VerifiedRoleModal(Modal, title="Set Verified Role"):
    role_id = TextInput(
        label="Role ID",
        placeholder="Right-click role → Copy Role ID",
        required=True,
        max_length=20,
    )

    def __init__(self, db_manager, guild_id: int):
        super().__init__()
        self.db = db_manager
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            role_id = int(self.role_id.value)
            role = interaction.guild.get_role(role_id)
            
            if not role:
                await interaction.response.send_message(
                    embed=create_embed(
                        "Error",
                        "Role not found. Make sure you copied the correct Role ID.",
                        COLORS["error"],
                    ),
                    ephemeral=True,
                )
                return

            await self.db.set_setting(f"verify_role_{self.guild_id}", role_id)
            await self.db.log_event(
                category="VERIFY",
                action="CONFIG_ROLE",
                user_id=interaction.user.id,
                details=f"Set verified role to {role.name}",
                guild_id=self.guild_id,
            )

            await interaction.response.send_message(
                embed=create_embed(
                    "Verified Role Set",
                    f"✅ Users will receive {role.mention} when verified",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except ValueError:
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Invalid Role ID. Please enter numbers only.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting verified role: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set verified role. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class SetupSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Verification System",
                value="verification",
                description="Configure verification channels and roles",
                emoji="✅"
            ),
            discord.SelectOption(
                label="Welcome System",
                value="welcome",
                description="Configure welcome messages and channel",
                emoji="👋"
            ),
            discord.SelectOption(
                label="Birthday System",
                value="birthday",
                description="Configure birthday announcements",
                emoji="🎂"
            ),
            discord.SelectOption(
                label="XP System",
                value="xp",
                description="Configure XP and leveling settings",
                emoji="🏆"
            ),
            discord.SelectOption(
                label="General Settings",
                value="general",
                description="Configure timezone, logging, etc.",
                emoji="⚙️"
            ),
            discord.SelectOption(
                label="View Current Config",
                value="view",
                description="View all current bot settings",
                emoji="📋"
            ),
        ]
        super().__init__(
            placeholder="Select a system to configure...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        
        if selection == "verification":
            await self.setup_verification(interaction)
        elif selection == "welcome":
            await self.setup_welcome(interaction)
        elif selection == "birthday":
            await self.setup_birthday(interaction)
        elif selection == "xp":
            await self.setup_xp(interaction)
        elif selection == "general":
            await self.setup_general(interaction)
        elif selection == "view":
            await self.view_config(interaction)

    async def setup_verification(self, interaction: discord.Interaction):
        """Setup verification system with interactive configuration"""
        view = VerificationSetupView(interaction.client.db_manager, interaction.guild.id)
        
        embed = discord.Embed(
            title="✅ Verification System Setup",
            description=(
                "Configure your verification system using the buttons below:\n\n"
                "**Required Settings:**\n"
                "• Review Channel - Where staff sees verification submissions\n"
                "• Verified Role - Role assigned when user is verified\n\n"
                "**User Workflow:**\n"
                "1. User runs `/verify submit`\n"
                "2. Enters Activision ID in modal\n"
                "3. Uploads screenshot\n"
                "4. Selects platform from dropdown\n"
                "5. Staff reviews with `/verify review @user verified/cheater/unverified`\n\n"
                "**Review Decisions:**\n"
                "• Verified - Assigns verified role\n"
                "• Cheater - Bans user from server\n"
                "• Unverified - Leaves user unverified"
            ),
            color=COLORS["info"],
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def setup_welcome(self, interaction: discord.Interaction):
        """Setup welcome system"""
        embed = discord.Embed(
            title="👋 Welcome System Setup",
            description=(
                "Configure your welcome system:\n\n"
                "**Commands to use:**\n"
                "`/welcome setchannel #channel` - Set welcome channel\n"
                "`/welcome setmessage <message>` - Set welcome message\n"
                "`/welcome settitle <title>` - Set welcome title\n"
                "`/welcome setimage <url>` - Set welcome image\n"
                "`/welcome toggle` - Enable/disable welcome messages\n\n"
                "**Variables you can use:**\n"
                "`{member}` - Mentions the new member\n"
                "`{member.name}` - Member's username\n"
                "`{server}` - Server name\n"
                "`{member.count}` - Total member count"
            ),
            color=COLORS["welcome"],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def setup_birthday(self, interaction: discord.Interaction):
        """Setup birthday system"""
        embed = discord.Embed(
            title="🎂 Birthday System Setup",
            description=(
                "Configure your birthday system:\n\n"
                "**Commands to use:**\n"
                "`/bday setchannel #channel` - Set birthday announcement channel\n"
                "`/bday setposttime <time>` - Set announcement time (e.g., 08:00 AM)\n"
                "`/settimezone <timezone>` - Set server timezone (e.g., UTC-6)\n\n"
                "**User Commands:**\n"
                "`/bday set <MM-DD>` - Users set their birthday\n"
                "`/bday view [@user]` - View birthday\n"
                "`/bday list` - View all birthdays\n"
                "`/bday next` - See next upcoming birthday"
            ),
            color=COLORS["birthday"],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def setup_xp(self, interaction: discord.Interaction):
        """Setup XP system"""
        embed = discord.Embed(
            title="🏆 XP System Setup",
            description=(
                "Configure your XP system:\n\n"
                "**Admin Commands:**\n"
                "`/xpadmin add @user <amount>` - Add XP to user\n"
                "`/xpadmin remove @user <amount>` - Remove XP from user\n"
                "`/xpadmin set @user <amount>` - Set user's XP\n"
                "`/xpadmin reset @user` - Reset user's XP\n\n"
                "**User Commands:**\n"
                "`/xp rank [@user]` - View XP rank\n"
                "`/xp leaderboard` - View server leaderboard\n"
                "`/xp daily` - Claim daily XP bonus\n\n"
                "**XP Settings:**\n"
                "• Users gain 5-15 XP per message\n"
                "• 60 second cooldown between XP gains\n"
                "• Daily check-in: 50 XP + streak bonus"
            ),
            color=COLORS["xp"],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def setup_general(self, interaction: discord.Interaction):
        """Setup general settings"""
        embed = discord.Embed(
            title="⚙️ General Settings Setup",
            description=(
                "Configure general bot settings:\n\n"
                "**Commands to use:**\n"
                "`/settimezone <timezone>` - Set server timezone (e.g., UTC-6, America/New_York)\n\n"
                "**Available Timezones:**\n"
                "• UTC-12 to UTC+14\n"
                "• America/New_York (EST)\n"
                "• America/Chicago (CST)\n"
                "• America/Denver (MST)\n"
                "• America/Los_Angeles (PST)\n"
                "• Europe/London (GMT)\n"
                "• And many more...\n\n"
                "**Note:** Timezone affects birthday announcements and scheduled tasks."
            ),
            color=COLORS["primary"],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def view_config(self, interaction: discord.Interaction):
        """View current configuration"""
        bot = interaction.client
        db = bot.db_manager
        guild_id = interaction.guild.id

        # Fetch all settings
        verify_channel_id = await db.get_setting(f"verify_channel_{guild_id}")
        verify_role_id = await db.get_setting(f"verify_role_{guild_id}")
        unverified_role_id = await db.get_setting(f"unverified_role_{guild_id}")
        welcome_channel_id = await db.get_setting(f"welcome_channel_{guild_id}")
        birthday_channel_id = await db.get_setting(f"birthday_channel_{guild_id}")
        timezone = await db.get_setting(f"timezone_{guild_id}", "UTC-6")

        embed = discord.Embed(
            title="📋 Current Bot Configuration",
            description=f"Configuration for **{interaction.guild.name}**",
            color=COLORS["info"],
        )

        # Verification settings
        verify_text = ""
        if verify_channel_id:
            verify_text += f"Review Channel: <#{verify_channel_id}>\n"
        if verify_role_id:
            verify_text += f"Verified Role: <@&{verify_role_id}>\n"
        if unverified_role_id:
            verify_text += f"Unverified Role: <@&{unverified_role_id}>\n"
        if not verify_text:
            verify_text = "Not configured"
        embed.add_field(name="✅ Verification", value=verify_text, inline=False)

        # Welcome settings
        welcome_text = ""
        if welcome_channel_id:
            welcome_text += f"Channel: <#{welcome_channel_id}>\n"
        else:
            welcome_text = "Not configured"
        embed.add_field(name="👋 Welcome", value=welcome_text, inline=False)

        # Birthday settings
        birthday_text = ""
        if birthday_channel_id:
            birthday_text += f"Channel: <#{birthday_channel_id}>\n"
        else:
            birthday_text = "Not configured"
        embed.add_field(name="🎂 Birthday", value=birthday_text, inline=False)

        # General settings
        general_text = f"Timezone: {timezone}"
        embed.add_field(name="⚙️ General", value=general_text, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


class SetupView(View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(SetupSelect())


class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db_manager

    @app_commands.command(name="setup", description="Configure bot settings (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        """Main setup command with interactive menu"""
        embed = discord.Embed(
            title="🤖 MalaBoT Setup",
            description=(
                "Welcome to the MalaBoT configuration system!\n\n"
                "Select a system below to configure it. Each system has its own set of commands and settings.\n\n"
                "**Available Systems:**\n"
                "✅ Verification - User verification system\n"
                "👋 Welcome - Welcome messages for new members\n"
                "🎂 Birthday - Birthday announcements\n"
                "🏆 XP - Experience and leveling system\n"
                "⚙️ General - Timezone and other settings\n"
                "📋 View Config - See current configuration"
            ),
            color=COLORS["primary"],
        )
        embed.set_footer(text="Select an option from the dropdown below")

        view = SetupView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))