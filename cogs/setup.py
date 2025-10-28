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


# ============================================================
# COMMON TIMEZONE OPTIONS
# ============================================================

TIMEZONE_OPTIONS = [
    discord.SelectOption(label="UTC-12 (Baker Island)", value="UTC-12"),
    discord.SelectOption(label="UTC-11 (American Samoa)", value="UTC-11"),
    discord.SelectOption(label="UTC-10 (Hawaii)", value="UTC-10"),
    discord.SelectOption(label="UTC-9 (Alaska)", value="UTC-9"),
    discord.SelectOption(label="UTC-8 (Pacific Time)", value="UTC-8"),
    discord.SelectOption(label="UTC-7 (Mountain Time)", value="UTC-7"),
    discord.SelectOption(label="UTC-6 (Central Time)", value="UTC-6"),
    discord.SelectOption(label="UTC-5 (Eastern Time)", value="UTC-5"),
    discord.SelectOption(label="UTC-4 (Atlantic Time)", value="UTC-4"),
    discord.SelectOption(label="UTC-3 (Brazil)", value="UTC-3"),
    discord.SelectOption(label="UTC-2 (Mid-Atlantic)", value="UTC-2"),
    discord.SelectOption(label="UTC-1 (Azores)", value="UTC-1"),
    discord.SelectOption(label="UTC+0 (London/GMT)", value="UTC+0"),
    discord.SelectOption(label="UTC+1 (Paris/Berlin)", value="UTC+1"),
    discord.SelectOption(label="UTC+2 (Cairo/Athens)", value="UTC+2"),
    discord.SelectOption(label="UTC+3 (Moscow)", value="UTC+3"),
    discord.SelectOption(label="UTC+4 (Dubai)", value="UTC+4"),
    discord.SelectOption(label="UTC+5 (Pakistan)", value="UTC+5"),
    discord.SelectOption(label="UTC+6 (Bangladesh)", value="UTC+6"),
    discord.SelectOption(label="UTC+7 (Bangkok)", value="UTC+7"),
    discord.SelectOption(label="UTC+8 (Singapore/Beijing)", value="UTC+8"),
    discord.SelectOption(label="UTC+9 (Tokyo/Seoul)", value="UTC+9"),
    discord.SelectOption(label="UTC+10 (Sydney)", value="UTC+10"),
    discord.SelectOption(label="UTC+11 (Solomon Islands)", value="UTC+11"),
    discord.SelectOption(label="UTC+12 (New Zealand)", value="UTC+12"),
]


# ============================================================
# VERIFICATION SYSTEM COMPONENTS
# ============================================================

class VerifyChannelSelect(discord.ui.ChannelSelect):
    """Channel selector for verification review channel"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(
            placeholder="Select review channel...",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.text]
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        channel = self.values[0]
        try:
            await self.db.set_setting(f"verify_channel_{self.guild_id}", channel.id)
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


class VerifiedRoleSelect(discord.ui.RoleSelect):
    """Role selector for verified role"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(
            placeholder="Select verified role...",
            min_values=1,
            max_values=1
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]
        try:
            await self.db.set_setting(f"verify_role_{self.guild_id}", role.id)
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


class StaffRoleSelect(discord.ui.RoleSelect):
    """Role selector for staff role (who can review verifications)"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(
            placeholder="Select staff role...",
            min_values=1,
            max_values=1
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]
        try:
            await self.db.set_setting(f"staff_role_{self.guild_id}", role.id)
            await self.db.log_event(
                category="VERIFY",
                action="CONFIG_STAFF_ROLE",
                user_id=interaction.user.id,
                details=f"Set staff role to {role.name}",
                guild_id=self.guild_id,
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "Staff Role Set",
                    f"✅ Only users with {role.mention} can review verifications",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting staff role: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set staff role. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class CheaterRoleSelect(discord.ui.RoleSelect):
    """Role selector for cheater role"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(
            placeholder="Select cheater role...",
            min_values=1,
            max_values=1
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]
        try:
            await self.db.set_setting(f"cheater_role_{self.guild_id}", role.id)
            await self.db.log_event(
                category="VERIFY",
                action="CONFIG_CHEATER_ROLE",
                user_id=interaction.user.id,
                details=f"Set cheater role to {role.name}",
                guild_id=self.guild_id,
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "Cheater Role Set",
                    f"✅ Cheaters will be assigned {role.mention} and isolated",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting cheater role: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set cheater role. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class CheaterChannelSelect(discord.ui.ChannelSelect):
    """Channel selector for cheater jail channel"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(
            placeholder="Select cheater jail channel...",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.text]
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        channel = self.values[0]
        try:
            await self.db.set_setting(f"cheater_channel_{self.guild_id}", channel.id)
            await self.db.log_event(
                category="VERIFY",
                action="SETUP_CHEATER_CHANNEL",
                user_id=interaction.user.id,
                details=f"Set cheater jail to #{channel.name}",
                guild_id=self.guild_id,
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "Cheater Jail Set",
                    f"✅ Cheaters will be sent to {channel.mention}",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting cheater jail: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set cheater jail. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class VerificationSetupView(View):
    """View for verification system setup"""
    def __init__(self, db_manager, guild: discord.Guild):
        super().__init__(timeout=300)
        self.db = db_manager
        self.guild = guild
        
        # Add all selectors
        self.add_item(VerifyChannelSelect(db_manager, guild.id))
        self.add_item(VerifiedRoleSelect(db_manager, guild.id))
        self.add_item(StaffRoleSelect(db_manager, guild.id))
        self.add_item(CheaterRoleSelect(db_manager, guild.id))
        self.add_item(CheaterChannelSelect(db_manager, guild.id))


# ============================================================
# BIRTHDAY SYSTEM COMPONENTS
# ============================================================

class BirthdayRoleSelect(discord.ui.RoleSelect):
    """Role selector for birthday role"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(
            placeholder="Select birthday role...",
            min_values=1,
            max_values=1
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]
        try:
            await self.db.set_setting(f"birthday_role_{self.guild_id}", role.id)
            await self.db.log_event(
                category="BIRTHDAY",
                action="CONFIG_ROLE",
                user_id=interaction.user.id,
                details=f"Set birthday role to {role.name}",
                guild_id=self.guild_id,
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "Birthday Role Set",
                    f"✅ Users will receive {role.mention} on their birthday",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting birthday role: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set birthday role. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class BirthdayChannelSelect(discord.ui.ChannelSelect):
    """Channel selector for birthday announcements"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(
            placeholder="Select birthday announcement channel...",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.text]
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        channel = self.values[0]
        try:
            await self.db.set_setting(f"birthday_channel_{self.guild_id}", channel.id)
            await self.db.log_event(
                category="BIRTHDAY",
                action="SETUP_CHANNEL",
                user_id=interaction.user.id,
                details=f"Set birthday channel to #{channel.name}",
                guild_id=self.guild_id,
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "Birthday Channel Set",
                    f"✅ Birthday announcements will be posted to {channel.mention}",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting birthday channel: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set birthday channel. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class BirthdayTimeSelect(Select):
    """Time selector for birthday announcements"""
    def __init__(self, db_manager, guild_id: int):
        options = [
            discord.SelectOption(label="12:00 AM (Midnight)", value="00:00"),
            discord.SelectOption(label="1:00 AM", value="01:00"),
            discord.SelectOption(label="2:00 AM", value="02:00"),
            discord.SelectOption(label="3:00 AM", value="03:00"),
            discord.SelectOption(label="4:00 AM", value="04:00"),
            discord.SelectOption(label="5:00 AM", value="05:00"),
            discord.SelectOption(label="6:00 AM", value="06:00"),
            discord.SelectOption(label="7:00 AM", value="07:00"),
            discord.SelectOption(label="8:00 AM", value="08:00"),
            discord.SelectOption(label="9:00 AM", value="09:00"),
            discord.SelectOption(label="10:00 AM", value="10:00"),
            discord.SelectOption(label="11:00 AM", value="11:00"),
            discord.SelectOption(label="12:00 PM (Noon)", value="12:00"),
            discord.SelectOption(label="1:00 PM", value="13:00"),
            discord.SelectOption(label="2:00 PM", value="14:00"),
            discord.SelectOption(label="3:00 PM", value="15:00"),
            discord.SelectOption(label="4:00 PM", value="16:00"),
            discord.SelectOption(label="5:00 PM", value="17:00"),
            discord.SelectOption(label="6:00 PM", value="18:00"),
            discord.SelectOption(label="7:00 PM", value="19:00"),
            discord.SelectOption(label="8:00 PM", value="20:00"),
            discord.SelectOption(label="9:00 PM", value="21:00"),
            discord.SelectOption(label="10:00 PM", value="22:00"),
            discord.SelectOption(label="11:00 PM", value="23:00"),
        ]
        super().__init__(
            placeholder="Select announcement time...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        time = self.values[0]
        try:
            await self.db.set_setting(f"birthday_time_{self.guild_id}", time)
            await self.db.log_event(
                category="BIRTHDAY",
                action="SET_TIME",
                user_id=interaction.user.id,
                details=f"Set birthday announcement time to {time}",
                guild_id=self.guild_id,
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "Birthday Time Set",
                    f"✅ Birthday announcements will be posted at **{time}** (server timezone)",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting birthday time: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set birthday time. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class BirthdaySetupView(View):
    """View for birthday system setup"""
    def __init__(self, db_manager, guild: discord.Guild):
        super().__init__(timeout=300)
        self.db = db_manager
        self.guild = guild
        
        # Add all selectors
        self.add_item(BirthdayChannelSelect(db_manager, guild.id))
        self.add_item(BirthdayRoleSelect(db_manager, guild.id))
        self.add_item(BirthdayTimeSelect(db_manager, guild.id))


# ============================================================
# XP SYSTEM COMPONENTS
# ============================================================

class XPAmountModal(Modal, title="Configure XP Amounts"):
    """Modal for setting XP amounts"""
    message_xp = TextInput(
        label="XP per Message",
        placeholder="e.g., 10",
        required=True,
        max_length=5,
        default="10"
    )
    
    voice_xp = TextInput(
        label="XP per Minute in Voice",
        placeholder="e.g., 5",
        required=True,
        max_length=5,
        default="5"
    )
    
    reaction_xp = TextInput(
        label="XP per Reaction Received",
        placeholder="e.g., 2",
        required=True,
        max_length=5,
        default="2"
    )
    
    command_xp = TextInput(
        label="XP per Command Used",
        placeholder="e.g., 3",
        required=True,
        max_length=5,
        default="3"
    )
    
    daily_bonus = TextInput(
        label="Daily Bonus XP",
        placeholder="e.g., 50",
        required=True,
        max_length=5,
        default="50"
    )

    def __init__(self, db_manager, guild_id: int):
        super().__init__()
        self.db = db_manager
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Validate inputs are numbers
            message_xp = int(self.message_xp.value)
            voice_xp = int(self.voice_xp.value)
            reaction_xp = int(self.reaction_xp.value)
            command_xp = int(self.command_xp.value)
            daily_bonus = int(self.daily_bonus.value)
            
            # Store settings
            await self.db.set_setting(f"xp_message_{self.guild_id}", message_xp)
            await self.db.set_setting(f"xp_voice_{self.guild_id}", voice_xp)
            await self.db.set_setting(f"xp_reaction_{self.guild_id}", reaction_xp)
            await self.db.set_setting(f"xp_command_{self.guild_id}", command_xp)
            await self.db.set_setting(f"xp_daily_{self.guild_id}", daily_bonus)
            
            await self.db.log_event(
                category="XP",
                action="CONFIG_AMOUNTS",
                user_id=interaction.user.id,
                details=f"Set XP amounts: msg={message_xp}, voice={voice_xp}, reaction={reaction_xp}, cmd={command_xp}, daily={daily_bonus}",
                guild_id=self.guild_id,
            )
            
            await interaction.response.send_message(
                embed=create_embed(
                    "XP Amounts Configured",
                    f"✅ XP amounts set:\n"
                    f"• Messages: **{message_xp} XP**\n"
                    f"• Voice (per minute): **{voice_xp} XP**\n"
                    f"• Reactions: **{reaction_xp} XP**\n"
                    f"• Commands: **{command_xp} XP**\n"
                    f"• Daily Bonus: **{daily_bonus} XP**",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except ValueError:
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "All XP amounts must be valid numbers. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting XP amounts: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set XP amounts. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class XPSetupView(View):
    """View for XP system setup"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(timeout=300)
        self.db = db_manager
        self.guild_id = guild_id

    @discord.ui.button(label="Configure XP Amounts", style=discord.ButtonStyle.primary, emoji="⚙️")
    async def configure_xp(self, interaction: discord.Interaction, button: Button):
        """Configure XP amounts"""
        modal = XPAmountModal(self.db, self.guild_id)
        await interaction.response.send_modal(modal)


# ============================================================
# GENERAL SETTINGS COMPONENTS
# ============================================================

class TimezoneSelect(Select):
    """Timezone selector dropdown"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(
            placeholder="Select your timezone...",
            min_values=1,
            max_values=1,
            options=TIMEZONE_OPTIONS
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        timezone = self.values[0]
        try:
            await self.db.set_setting(f"timezone_{self.guild_id}", timezone)
            await self.db.log_event(
                category="SETTINGS",
                action="SET_TIMEZONE",
                user_id=interaction.user.id,
                details=f"Set timezone to {timezone}",
                guild_id=self.guild_id,
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "Timezone Set",
                    f"✅ Server timezone set to **{timezone}**\n\nThis affects birthday announcements and scheduled tasks.",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting timezone: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set timezone. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class OnlineMessageChannelSelect(discord.ui.ChannelSelect):
    """Channel selector for online message"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(
            placeholder="Select channel for online message...",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.text]
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        channel = self.values[0]
        try:
            await self.db.set_setting(f"online_channel_{self.guild_id}", channel.id)
            await self.db.log_event(
                category="SETTINGS",
                action="SET_ONLINE_CHANNEL",
                user_id=interaction.user.id,
                details=f"Set online message channel to #{channel.name}",
                guild_id=self.guild_id,
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "Online Message Channel Set",
                    f"✅ Bot online messages will be posted to {channel.mention}\n\nNow set the message text using the button below.",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting online channel: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set online channel. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class OnlineMessageModal(Modal, title="Set Bot Online Message"):
    """Modal for setting bot online message"""
    message = TextInput(
        label="Online Message",
        placeholder="Message to send when bot comes online",
        required=True,
        max_length=200,
        style=discord.TextStyle.paragraph
    )

    def __init__(self, db_manager, guild_id: int):
        super().__init__()
        self.db = db_manager
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await self.db.set_setting(f"online_message_{self.guild_id}", self.message.value)
            await self.db.log_event(
                category="SETTINGS",
                action="SET_ONLINE_MESSAGE",
                user_id=interaction.user.id,
                details=f"Set online message",
                guild_id=self.guild_id,
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "Online Message Set",
                    f"✅ Bot online message set to:\n\n{self.message.value}",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting online message: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set online message. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class GeneralSettingsView(View):
    """View for general settings"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(timeout=300)
        self.db = db_manager
        self.guild_id = guild_id
        
        # Add timezone selector
        self.add_item(TimezoneSelect(db_manager, guild_id))
        # Add online message channel selector
        self.add_item(OnlineMessageChannelSelect(db_manager, guild_id))

    @discord.ui.button(label="Set Online Message Text", style=discord.ButtonStyle.primary, emoji="💬")
    async def set_online_message(self, interaction: discord.Interaction, button: Button):
        """Set bot online message text"""
        modal = OnlineMessageModal(self.db, self.guild_id)
        await interaction.response.send_modal(modal)


# ============================================================
# MAIN SETUP SELECT MENU
# ============================================================

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
                description="Configure timezone, online message, etc.",
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
        view = VerificationSetupView(interaction.client.db_manager, interaction.guild)
        
        embed = discord.Embed(
            title="✅ Verification System Setup",
            description=(
                "Configure your verification system using the dropdowns below:\n\n"
                "**Required Settings:**\n"
                "• Review Channel - Where staff sees verification submissions\n"
                "• Verified Role - Role assigned when user is verified\n"
                "• Staff Role - Who can review verifications\n"
                "• Cheater Role - Role assigned to cheaters\n"
                "• Cheater Jail - Channel where cheaters are isolated\n\n"
                "**User Workflow:**\n"
                "1. User runs `/verify submit`\n"
                "2. Enters Activision ID in modal\n"
                "3. Uploads screenshot\n"
                "4. Selects platform from dropdown\n"
                "5. Staff reviews with `/verify review @user verified/cheater/unverified`\n\n"
                "**Review Decisions:**\n"
                "• Verified - Assigns verified role\n"
                "• Cheater - Assigns cheater role and isolates to jail\n"
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
        """Setup birthday system with interactive configuration"""
        view = BirthdaySetupView(interaction.client.db_manager, interaction.guild)
        
        embed = discord.Embed(
            title="🎂 Birthday System Setup",
            description=(
                "Configure your birthday system using the dropdowns below:\n\n"
                "**Required Settings:**\n"
                "• Birthday Channel - Where announcements are posted\n"
                "• Birthday Role - Role given on user's birthday\n"
                "• Announcement Time - What time to post announcements\n\n"
                "**Note:** Timezone must be configured in General Settings first!\n\n"
                "**User Commands:**\n"
                "`/bday set <MM-DD>` - Users set their birthday\n"
                "`/bday view [@user]` - View birthday\n"
                "`/bday list` - View all birthdays\n"
                "`/bday next` - See next upcoming birthday"
            ),
            color=COLORS["birthday"],
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def setup_xp(self, interaction: discord.Interaction):
        """Setup XP system with interactive configuration"""
        view = XPSetupView(interaction.client.db_manager, interaction.guild.id)
        
        embed = discord.Embed(
            title="🏆 XP System Setup",
            description=(
                "Configure your XP system using the button below:\n\n"
                "**Configurable XP Amounts:**\n"
                "• XP per Message\n"
                "• XP per Minute in Voice Chat\n"
                "• XP per Reaction Received\n"
                "• XP per Command Used\n"
                "• Daily Bonus XP\n\n"
                "**User Commands:**\n"
                "`/xp rank [@user]` - View XP rank\n"
                "`/xp leaderboard` - View server leaderboard\n"
                "`/xp daily` - Claim daily XP bonus\n\n"
                "**Admin Commands:**\n"
                "`/xpadmin add @user <amount>` - Add XP to user\n"
                "`/xpadmin remove @user <amount>` - Remove XP from user\n"
                "`/xpadmin set @user <amount>` - Set user's XP\n"
                "`/xpadmin reset @user` - Reset user's XP"
            ),
            color=COLORS["xp"],
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def setup_general(self, interaction: discord.Interaction):
        """Setup general settings with interactive configuration"""
        view = GeneralSettingsView(interaction.client.db_manager, interaction.guild.id)
        
        embed = discord.Embed(
            title="⚙️ General Settings Setup",
            description=(
                "Configure general bot settings using the dropdowns and buttons below:\n\n"
                "**Available Settings:**\n"
                "• **Timezone** - Affects birthday announcements and scheduled tasks\n"
                "• **Online Message Channel** - Where bot posts when coming online\n"
                "• **Bot Online Message** - Message sent when bot comes online\n\n"
                "Select options from the dropdowns and use the button to configure."
            ),
            color=COLORS["primary"],
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def view_config(self, interaction: discord.Interaction):
        """View current configuration"""
        bot = interaction.client
        db = bot.db_manager
        guild_id = interaction.guild.id

        # Fetch all settings
        verify_channel_id = await db.get_setting(f"verify_channel_{guild_id}")
        verify_role_id = await db.get_setting(f"verify_role_{guild_id}")
        staff_role_id = await db.get_setting(f"staff_role_{guild_id}")
        cheater_role_id = await db.get_setting(f"cheater_role_{guild_id}")
        cheater_channel_id = await db.get_setting(f"cheater_channel_{guild_id}")
        welcome_channel_id = await db.get_setting(f"welcome_channel_{guild_id}")
        birthday_channel_id = await db.get_setting(f"birthday_channel_{guild_id}")
        birthday_role_id = await db.get_setting(f"birthday_role_{guild_id}")
        birthday_time = await db.get_setting(f"birthday_time_{guild_id}", "08:00")
        timezone = await db.get_setting(f"timezone_{guild_id}", "UTC-6")
        online_channel_id = await db.get_setting(f"online_channel_{guild_id}")
        online_message = await db.get_setting(f"online_message_{guild_id}", "Not set")
        
        # XP settings
        message_xp = await db.get_setting(f"xp_message_{guild_id}", 10)
        voice_xp = await db.get_setting(f"xp_voice_{guild_id}", 5)
        reaction_xp = await db.get_setting(f"xp_reaction_{guild_id}", 2)
        command_xp = await db.get_setting(f"xp_command_{guild_id}", 3)
        daily_bonus = await db.get_setting(f"xp_daily_{guild_id}", 50)

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
            verify_text += f"Verified Role: <@&amp;{verify_role_id}>\n"
        if staff_role_id:
            verify_text += f"Staff Role: <@&amp;{staff_role_id}>\n"
        if cheater_role_id:
            verify_text += f"Cheater Role: <@&amp;{cheater_role_id}>\n"
        if cheater_channel_id:
            verify_text += f"Cheater Jail: <#{cheater_channel_id}>\n"
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
        if birthday_role_id:
            birthday_text += f"Role: <@&amp;{birthday_role_id}>\n"
        birthday_text += f"Time: {birthday_time}\n"
        if not birthday_channel_id and not birthday_role_id:
            birthday_text = "Not configured"
        embed.add_field(name="🎂 Birthday", value=birthday_text, inline=False)

        # XP settings
        xp_text = (
            f"Messages: {message_xp} XP\n"
            f"Voice: {voice_xp} XP/min\n"
            f"Reactions: {reaction_xp} XP\n"
            f"Commands: {command_xp} XP\n"
            f"Daily: {daily_bonus} XP"
        )
        embed.add_field(name="🏆 XP System", value=xp_text, inline=False)

        # General settings
        general_text = f"Timezone: {timezone}\n"
        if online_channel_id:
            general_text += f"Online Channel: <#{online_channel_id}>\n"
        general_text += f"Online Message: {online_message}"
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
                "⚙️ General - Timezone, online message, and other settings\n"
                "📋 View Config - See current configuration"
            ),
            color=COLORS["primary"],
        )
        embed.set_footer(text="Select an option from the dropdown below")

        view = SetupView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))