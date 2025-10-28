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
# VERIFICATION SYSTEM COMPONENTS
# ============================================================

class ChannelSelect(discord.ui.ChannelSelect):
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


class RoleSelect(discord.ui.RoleSelect):
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


class VerificationModRoleSelect(discord.ui.RoleSelect):
    """Role selector for verification mod role"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(
            placeholder="Select verification mod role (optional)...",
            min_values=0,
            max_values=1
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not self.values:
            # Clear the role if none selected
            await self.db.set_setting(f"verification_mod_role_{self.guild_id}", None)
            await interaction.response.send_message(
                embed=create_embed(
                    "Verification Mod Role Cleared",
                    "✅ Verification mod role has been cleared. General mod role will be used.",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
            return
            
        role = self.values[0]
        try:
            await self.db.set_setting(f"verification_mod_role_{self.guild_id}", role.id)
            await self.db.log_event(
                category="VERIFY",
                action="CONFIG_MOD_ROLE",
                user_id=interaction.user.id,
                details=f"Set verification mod role to {role.name}",
                guild_id=self.guild_id,
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "Verification Mod Role Set",
                    f"✅ Users with {role.mention} can review verifications\n\n"
                    f"If not set, the general mod role will be used.",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting verification mod role: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set verification mod role. Please try again.",
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
        
        # Add channel and role selects
        self.add_item(ChannelSelect(db_manager, guild.id))
        self.add_item(RoleSelect(db_manager, guild.id))
        self.add_item(VerificationModRoleSelect(db_manager, guild.id))

    @discord.ui.button(label="View Current Config", style=discord.ButtonStyle.secondary, emoji="👁️")
    async def view_config(self, interaction: discord.Interaction, button: Button):
        """View current verification configuration"""
        verify_channel_id = await self.db.get_setting(f"verify_channel_{self.guild.id}")
        verify_role_id = await self.db.get_setting(f"verify_role_{self.guild.id}")

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


# ============================================================
# GENERAL SETTINGS COMPONENTS
# ============================================================

class TimezoneModal(Modal, title="Set Timezone"):
    """Modal for setting server timezone"""
    timezone = discord.ui.Select(
        placeholder="Select your timezone",
        options=[
            discord.SelectOption(label="Eastern Time (ET)", value="America/New_York"),
            discord.SelectOption(label="Central Time (CT)", value="America/Chicago"),
            discord.SelectOption(label="Mountain Time (MT)", value="America/Denver"),
            discord.SelectOption(label="Pacific Time (PT)", value="America/Los_Angeles"),
            discord.SelectOption(label="Alaska Time (AKT)", value="America/Anchorage"),
            discord.SelectOption(label="Hawaii Time (HT)", value="Pacific/Honolulu"),
            discord.SelectOption(label="Arizona Time (AZ)", value="America/Phoenix"),
        ],
    )

    def __init__(self, db_manager, guild_id: int):
        super().__init__()
        self.db = db_manager
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await self.db.set_setting(f"timezone_{self.guild_id}", self.timezone.values[0])
            await self.db.log_event(
                category="SETTINGS",
                action="SET_TIMEZONE",
                user_id=interaction.user.id,
                details=f"Set timezone to {self.timezone.values[0]}",
                guild_id=self.guild_id,
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "Timezone Set",
                    f"✅ Server timezone set to **{self.timezone.values[0]}**\n\nThis affects birthday announcements and scheduled tasks.",
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
    """Channel selection for online message"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(placeholder="Select a channel for the online message")
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        channel = self.values[0]
        modal = OnlineMessageModal(self.db, self.guild_id, channel.id)
        await interaction.response.send_modal(modal)


class OnlineMessageModal(Modal, title="Set Bot Online Message"):
    """Modal for setting bot online message"""
    message = TextInput(
        label="Online Message",
        placeholder="Message to send when bot comes online",
        required=True,
        max_length=200,
        style=discord.TextStyle.paragraph
    )

    def __init__(self, db_manager, guild_id: int, channel_id: int):
        super().__init__()
        self.db = db_manager
        self.guild_id = guild_id
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await self.db.set_setting(f"online_message_{self.guild_id}", self.message.value)
            await self.db.set_setting(f"online_message_channel_{self.guild_id}", str(self.channel_id))
            await self.db.log_event(
                category="SETTINGS",
                action="SET_ONLINE_MESSAGE",
                user_id=interaction.user.id,
                details=f"Set online message in channel {self.channel_id}",
                guild_id=self.guild_id,
            )
            channel = interaction.guild.get_channel(self.channel_id)
            channel_name = channel.name if channel else "Unknown"
            await interaction.response.send_message(
                embed=create_embed(
                    "Online Message Set",
                    f"✅ Bot online message set in **#{channel_name}**:\n\n{self.message.value}",
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
    """View for general settings setup"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(timeout=300)
        self.db = db_manager
        self.guild_id = guild_id

    @discord.ui.button(label="Set Timezone", style=discord.ButtonStyle.primary, emoji="🌍")
    async def set_timezone(self, interaction: discord.Interaction, button: Button):
        """Set server timezone"""
        modal = TimezoneModal(self.db, self.guild_id)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Set Online Message", style=discord.ButtonStyle.primary, emoji="💬")
    async def set_online_message(self, interaction: discord.Interaction, button: Button):
        """Set bot online message"""
        view = View()
        view.add_item(OnlineMessageChannelSelect(self.db, self.guild_id))
        await interaction.response.send_message("Select a channel for the online message:", view=view, ephemeral=True)

    @discord.ui.button(label="Set Mod Role", style=discord.ButtonStyle.primary, emoji="🛡️")
    async def set_mod_role(self, interaction: discord.Interaction, button: Button):
        """Set mod role for command permissions"""
        select = discord.ui.RoleSelect(
            placeholder="Select the mod role...",
            min_values=1,
            max_values=1
        )
        
        async def role_callback(interaction: discord.Interaction):
            role = select.values[0]
            await self.db.set_setting(f"mod_role_{self.guild_id}", str(role.id))
            
            embed = discord.Embed(
                title="✅ Mod Role Set",
                description=f"Mod role has been set to {role.mention}\n\n"
                           f"Users with this role can verify users and review appeals.",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        select.callback = role_callback
        view = View(timeout=60)
        view.add_item(select)
        
        embed = discord.Embed(
            title="🛡️ Select Mod Role",
            description="Choose the role that will have moderator permissions for bot commands.",
            color=COLORS["primary"],
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="View Current Config", style=discord.ButtonStyle.secondary, emoji="👁️")
    async def view_config(self, interaction: discord.Interaction, button: Button):
        """View current general settings"""
        timezone = await self.db.get_setting(f"timezone_{self.guild_id}", "UTC-6")
        online_message = await self.db.get_setting(f"online_message_{self.guild_id}", "Not set")
        mod_role_id = await self.db.get_setting(f"mod_role_{self.guild_id}")
        
        mod_role_text = "Not set"
        if mod_role_id:
            mod_role_text = f"<@&amp;{mod_role_id}>"

        config_text = f"**Timezone:** {timezone}\n**Online Message:** {online_message}\n**Mod Role:** {mod_role_text}"

        embed = discord.Embed(
            title="Current General Settings",
            description=config_text,
            color=COLORS["info"],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


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
        """Setup general settings with interactive configuration"""
        view = GeneralSettingsView(interaction.client.db_manager, interaction.guild.id)
        
        embed = discord.Embed(
            title="⚙️ General Settings Setup",
            description=(
                "Configure general bot settings using the buttons below:\n\n"
                "**Available Settings:**\n"
                "• **Timezone** - Affects birthday announcements and scheduled tasks\n"
                "• **Bot Online Message** - Message sent when bot comes online\n"
                "• **Mod Role** - Role that can use moderation commands\n\n"
                "Click the buttons below to configure each setting."
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
        welcome_channel_id = await db.get_setting(f"welcome_channel_{guild_id}")
        birthday_channel_id = await db.get_setting(f"birthday_channel_{guild_id}")
        timezone = await db.get_setting(f"timezone_{guild_id}", "UTC-6")
        online_message = await db.get_setting(f"online_message_{guild_id}", "Not set")

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
        general_text = f"Timezone: {timezone}\nOnline Message: {online_message}"
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

    @app_commands.command(name="setup", description="Configure bot settings (Server Owner only)")
    async def setup(self, interaction: discord.Interaction):
        """Main setup command with interactive menu"""
        # Check if user is server owner
        if interaction.guild.owner_id != interaction.user.id:
            embed = discord.Embed(
                title="🚫 Permission Denied",
                description="This command is only available to the server owner.",
                color=COLORS["error"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
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