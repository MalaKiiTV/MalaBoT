"""
Setup Cog for MalaBoT
Unified configuration system for all bot features
Command: /setup
"""

import discord
from discord import ButtonStyle, app_commands
from discord.ext import commands
from discord.ui import Button, Modal, Select, TextInput, View

from src.cogs.role_connection_ui import (
    AddConnectionView,
    ManageConnectionsView,
    ProtectedRolesView,
)
from src.config.constants import COLORS
from src.utils.helpers import create_embed
from src.utils.logger import log_system

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
            channel_types=[discord.ChannelType.text],
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        channel = self.values[0]
        try:
            await self.db.set_setting("verify_channel", channel.id, self.guild_id)
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
            placeholder="Select verified role...", min_values=1, max_values=1
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]
        try:
            await self.db.set_setting("verify_role", role.id, self.guild_id)
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


class CheaterRoleSelect(discord.ui.RoleSelect):
    """Role selector for cheater role"""

    def __init__(self, db_manager, guild_id: int):
        super().__init__(
            placeholder="Select cheater role...", min_values=1, max_values=1
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]
        try:
            await self.db.set_setting("cheater_role", role.id, self.guild_id)
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
                    f"✅ Cheaters will receive {role.mention} and have all other roles removed",
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


class CheaterJailChannelSelect(discord.ui.ChannelSelect):
    """Channel selector for cheater jail"""

    def __init__(self, db_manager, guild_id: int):
        super().__init__(
            placeholder="Select cheater jail channel (optional)...",
            min_values=0,
            max_values=1,
            channel_types=[discord.ChannelType.text],
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not self.values:
            # Clear the channel if none selected
            await self.db.set_setting("cheater_jail_channel", None, self.guild_id)
            await interaction.response.send_message(
                embed=create_embed(
                    "Cheater Jail Channel Cleared",
                    "✅ Cheater jail channel has been cleared.",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
            return

        channel = self.values[0]
        try:
            await self.db.set_setting("cheater_jail_channel", channel.id, self.guild_id)
            await self.db.log_event(
                category="VERIFY",
                action="CONFIG_CHEATER_JAIL",
                user_id=interaction.user.id,
                details=f"Set cheater jail channel to {channel.name}",
                guild_id=self.guild_id,
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "Cheater Jail Channel Set",
                    f"✅ Cheater jail channel set to {channel.mention}\n\n"
                    f"Users marked as cheaters will be moved here and have all other roles removed.",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting cheater jail channel: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set cheater jail channel. Please try again.",
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
        self.add_item(VerifyChannelSelect(db_manager, guild.id))
        self.add_item(RoleSelect(db_manager, guild.id))
        self.add_item(CheaterRoleSelect(db_manager, guild.id))
        self.add_item(CheaterJailChannelSelect(db_manager, guild.id))

    @discord.ui.button(
        label="View Current Config", style=discord.ButtonStyle.secondary, emoji="👁️"
    )
    async def view_config(self, interaction: discord.Interaction, button: Button):
        """View current verification configuration"""
        verify_channel_id = await self.db.get_setting("verify_channel", self.guild.id)
        verify_role_id = await self.db.get_setting("verify_role", self.guild.id)
        cheater_role_id = await self.db.get_setting("cheater_role", self.guild.id)
        cheater_jail_id = await self.db.get_setting(
            "cheater_jail_channel", self.guild.id
        )

        config_text = ""
        if verify_channel_id:
            config_text += f"**Review Channel:** <#{verify_channel_id}>\n"
        else:
            config_text += "**Review Channel:** Not configured\n"

        if verify_role_id:
            config_text += f"**Verified Role:** <@&{verify_role_id}>\n"
        else:
            config_text += "**Verified Role:** Not configured\n"

        if cheater_role_id:
            config_text += f"**Cheater Role:** <@&{cheater_role_id}>\n"
        else:
            config_text += "**Cheater Role:** Not configured\n"

        if cheater_jail_id:
            config_text += f"**Cheater Jail:** <#{cheater_jail_id}>\n"
        else:
            config_text += "**Cheater Jail:** Not configured\n"

        embed = discord.Embed(
            title="Current Verification Configuration",
            description=config_text,
            color=COLORS["info"],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ============================================================
# GENERAL SETTINGS COMPONENTS
# ============================================================


class TimezoneSelect(discord.ui.Select):
    """Dropdown for timezone selection"""

    def __init__(self, db_manager, guild_id: int):
        self.db = db_manager
        self.guild_id = guild_id
        options = [
            discord.SelectOption(label="Eastern Time (ET)", value="America/New_York"),
            discord.SelectOption(label="Central Time (CT)", value="America/Chicago"),
            discord.SelectOption(label="Mountain Time (MT)", value="America/Denver"),
            discord.SelectOption(
                label="Pacific Time (PT)", value="America/Los_Angeles"
            ),
            discord.SelectOption(label="Alaska Time (AKT)", value="America/Anchorage"),
            discord.SelectOption(label="Hawaii Time (HT)", value="Pacific/Honolulu"),
            discord.SelectOption(label="Arizona Time (AZ)", value="America/Phoenix"),
        ]
        super().__init__(
            placeholder="Select your timezone",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            await self.db.set_setting("timezone", self.values[0], self.guild_id)
            await self.db.log_event(
                category="SETTINGS",
                action="SET_TIMEZONE",
                user_id=interaction.user.id,
                details=f"Set timezone to {self.values[0]}",
                guild_id=self.guild_id,
            )

            # Show brief confirmation
            await interaction.response.edit_message(
                embed=create_embed(
                    "✅ Timezone Set",
                    f"Timezone set to **{self.values[0]}**",
                    COLORS["success"],
                ),
                view=None,
            )

            # Wait 2 seconds then return to general settings
            import asyncio

            await asyncio.sleep(2)

            general_view = GeneralSettingsView(self.db, self.guild_id)
            embed = discord.Embed(
                title="⚙️ General Settings",
                description="Click the buttons below to configure each setting.",
                color=COLORS["primary"],
            )
            await interaction.edit_original_response(embed=embed, view=general_view)

        except Exception as e:
            log_system(f"Error setting timezone: {e}", level="error")
            await interaction.response.edit_message(
                embed=create_embed(
                    "❌ Error",
                    "Failed to set timezone.",
                    COLORS["error"],
                ),
                view=None,
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
        style=discord.TextStyle.paragraph,
    )

    def __init__(self, db_manager, guild_id: int, channel_id: int):
        super().__init__()
        self.db = db_manager
        self.guild_id = guild_id
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await self.db.set_setting(
                "online_message", self.message.value, self.guild_id
            )
            await self.db.set_setting(
                "online_message_channel", str(self.channel_id), self.guild_id
            )
            await self.db.log_event(
                category="SETTINGS",
                action="SET_ONLINE_MESSAGE",
                user_id=interaction.user.id,
                details=f"Set online message in channel {self.channel_id}",
                guild_id=self.guild_id,
            )
            channel = interaction.guild.get_channel(self.channel_id)
            channel_name = channel.name if channel else "Unknown"

            # Show brief confirmation
            await interaction.response.send_message(
                embed=create_embed(
                    "✅ Online Message Set",
                    f"Message set in **#{channel_name}**",
                    COLORS["success"],
                ),
                ephemeral=True,
            )

            # Wait 2 seconds then show general settings again
            import asyncio

            await asyncio.sleep(2)

            general_view = GeneralSettingsView(self.db, self.guild_id)
            embed = discord.Embed(
                title="⚙️ General Settings",
                description="Click the buttons below to configure each setting.",
                color=COLORS["primary"],
            )
            await interaction.edit_original_response(embed=embed, view=general_view)
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
class OnboardingRoleSelectView(View):
    """View for selecting onboarding role from dropdown"""

    def __init__(self, db_manager, guild_id: int, guild: discord.Guild):
        super().__init__(timeout=300)
        self.db = db_manager
        self.guild_id = guild_id
        self.guild = guild

        # Get all roles except @everyone and sort by position (highest first)
        roles = [r for r in guild.roles if r.name != "@everyone"]
        roles.sort(key=lambda r: r.position, reverse=True)
        roles = roles[:25]

        # Create select menu options
        options = [
            discord.SelectOption(
                label=role.name,
                value=str(role.id),
                description=f"Position: {role.position}",
                emoji="📋",
            )
            for role in roles
        ]

        # Add the select menu
        select = discord.ui.Select(
            placeholder="Choose onboarding role...",
            options=options,
            custom_id="onboarding_role_select",
        )
        select.callback = self.role_selected
        self.add_item(select)

        # Add cancel button
        cancel_button = Button(
            label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌"
        )
        cancel_button.callback = self.cancel
        self.add_item(cancel_button)

    async def role_selected(self, interaction: discord.Interaction):
        """Handle role selection"""
        role_id = interaction.data["values"][0]
        role = self.guild.get_role(int(role_id))

        if not role:
            embed = discord.Embed(
                title="❌ Error",
                description="Could not find the selected role. Please try again.",
                color=COLORS["error"],
            )
            await interaction.edit_original_response(embed=embed, view=None)

            import asyncio
            await asyncio.sleep(3)

            general_view = GeneralSettingsView(self.db, self.guild_id)
            embed = discord.Embed(
                title="⚙️ General Settings",
                description="Click the buttons below to configure each setting.",
                color=COLORS["primary"],
            )
            await interaction.edit_original_response(embed=embed, view=general_view)
            return

        # Save the role
        await self.db.set_setting("onboarding_role", str(role.id), self.guild_id)

        # Show confirmation
        embed = discord.Embed(
            title="✅ Onboarding Role Set",
            description=f"Members will receive {role.mention} until they complete onboarding",
            color=COLORS["success"],
        )
        await interaction.edit_original_response(embed=embed, view=None)

        # Wait 2 seconds then return to general settings
        import asyncio
        await asyncio.sleep(2)

        general_view = GeneralSettingsView(self.db, self.guild_id)
        embed = discord.Embed(
            title="⚙️ General Settings",
            description="Click the buttons below to configure each setting.",
            color=COLORS["primary"],
        )
        await interaction.edit_original_response(embed=embed, view=general_view)

    async def cancel(self, interaction: discord.Interaction):
        """Cancel and return to general settings"""
        general_view = GeneralSettingsView(self.db, self.guild_id)
        embed = discord.Embed(
            title="⚙️ General Settings",
            description="Click the buttons below to configure each setting.",
            color=COLORS["primary"],
        )
        await interaction.response.edit_message(embed=embed, view=general_view)

class GeneralSettingsView(View):
    """View for general settings setup"""

    def __init__(self, db_manager, guild_id: int):
        super().__init__(timeout=300)
        self.db = db_manager
        self.guild_id = guild_id

    async def show_general_settings(
        self, interaction: discord.Interaction, is_followup: bool = False
    ):
        """Show the general settings menu"""
        embed = discord.Embed(
            title="⚙️ General Settings",
            description="Click the buttons below to configure each setting.",
            color=COLORS["primary"],
        )
        new_view = GeneralSettingsView(self.db, self.guild_id)

        # Always edit the original message to avoid creating duplicates
        await interaction.message.edit(embed=embed, view=new_view)

    @discord.ui.button(
        label="Set Timezone", style=discord.ButtonStyle.primary, emoji="🌍"
    )
    async def set_timezone(self, interaction: discord.Interaction, button: Button):
        """Set server timezone"""
        view = discord.ui.View()
        view.add_item(TimezoneSelect(self.db, self.guild_id))

        embed = discord.Embed(
            title="🌍 Select Timezone",
            description="Choose your server's timezone.",
            color=COLORS["primary"],
        )
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(
        label="Set Online Message", style=discord.ButtonStyle.primary, emoji="💬"
    )
    async def set_online_message(
        self, interaction: discord.Interaction, button: Button
    ):
        """Set bot online message"""
        view = View()
        view.add_item(OnlineMessageChannelSelect(self.db, self.guild_id))

        embed = discord.Embed(
            title="💬 Set Online Message",
            description="Select a channel for the online message.",
            color=COLORS["primary"],
        )
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(
        label="Set Mod Role", style=discord.ButtonStyle.primary, emoji="🛡️"
    )
    async def set_mod_role(self, interaction: discord.Interaction, button: Button):
        """Set mod role for command permissions"""
        select = discord.ui.RoleSelect(
            placeholder="Select the mod role...", min_values=1, max_values=1
        )

        async def role_callback(interaction: discord.Interaction):
            role = select.values[0]
            await self.db.set_setting("mod_role", str(role.id), self.guild_id)

            # Show brief confirmation
            embed = discord.Embed(
                title="✅ Mod Role Set",
                description=f"Mod role set to {role.mention}",
                color=COLORS["success"],
            )
            await interaction.edit_original_response(embed=embed, view=None)

            # Wait 2 seconds then return to general settings
            import asyncio

            await asyncio.sleep(2)

            general_view = GeneralSettingsView(self.db, self.guild_id)
            embed = discord.Embed(
                title="⚙️ General Settings",
                description="Click the buttons below to configure each setting.",
                color=COLORS["primary"],
            )
            await interaction.edit_original_response(embed=embed, view=general_view)

        select.callback = role_callback
        view = View(timeout=60)
        view.add_item(select)

        embed = discord.Embed(
            title="🛡️ Select Mod Role",
            description="Choose the mod role.",
            color=COLORS["primary"],
        )
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(
        label="View Current Config", style=discord.ButtonStyle.secondary, emoji="👁️"
    )
    async def view_config(self, interaction: discord.Interaction, button: Button):
        """View current general settings"""
        timezone = await self.db.get_setting("timezone", self.guild_id)
        online_message = await self.db.get_setting("online_message", self.guild_id)
        online_channel_id = await self.db.get_setting(
            "online_message_channel", self.guild_id
        )
        mod_role_id = await self.db.get_setting("mod_role", self.guild_id)
        mod_role_text = "Not set"
        if mod_role_id:
            try:
                mod_role = interaction.guild.get_role(int(mod_role_id))
                if mod_role:
                    mod_role_text = f"{mod_role.name}"
                else:
                    mod_role_text = f"<@&{mod_role_id}>"
            except (ValueError, AttributeError):
                mod_role_text = f"<@&{mod_role_id}>"

        online_channel_text = "Not set"
        if online_channel_id:
            online_channel_text = f"<#{online_channel_id}>"

        # Get onboarding role
        onboarding_role_id = await self.db.get_setting("onboarding_role", self.guild_id)
        onboarding_role_text = "Not set"
        if onboarding_role_id:
            try:
                onboarding_role = interaction.guild.get_role(int(onboarding_role_id))
                if onboarding_role:
                    onboarding_role_text = f"{onboarding_role.name}"
                else:
                    onboarding_role_text = f"<@&{onboarding_role_id}>"
            except (ValueError, AttributeError):
                onboarding_role_text = f"<@&{onboarding_role_id}>"

        config_text = f"**Timezone:** {timezone}\n**Online Message:** {online_message}\n**Online Channel:** {online_channel_text}\n**Mod Role:** {mod_role_text}\n**Onboarding Role:** {onboarding_role_text}"

        embed = discord.Embed(
            title="Current General Settings",
            description=config_text,
            color=COLORS["info"],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="Set Onboarding Role", style=discord.ButtonStyle.primary, emoji="📋", row=1
    )
    async def set_onboarding_role(self, interaction: discord.Interaction, button: Button):
        """Set role to auto-assign to members completing onboarding"""
        view = OnboardingRoleSelectView(self.db, self.guild_id, interaction.guild)

        embed = discord.Embed(
            title="📋 Set Onboarding Role",
            description="Select a role from the dropdown below to auto-assign to members who haven't completed onboarding.\n\n"
            "**Note:** This role will be removed once they complete onboarding.",
            color=COLORS["primary"],
        )

        await interaction.response.edit_message(embed=embed, view=view)

# ============================================================
# ROLE CONNECTION SYSTEM COMPONENTS
# ============================================================


class RoleConnectionSetupView(View):
    """Main view for role connection management"""

    def __init__(self, manager, guild: discord.Guild):
        super().__init__(timeout=300)
        self.manager = manager
        self.guild = guild
        self.add_item(RoleConnectionMainSelect(manager, guild))


class RoleConnectionMainSelect(Select):
    """Main menu for role connections"""

    def __init__(self, manager, guild: discord.Guild):
        self.manager = manager
        self.guild = guild
        options = [
            discord.SelectOption(
                label="Add Connection",
                value="add",
                description="Create a new role connection rule",
                emoji="➕",
            ),
            discord.SelectOption(
                label="Manage Connections",
                value="manage",
                description="View, edit, or delete existing connections",
                emoji="📝",
            ),
            discord.SelectOption(
                label="Protected Roles",
                value="protected",
                description="Manage roles exempt from connections",
                emoji="🛡️",
            ),
            discord.SelectOption(
                label="Back to Setup",
                value="back",
                description="Return to main setup menu",
                emoji="◀️",
            ),
        ]
        super().__init__(
            placeholder="Select an option...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]

        if selection == "add":
            await self.add_connection(interaction)
        elif selection == "manage":
            await self.manage_connections(interaction)
        elif selection == "protected":
            await self.manage_protected_roles(interaction)
        elif selection == "back":
            await self.back_to_setup(interaction)

    async def add_connection(self, interaction: discord.Interaction):
        """Start the process of adding a new connection"""
        view = AddConnectionView(self.manager, self.guild)

        embed = discord.Embed(
            title="➕ Add Role Connection",
            description=(
                "**Step 1: Select Target Role**\n"
                "Choose the role that will be given or removed.\n\n"
                "After selecting the role, you'll configure:\n"
                "• Action (Give or Remove)\n"
                "• Conditions (Has/Doesn't Have roles)\n"
                "• Logic (AND/OR)"
            ),
            color=COLORS["primary"],
        )

        await interaction.response.edit_message(embed=embed, view=view)

    async def manage_connections(self, interaction: discord.Interaction):
        """Show list of connections to manage"""
        # Force reload from database to ensure fresh data
        self.manager.connections_cache[self.guild.id] = []  # Clear cache
        await self.manager.load_connections(self.guild.id)
        connections = self.manager.connections_cache.get(self.guild.id, [])

        if not connections:
            await interaction.response.send_message(
                embed=create_embed(
                    "No Connections",
                    "No role connections have been configured yet.\nUse 'Add Connection' to create one.",
                    COLORS["warning"],
                ),
                ephemeral=True,
            )
            return

        view = ManageConnectionsView(self.manager, self.guild, connections)

        embed = discord.Embed(
            title="📝 Manage Connections",
            description="Select a connection to toggle, edit, or delete:",
            color=COLORS["primary"],
        )

        for i, conn in enumerate(connections[:25], 1):
            target_role = self.guild.get_role(conn.target_role_id)
            if target_role:
                status = "✅ Enabled" if conn.enabled else "❌ Disabled"

                # Build condition text
                cond_text = []
                for cond in conn.conditions:
                    role = self.guild.get_role(cond["role_id"])
                    if role:
                        cond_type = "HAS" if cond["type"] == "has" else "DOESN'T HAVE"
                        cond_text.append(f"{cond_type} {role.name}")

                conditions_str = (
                    f" {conn.logic} ".join(cond_text) if cond_text else "No conditions"
                )

                embed.add_field(
                    name=f"{i}. {conn.action.title()} {target_role.name} ({status})",
                    value=f"When: {conditions_str}",
                    inline=False,
                )

        await interaction.response.edit_message(embed=embed, view=view)

    async def manage_protected_roles(self, interaction: discord.Interaction):
        """Manage protected roles"""
        await self.manager.load_protected_roles(self.guild.id)
        protected = self.manager.protected_roles_cache.get(self.guild.id, [])

        view = ProtectedRolesView(self.manager, self.guild)

        embed = discord.Embed(
            title="🛡️ Protected Roles",
            description=(
                "Users with protected roles are exempt from ALL role connection rules.\n\n"
                "**Current Protected Roles:**"
            ),
            color=COLORS["primary"],
        )

        if protected:
            role_list = []
            for role_id in protected:
                role = self.guild.get_role(role_id)
                if role:
                    role_list.append(f"• {role.mention}")
            embed.add_field(
                name="Protected", value="\n".join(role_list) or "None", inline=False
            )
        else:
            embed.add_field(
                name="Protected", value="*No protected roles set*", inline=False
            )

        await interaction.response.edit_message(embed=embed, view=view)

    async def back_to_setup(self, interaction: discord.Interaction):
        """Return to main setup menu"""
        view = SetupView()

        embed = discord.Embed(
            title="⚙️ MalaBoT Setup",
            description="Select a system to configure:",
            color=COLORS["primary"],
        )

        await interaction.response.edit_message(embed=embed, view=view)


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
                emoji="✅",
            ),
            discord.SelectOption(
                label="Welcome System",
                value="welcome",
                description="Configure welcome messages and channel",
                emoji="👋",
            ),
            discord.SelectOption(
                label="Birthday System",
                value="birthday",
                description="Configure birthday announcements",
                emoji="🎂",
            ),
            discord.SelectOption(
                label="XP System",
                value="xp",
                description="Configure XP and leveling settings",
                emoji="🏆",
            ),
            discord.SelectOption(
                label="General Settings",
                value="general",
                description="Configure timezone, online message, etc.",
                emoji="⚙️",
            ),
            discord.SelectOption(
                label="Role Connections",
                value="role_connections",
                description="Configure automatic role assignment rules",
                emoji="🔗",
            ),
            discord.SelectOption(
                label="View Current Config",
                value="view",
                description="View all current bot settings",
                emoji="📋",
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
        elif selection == "role_connections":
            await self.setup_role_connections(interaction)
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
                "Configure your welcome and goodbye systems:\n\n"
                "**Available Variables:**\n"
                "`{member}` - Mentions the new member\n"
                "`{member.name}` - Member's username\n"
                "`{server}` - Server name\n"
                "`{member.count}` - Total member count\n\n"
                "Click the buttons below to configure welcome settings.\n"
                "Use the **Goodbye System** button to configure goodbye messages."
            ),
            color=COLORS["welcome"],
        )

        view = WelcomeSetupView(interaction.guild.id, interaction.client.db_manager)
        await interaction.response.edit_message(embed=embed, view=view)

    async def setup_birthday(self, interaction: discord.Interaction):
        """Setup birthday system"""
        embed = discord.Embed(
            title="🎂 Birthday System Setup",
            description=(
                "Configure your birthday system:\n\n"
                "**Available Variables:**\n"
                "`{member}` - Mentions the birthday person\n"
                "`{member.name}` - Member's username\n"
                "`{age}` - Age (if year provided)\n\n"
                "**User Commands:**\n"
                "`/bday set <MM-DD>` - Users set their birthday\n"
                "`/bday view [@user]` - View birthday\n"
                "`/bday list` - View all birthdays\n"
                "`/bday next` - See next upcoming birthday\n\n"
                "Click the buttons below to configure each setting."
            ),
            color=COLORS["birthday"],
        )

        view = BirthdaySetupView(interaction.guild.id, interaction.client.db_manager)
        await interaction.response.edit_message(embed=embed, view=view)

    async def setup_xp(self, interaction: discord.Interaction):
        """Setup XP system"""
        embed = discord.Embed(
            title="🏆 XP System Setup",
            description=(
                "Configure your XP system:\n\n"
                "**User Commands:**\n"
                "`/xp rank [@user]` - View XP rank\n"
                "`/xp leaderboard` - View server leaderboard\n"
                "`/xp daily` - Claim daily XP bonus\n\n"
                "**XP Sources:**\n"
                "• Message XP - XP gained per message sent\n"
                "• Reaction XP - XP gained per reaction received\n"
                "• Voice XP - XP gained per minute in voice chat\n"
                "• XP Cooldown - Time between XP gains\n\n"
                "Click the buttons below to configure XP settings."
            ),
            color=COLORS["xp"],
        )

        view = XPSetupView(interaction.guild.id, interaction.client.db_manager)
        await interaction.response.edit_message(embed=embed, view=view)

    async def setup_general(self, interaction: discord.Interaction):
        """Setup general settings with interactive configuration"""
        view = GeneralSettingsView(interaction.client.db_manager, interaction.guild.id)

        embed = discord.Embed(
            title="⚙️ General Settings",
            description="Click the buttons below to configure each setting.",
            color=COLORS["primary"],
        )
        await interaction.response.edit_message(embed=embed, view=view)

    async def view_config(self, interaction: discord.Interaction):
        """View current configuration"""
        await interaction.response.defer()
        bot = interaction.client
        db = bot.db_manager
        guild_id = interaction.guild.id
        # Fetch all settings
        verify_channel_id = await db.get_setting("verify_channel", guild_id)
        verify_role_id = await db.get_setting("verify_role", guild_id)
        cheater_role_id = await db.get_setting("cheater_role", guild_id)
        cheater_jail_id = await db.get_setting("cheater_jail_channel", guild_id)
        mod_role_id = await db.get_setting("mod_role", guild_id)
        welcome_channel_id = await db.get_setting("welcome_channel", guild_id)
        welcome_message = await db.get_setting("welcome_message", guild_id)
        welcome_title = await db.get_setting("welcome_title", guild_id)
        goodbye_channel_id = await db.get_setting("goodbye_channel", guild_id)
        goodbye_message = await db.get_setting("goodbye_message", guild_id)
        goodbye_title = await db.get_setting("goodbye_title", guild_id)
        birthday_channel_id = await db.get_setting("birthday_channel", guild_id)
        birthday_time = await db.get_setting("birthday_time", guild_id)
        birthday_message = await db.get_setting("birthday_message", guild_id)
        xp_channel_id = await db.get_setting("xp_channel", guild_id)
        xp_per_message = await db.get_setting("xp_per_message", guild_id)
        xp_per_reaction = await db.get_setting("xp_per_reaction", guild_id)
        xp_per_voice = await db.get_setting("xp_per_voice_minute", guild_id)
        xp_cooldown = await db.get_setting("xp_cooldown", guild_id)
        timezone = await db.get_setting("timezone", guild_id)
        online_message = await db.get_setting("online_message", guild_id)
        
        # Fetch all toggle settings
        welcome_enabled = await db.get_setting("welcome_enabled", guild_id)
        goodbye_enabled = await db.get_setting("goodbye_enabled", guild_id)
        birthday_announcements_enabled = await db.get_setting("birthday_announcements_enabled", guild_id)
        birthday_pending_enabled = await db.get_setting("birthday_pending_enabled", guild_id)
        xp_message_enabled = await db.get_setting("xp_message_enabled", guild_id)
        xp_reaction_enabled = await db.get_setting("xp_reaction_enabled", guild_id)
        xp_voice_enabled = await db.get_setting("xp_voice_enabled", guild_id)
        
        # Fetch additional settings
        welcome_image = await db.get_setting("welcome_image", guild_id)
        goodbye_image = await db.get_setting("goodbye_image", guild_id)
        birthday_xp = await db.get_setting("birthday_set_xp", guild_id)
        birthday_pending_role_id = await db.get_setting("birthday_pending_role", guild_id)
        birthday_reminder_channel_id = await db.get_setting("birthday_reminder_channel", guild_id)
        online_channel_id = await db.get_setting("online_message_channel", guild_id)
        onboarding_role_id = await db.get_setting("onboarding_role", guild_id)

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
        if cheater_role_id:
            verify_text += f"Cheater Role: <@&{cheater_role_id}>\n"
        if cheater_jail_id:
            verify_text += f"Cheater Jail: <#{cheater_jail_id}>\n"
        if not verify_text:
            verify_text = "Not configured"
        embed.add_field(name="✅ Verification", value=verify_text, inline=False)

        # Welcome settings
        welcome_text = f"**Status:** {'✅ Enabled' if welcome_enabled == 'true' else '❌ Disabled'}\n"
        if welcome_channel_id:
            welcome_text += f"Channel: <#{welcome_channel_id}>\n"
            if welcome_title:
                welcome_text += f"Title: {welcome_title}\n"
            if welcome_message:
                welcome_text += f"Message: {welcome_message[:50]}{'...' if len(welcome_message) > 50 else ''}\n"
            if welcome_image:
                welcome_text += f"Image: Set\n"
        else:
            welcome_text += "Channel: Not configured\n"
        embed.add_field(name="👋 Welcome", value=welcome_text, inline=False)

        # Goodbye settings
        goodbye_text = f"**Status:** {'✅ Enabled' if goodbye_enabled == 'true' else '❌ Disabled'}\n"
        if goodbye_channel_id:
            goodbye_text += f"Channel: <#{goodbye_channel_id}>\n"
            if goodbye_title:
                goodbye_text += f"Title: {goodbye_title}\n"
            if goodbye_message:
                goodbye_text += f"Message: {goodbye_message[:50]}{'...' if len(goodbye_message) > 50 else ''}\n"
            if goodbye_image:
                goodbye_text += f"Image: Set\n"
        else:
            goodbye_text += "Channel: Not configured\n"
        embed.add_field(name="👋 Goodbye", value=goodbye_text, inline=False)

        # Birthday settings
        birthday_text = f"**Announcements:** {'✅ Enabled' if birthday_announcements_enabled == 'true' else '❌ Disabled'}\n"
        birthday_text += f"**Pending System:** {'✅ Enabled' if birthday_pending_enabled == 'true' else '❌ Disabled'}\n"
        if birthday_channel_id:
            birthday_text += f"Channel: <#{birthday_channel_id}>\n"
            if birthday_time:
                birthday_text += f"Time: {birthday_time}\n"
            if birthday_message:
                birthday_text += f"Message: {birthday_message[:50]}{'...' if len(birthday_message) > 50 else ''}\n"
        else:
            birthday_text += "Channel: Not configured\n"
        if birthday_xp:
            birthday_text += f"XP Reward: {birthday_xp} XP\n"
        if birthday_pending_enabled == 'true':
            if birthday_pending_role_id:
                birthday_text += f"Pending Role: <@&{birthday_pending_role_id}>\n"
            if birthday_reminder_channel_id:
                birthday_text += f"Reminder Channel: <#{birthday_reminder_channel_id}>\n"
        embed.add_field(name="🎂 Birthday", value=birthday_text, inline=False)

        # XP settings
        xp_text = f"**Message XP:** {'✅ Enabled' if xp_message_enabled == 'true' else '❌ Disabled'}\n"
        xp_text += f"**Reaction XP:** {'✅ Enabled' if xp_reaction_enabled == 'true' else '❌ Disabled'}\n"
        xp_text += f"**Voice XP:** {'✅ Enabled' if xp_voice_enabled == 'true' else '❌ Disabled'}\n"
        xp_text += "\n**Settings:**\n"
        if xp_channel_id:
            xp_text += f"Level-up Channel: <#{xp_channel_id}>\n"
        if xp_per_message:
            xp_text += f"Message XP: {xp_per_message}\n"
        if xp_per_reaction:
            xp_text += f"Reaction XP: {xp_per_reaction}\n"
        if xp_per_voice:
            xp_text += f"Voice XP: {xp_per_voice}/min\n"
        if xp_cooldown:
            xp_text += f"Cooldown: {xp_cooldown}s\n"
        embed.add_field(name="🏆 XP System", value=xp_text, inline=False)

        # General settings
        general_text = f"**Timezone:** {timezone}\n"
        general_text += f"**Online Message:** {online_message}\n"
        if online_channel_id:
            general_text += f"**Online Channel:** <#{online_channel_id}>\n"
        if mod_role_id:
            general_text += f"**Mod Role:** <@&{mod_role_id}>\n"
        if onboarding_role_id:
            general_text += f"**Onboarding Role:** <@&{onboarding_role_id}>\n"
        embed.add_field(name="⚙️ General", value=general_text, inline=False)

        # Role Connections settings
        role_conn_cog = interaction.client.get_cog("RoleConnections")
        if role_conn_cog:
            manager = role_conn_cog.manager
            await manager.load_connections(guild_id)
            await manager.load_protected_roles(guild_id)

            connections = manager.connections_cache.get(guild_id, [])
            protected_roles = manager.protected_roles_cache.get(guild_id, [])

            active_count = sum(1 for conn in connections if conn.enabled)
            disabled_count = sum(1 for conn in connections if not conn.enabled)

            role_conn_text = f"Active Connections: {active_count}\n"
            role_conn_text += f"Disabled Connections: {disabled_count}\n"
            role_conn_text += f"Protected Roles: {len(protected_roles)}"

            embed.add_field(
                name="🔗 Role Connections", value=role_conn_text, inline=False
            )

        await interaction.edit_original_response(embed=embed, view=None)

    async def setup_role_connections(self, interaction: discord.Interaction):
        """Setup role connections system"""
        # Get the role connections manager from the bot
        role_conn_cog = interaction.client.get_cog("RoleConnections")
        if not role_conn_cog:
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Role Connections system is not loaded. Please contact an administrator.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )
            return

        manager = role_conn_cog.manager
        await manager.load_connections(interaction.guild.id)
        await manager.load_protected_roles(interaction.guild.id)

        view = RoleConnectionSetupView(manager, interaction.guild)

        embed = discord.Embed(
            title="🔗 Role Connection System",
            description=(
                "Automatically assign or remove roles based on conditions.\n\n"
                "**How it works:**\n"
                "• Create rules that give/remove roles when conditions are met\n"
                "• Conditions: User HAS or DOESN'T HAVE specific roles\n"
                "• Logic: Combine conditions with AND/OR\n"
                "• Protected Roles: Users with these roles are exempt from all rules\n\n"
                "**Example Rules:**\n"
                "• Give 'Sus' when user doesn't have 'Mala'\n"
                "• Give 'VIP' when user has 'Subscriber' AND 'Active'\n"
                "• Remove 'Guest' when user has 'Member'"
            ),
            color=COLORS["primary"],
        )

        # Show current connections
        connections = manager.connections_cache.get(interaction.guild.id, [])
        if connections:
            conn_text = ""
            for i, conn in enumerate(connections[:10], 1):
                target_role = interaction.guild.get_role(conn.target_role_id)
                if target_role:
                    status = "✅" if conn.enabled else "❌"
                    conn_text += (
                        f"{status} {i}. {conn.action.title()} **{target_role.name}**\n"
                    )
            embed.add_field(
                name="Active Connections", value=conn_text or "None", inline=False
            )

        # Show protected roles
        protected = manager.protected_roles_cache.get(interaction.guild.id, [])
        if protected:
            protected_text = " ".join(
                [f"<@&amp;{role_id}>" for role_id in protected[:10]]
            )
            embed.add_field(
                name="🛡️ Protected Roles", value=protected_text, inline=False
            )

        await interaction.response.edit_message(embed=embed, view=view)


class SetupView(View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(SetupSelect())


class WelcomeSetupView(View):
    def __init__(self, guild_id: int, db_manager):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.db_manager = db_manager

    @discord.ui.button(label="Set Channel", style=ButtonStyle.primary, emoji="📢")
    async def set_channel(self, interaction: discord.Interaction, button: Button):
        """Set welcome channel"""
        # Defer immediately to prevent timeout
        await interaction.response.defer(ephemeral=True)

        view = View()
        select = discord.ui.ChannelSelect(
            placeholder="Select welcome channel",
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1,
        )

        async def channel_callback(interaction: discord.Interaction):
            channel = select.values[0]
            await self.db_manager.set_setting(
                "welcome_channel", str(channel.id), self.guild_id
            )
            embed = discord.Embed(
                title="✅ Welcome Channel Set",
                description=f"Welcome messages will be sent to {channel.mention}",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        select.callback = channel_callback
        view.add_item(select)

        embed = discord.Embed(
            title="📢 Select Welcome Channel",
            description="Choose the channel where welcome messages will be sent.",
            color=COLORS["primary"],
        )
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Set Message", style=ButtonStyle.primary, emoji="💬")
    async def set_message(self, interaction: discord.Interaction, button: Button):
        """Set welcome message"""
        modal = Modal(title="Set Welcome Message")
        message_input = discord.ui.TextInput(
            label="Welcome Message",
            default="Welcome {member} to {server}!",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000,
        )
        modal.add_item(message_input)

        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting(
                "welcome_message", message_input.value, self.guild_id
            )
            embed = discord.Embed(
                title="✅ Welcome Message Set",
                description=f"Message: {message_input.value}",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Set Title", style=ButtonStyle.primary, emoji="📝")
    async def set_title(self, interaction: discord.Interaction, button: Button):
        """Set welcome title"""
        modal = Modal(title="Set Welcome Title")
        title_input = discord.ui.TextInput(
            label="Welcome Title",
            placeholder="Welcome to the Server!",
            style=discord.TextStyle.short,
            required=True,
            max_length=100,
        )
        modal.add_item(title_input)

        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting(
                "welcome_title", title_input.value, self.guild_id
            )
            embed = discord.Embed(
                title="✅ Welcome Title Set",
                description=f"Title: {title_input.value}",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Set Image", style=ButtonStyle.primary, emoji="🖼️")
    async def set_image(self, interaction: discord.Interaction, button: Button):
        """Set welcome image"""
        modal = Modal(title="Set Welcome Image")
        image_input = discord.ui.TextInput(
            label="Image URL (Optional)",
            placeholder="https://i.imgur.com/example.png",
            style=discord.TextStyle.short,
            required=False,
            max_length=500,
        )
        modal.add_item(image_input)

        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting(
                "welcome_image", image_input.value or "", self.guild_id
            )
            embed = discord.Embed(
                title="✅ Welcome Image Set",
                description=f"Image URL: {image_input.value or 'None (removed)'}\n\n**Tip:** Upload your image to Discord, right-click it, and select 'Copy Link' to get a URL!",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Toggle System", style=ButtonStyle.success, emoji="🔄", row=1)
    async def toggle_welcome(self, interaction: discord.Interaction, button: Button):
        """Toggle welcome system on/off"""
        current = await self.db_manager.get_setting("welcome_enabled", self.guild_id)
        new_state = "false" if current == "true" else "true"
        
        await self.db_manager.set_setting("welcome_enabled", new_state, self.guild_id)
        
        status = "✅ Enabled" if new_state == "true" else "❌ Disabled"
        embed = discord.Embed(
            title=f"Welcome System {status}",
            description=f"System is now **{status.split()[1]}**",
            color=COLORS["success"] if new_state == "true" else COLORS["error"],
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="View Config", style=ButtonStyle.secondary, emoji="📋", row=1)
    async def view_welcome_config(self, interaction: discord.Interaction, button: Button):
        """View current welcome configuration"""
        welcome_channel_id = await self.db_manager.get_setting("welcome_channel", self.guild_id)
        welcome_title = await self.db_manager.get_setting("welcome_title", self.guild_id)
        welcome_message = await self.db_manager.get_setting("welcome_message", self.guild_id)
        welcome_enabled = await self.db_manager.get_setting("welcome_enabled", self.guild_id)
        welcome_image = await self.db_manager.get_setting("welcome_image", self.guild_id)
        
        config_text = ""
        if welcome_channel_id:
            config_text += f"**Channel:** <#{welcome_channel_id}>\n"
        else:
            config_text += "**Channel:** Not configured\n"
            
        if welcome_title:
            config_text += f"**Title:** {welcome_title}\n"
        else:
            config_text += "**Title:** Not set\n"
            
        if welcome_message:
            msg_preview = welcome_message[:50] + "..." if len(welcome_message) > 50 else welcome_message
            config_text += f"**Message:** {msg_preview}\n"
        else:
            config_text += "**Message:** Not set\n"
            
        if welcome_image:
            config_text += f"**Image:** {welcome_image}\n"
        else:
            config_text += "**Image:** Not set\n"
            
        config_text += f"**Status:** {'✅ Enabled' if welcome_enabled == 'true' else '❌ Disabled'}\n"
        
        embed = discord.Embed(
            title="📋 Welcome System Configuration",
            description=config_text,
            color=COLORS["info"],
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="Goodbye System", style=ButtonStyle.secondary, emoji="👋", row=1
    )
    async def goto_goodbye(self, interaction: discord.Interaction, button: Button):
        """Navigate to goodbye system setup"""
        embed = discord.Embed(
            title="👋 Goodbye System Setup",
            description=(
                "Configure your goodbye system:\n\n"
                "**Available Variables:**\n"
                "`{member.mention}` - Mentions the member who left\n"
                "`{member.name}` - Member's username\n"
                "`{server.name}` - Server name\n"
                "`{member.count}` - Total member count\n\n"
                "Click the buttons below to configure each setting."
            ),
            color=COLORS["error"],
        )

        view = GoodbyeSetupView(self.guild_id, self.db_manager)
        await interaction.response.edit_message(embed=embed, view=view)


class GoodbyeSetupView(View):
    def __init__(self, guild_id: int, db_manager):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.db_manager = db_manager

    @discord.ui.button(label="Set Channel", style=ButtonStyle.primary, emoji="📢")
    async def set_channel(self, interaction: discord.Interaction, button: Button):
        """Set goodbye channel"""
        # Defer immediately to prevent timeout
        await interaction.response.defer(ephemeral=True)

        view = View()
        select = discord.ui.ChannelSelect(
            placeholder="Select goodbye channel",
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1,
        )

        async def channel_callback(interaction: discord.Interaction):
            channel = select.values[0]
            await self.db_manager.set_setting(
                "goodbye_channel", str(channel.id), self.guild_id
            )
            embed = discord.Embed(
                title="✅ Goodbye Channel Set",
                description=f"Goodbye messages will be sent to {channel.mention}",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        select.callback = channel_callback
        view.add_item(select)

        embed = discord.Embed(
            title="📢 Select Goodbye Channel",
            description="Choose the channel where goodbye messages will be sent.",
            color=COLORS["primary"],
        )
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Set Message", style=ButtonStyle.primary, emoji="💬")
    async def set_message(self, interaction: discord.Interaction, button: Button):
        """Set goodbye message"""
        modal = Modal(title="Set Goodbye Message")
        message_input = discord.ui.TextInput(
            label="Goodbye Message",
            default="{member.name} has left {server}. We'll miss you!",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000,
        )
        modal.add_item(message_input)

        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting(
                "goodbye_message", message_input.value, self.guild_id
            )
            embed = discord.Embed(
                title="✅ Goodbye Message Set",
                description=f"Message: {message_input.value}",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Set Title", style=ButtonStyle.primary, emoji="📝")
    async def set_title(self, interaction: discord.Interaction, button: Button):
        """Set goodbye title"""
        modal = Modal(title="Set Goodbye Title")
        title_input = discord.ui.TextInput(
            label="Goodbye Title",
            placeholder="Goodbye!",
            style=discord.TextStyle.short,
            required=True,
            max_length=100,
        )
        modal.add_item(title_input)

        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting(
                "goodbye_title", title_input.value, self.guild_id
            )
            embed = discord.Embed(
                title="✅ Goodbye Title Set",
                description=f"Title: {title_input.value}",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Set Image", style=ButtonStyle.primary, emoji="🖼️")
    async def set_image(self, interaction: discord.Interaction, button: Button):
        """Set goodbye image"""
        modal = Modal(title="Set Goodbye Image")
        image_input = discord.ui.TextInput(
            label="Image URL (Optional)",
            placeholder="https://i.imgur.com/example.png",
            style=discord.TextStyle.short,
            required=False,
            max_length=500,
        )
        modal.add_item(image_input)

        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting(
                "goodbye_image", image_input.value or "", self.guild_id
            )
            embed = discord.Embed(
                title="✅ Goodbye Image Set",
                description=f"Image URL: {image_input.value or 'None (removed)'}\n\n**Tip:** Upload your image to Discord, right-click it, and select 'Copy Link' to get a URL!",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Toggle System", style=ButtonStyle.success, emoji="🔄", row=1)
    async def toggle_goodbye(self, interaction: discord.Interaction, button: Button):
        """Toggle goodbye system on/off"""
        current = await self.db_manager.get_setting("goodbye_enabled", self.guild_id)
        new_state = "false" if current == "true" else "true"
        
        await self.db_manager.set_setting("goodbye_enabled", new_state, self.guild_id)
        
        status = "✅ Enabled" if new_state == "true" else "❌ Disabled"
        embed = discord.Embed(
            title=f"Goodbye System {status}",
            description=f"System is now **{status.split()[1]}**",
            color=COLORS["success"] if new_state == "true" else COLORS["error"],
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="View Config", style=ButtonStyle.secondary, emoji="📋", row=1)
    async def view_goodbye_config(self, interaction: discord.Interaction, button: Button):
        """View current goodbye configuration"""
        goodbye_channel_id = await self.db_manager.get_setting("goodbye_channel", self.guild_id)
        goodbye_title = await self.db_manager.get_setting("goodbye_title", self.guild_id)
        goodbye_message = await self.db_manager.get_setting("goodbye_message", self.guild_id)
        goodbye_enabled = await self.db_manager.get_setting("goodbye_enabled", self.guild_id)
        goodbye_image = await self.db_manager.get_setting("goodbye_image", self.guild_id)
        
        config_text = ""
        if goodbye_channel_id:
            config_text += f"**Channel:** <#{goodbye_channel_id}>\n"
        else:
            config_text += "**Channel:** Not configured\n"
            
        if goodbye_title:
            config_text += f"**Title:** {goodbye_title}\n"
        else:
            config_text += "**Title:** Not set\n"
            
        if goodbye_message:
            msg_preview = goodbye_message[:50] + "..." if len(goodbye_message) > 50 else goodbye_message
            config_text += f"**Message:** {msg_preview}\n"
        else:
            config_text += "**Message:** Not set\n"
            
        if goodbye_image:
            config_text += f"**Image:** {goodbye_image}\n"
        else:
            config_text += "**Image:** Not set\n"
            
        config_text += f"**Status:** {'✅ Enabled' if goodbye_enabled == 'true' else '❌ Disabled'}\n"
        
        embed = discord.Embed(
            title="📋 Goodbye System Configuration",
            description=config_text,
            color=COLORS["error"],
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="Back to Welcome", style=ButtonStyle.secondary, emoji="◀️", row=1
    )
    async def back_to_welcome(self, interaction: discord.Interaction, button: Button):
        """Navigate back to welcome system setup"""
        embed = discord.Embed(
            title="👋 Welcome System Setup",
            description=(
                "Configure your welcome and goodbye systems:\n\n"
                "**Available Variables:**\n"
                "`{member}` - Mentions the new member\n"
                "`{member.name}` - Member's username\n"
                "`{server}` - Server name\n"
                "`{member.count}` - Total member count\n\n"
                "Click the buttons below to configure welcome settings.\n"
                "Use the **Goodbye System** button to configure goodbye messages."
            ),
            color=COLORS["welcome"],
        )

        view = WelcomeSetupView(self.guild_id, self.db_manager)
        await interaction.response.edit_message(embed=embed, view=view)


class BirthdaySetupView(View):
    def __init__(self, guild_id: int, db_manager):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.db_manager = db_manager

    @discord.ui.button(label="Set Channel", style=ButtonStyle.primary, emoji="📢")
    async def set_channel(self, interaction: discord.Interaction, button: Button):
        """Set birthday announcement channel"""
        # Defer immediately to prevent timeout
        await interaction.response.defer(ephemeral=True)

        view = View()
        select = discord.ui.ChannelSelect(
            placeholder="Select birthday announcement channel",
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1,
        )

        async def channel_callback(interaction: discord.Interaction):
            channel = select.values[0]
            await self.db_manager.set_setting(
                "birthday_channel", str(channel.id), self.guild_id
            )
            embed = discord.Embed(
                title="✅ Birthday Channel Set",
                description=f"Birthday announcements will be sent to {channel.mention}",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        select.callback = channel_callback
        view.add_item(select)

        embed = discord.Embed(
            title="📢 Select Birthday Channel",
            description="Choose the channel where birthday announcements will be sent.",
            color=COLORS["primary"],
        )
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Set Time", style=ButtonStyle.primary, emoji="⏰")
    async def set_time(self, interaction: discord.Interaction, button: Button):
        """Set birthday announcement time"""
        modal = Modal(title="Set Birthday Announcement Time")
        time_input = discord.ui.TextInput(
            label="Announcement Time (24-hour format)",
            placeholder="08:00",
            style=discord.TextStyle.short,
            required=True,
            max_length=5,
        )
        modal.add_item(time_input)

        async def modal_callback(interaction: discord.Interaction):
            # Validate time format
            try:
                hour, minute = time_input.value.split(":")
                hour = int(hour)
                minute = int(minute)
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError

                await self.db_manager.set_setting(
                    "birthday_time", time_input.value, self.guild_id
                )
                embed = discord.Embed(
                    title="✅ Birthday Time Set",
                    description=f"Announcements will be posted at {time_input.value} (server timezone)",
                    color=COLORS["success"],
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except ValueError:
                embed = discord.Embed(
                    title="❌ Invalid Time Format",
                    description="Please use 24-hour format (HH:MM), e.g., 08:00 or 14:30",
                    color=COLORS["error"],
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Set Message", style=ButtonStyle.primary, emoji="💬")
    async def set_message(self, interaction: discord.Interaction, button: Button):
        """Set birthday message"""
        modal = Modal(title="Set Birthday Message")
        message_input = discord.ui.TextInput(
            label="Birthday Message",
            default="🎂 Happy Birthday {member}! Have a great day!",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500,
        )
        modal.add_item(message_input)

        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting(
                "birthday_message", message_input.value, self.guild_id
            )
            embed = discord.Embed(
                title="✅ Birthday Message Set",
                description=f"Message: {message_input.value}",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Toggle Announcements", style=ButtonStyle.success, emoji="🔄", row=1)
    async def toggle_birthday_announcements(self, interaction: discord.Interaction, button: Button):
        """Toggle birthday announcements on/off"""
        current = await self.db_manager.get_setting("birthday_announcements_enabled", self.guild_id)
        new_state = "false" if current == "true" else "true"
        
        await self.db_manager.set_setting("birthday_announcements_enabled", new_state, self.guild_id)
        
        status = "✅ Enabled" if new_state == "true" else "❌ Disabled"
        embed = discord.Embed(
            title=f"Birthday Announcements {status}",
            description=f"System is now **{status.split()[1]}**",
            color=COLORS["success"] if new_state == "true" else COLORS["error"],
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Birthday Pending", style=ButtonStyle.secondary, emoji="🎯", row=1)
    async def birthday_pending_settings(self, interaction: discord.Interaction, button: Button):
        """Configure Birthday Pending system"""
        await interaction.response.defer(ephemeral=True)
        
        view = BirthdayPendingSetupView(self.guild_id, self.db_manager)
        
        enabled = await self.db_manager.get_setting("birthday_pending_enabled", self.guild_id)
        pending_role_id = await self.db_manager.get_setting("birthday_pending_role", self.guild_id)
        reminder_channel_id = await self.db_manager.get_setting("birthday_reminder_channel", self.guild_id)
        
        status = "✅ Enabled" if enabled == "true" else "❌ Disabled"
        role_text = f"<@&amp;{pending_role_id}>" if pending_role_id else "Not set"
        channel_text = f"<#{reminder_channel_id}>" if reminder_channel_id else "Not set"
        
        embed = discord.Embed(
            title="🎯 Birthday Pending System",
            description=(
                "Configure the Birthday Pending system.\n\n"
                f"**Status:** {status}\n"
                f"**Pending Role:** {role_text}\n"
                f"**Reminder Channel:** {channel_text}"
            ),
            color=COLORS["primary"],
        )
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

# Code to insert into BirthdaySetupView class in cogs/setup.py
# Insert this BEFORE the "View Config" button

    @discord.ui.button(label="Set Birthday XP", style=ButtonStyle.primary, emoji="⭐", row=1)
    async def set_birthday_xp(self, interaction: discord.Interaction, button: Button):
        """Set XP reward for setting birthday"""
        modal = Modal(title="Set Birthday XP Reward")
        xp_input = discord.ui.TextInput(
            label="XP Amount (0 to disable)",
            placeholder="50",
            style=discord.TextStyle.short,
            required=True,
            max_length=5,
        )
        modal.add_item(xp_input)

        async def modal_callback(interaction: discord.Interaction):
            try:
                xp_amount = int(xp_input.value)
                if xp_amount < 0:
                    raise ValueError("XP amount cannot be negative")
                
                if xp_amount == 0:
                    # Disable XP reward
                    await self.db_manager.set_setting("birthday_set_xp", "", self.guild_id)
                    embed = discord.Embed(
                        title="✅ Birthday XP Disabled",
                        description="Users will no longer receive XP for setting their birthday.",
                        color=COLORS["success"],
                    )
                else:
                    await self.db_manager.set_setting("birthday_set_xp", str(xp_amount), self.guild_id)
                    embed = discord.Embed(
                        title="✅ Birthday XP Set",
                        description=f"Users will receive **{xp_amount} XP** when they set their birthday for the first time.",
                        color=COLORS["success"],
                    )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except ValueError:
                embed = discord.Embed(
                    title="❌ Invalid XP Amount",
                    description="Please enter a valid number (0 or positive integer).",
                    color=COLORS["error"],
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)
    @discord.ui.button(label="View Config", style=ButtonStyle.secondary, emoji="📋", row=2)
    async def view_birthday_config(self, interaction: discord.Interaction, button: Button):
        """View current birthday configuration"""
        birthday_channel_id = await self.db_manager.get_setting("birthday_channel", self.guild_id)
        birthday_time = await self.db_manager.get_setting("birthday_time", self.guild_id)
        birthday_message = await self.db_manager.get_setting("birthday_message", self.guild_id)
        birthday_xp = await self.db_manager.get_setting("birthday_set_xp", self.guild_id)
        pending_enabled = await self.db_manager.get_setting("birthday_pending_enabled", self.guild_id)
        pending_role_id = await self.db_manager.get_setting("birthday_pending_role", self.guild_id)
        reminder_channel_id = await self.db_manager.get_setting("birthday_reminder_channel", self.guild_id)
        
        config_text = "**Birthday Announcements:**\n"
        config_text += f"Channel: <#{birthday_channel_id}>\n" if birthday_channel_id else "Channel: Not set\n"
        config_text += f"Time: {birthday_time}\n" if birthday_time else "Time: Not set\n"
        
        if birthday_message:
            msg_preview = birthday_message[:50] + "..." if len(birthday_message) > 50 else birthday_message
            config_text += f"Message: {msg_preview}\n"
        else:
            config_text += "Message: Not set\n"
        
        config_text += "\n**Birthday Rewards:**\n"
        if birthday_xp:
            config_text += f"XP Reward: {birthday_xp} XP (one-time)\n"
        else:
            config_text += "XP Reward: Not set (disabled)\n"
        
        config_text += "\n**Birthday Pending:**\n"
        config_text += f"Status: {'✅ Enabled' if pending_enabled == 'true' else '❌ Disabled'}\n"
        config_text += f"Role: <@&amp;{pending_role_id}>\n" if pending_role_id else "Role: Not set\n"
        config_text += f"Channel: <#{reminder_channel_id}>\n" if reminder_channel_id else "Channel: Not set\n"
        
        embed = discord.Embed(
            title="📋 Birthday Configuration",
            description=config_text,
            color=COLORS["info"],
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class BirthdayPendingSetupView(View):
    """View for Birthday Pending system configuration"""
    
    def __init__(self, guild_id: int, db_manager):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.db_manager = db_manager
    
    @discord.ui.button(label="Toggle System", style=ButtonStyle.success, emoji="🔄")
    async def toggle_system(self, interaction: discord.Interaction, button: Button):
        """Toggle Birthday Pending system"""
        current = await self.db_manager.get_setting("birthday_pending_enabled", self.guild_id)
        new_state = "false" if current == "true" else "true"
        
        await self.db_manager.set_setting("birthday_pending_enabled", new_state, self.guild_id)
        
        if new_state == "true":
            pending_role_id = await self.db_manager.get_setting("birthday_pending_role", self.guild_id)
            if pending_role_id:
                role_conn_cog = interaction.client.get_cog("RoleConnections")
                if role_conn_cog:
                    await role_conn_cog.manager.add_protected_role(self.guild_id, int(pending_role_id))
        
        status = "✅ Enabled" if new_state == "true" else "❌ Disabled"
        embed = discord.Embed(
            title=f"Birthday Pending {status}",
            description=f"System is now **{status.split()[1]}**",
            color=COLORS["success"] if new_state == "true" else COLORS["error"],
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="Set Role", style=ButtonStyle.primary, emoji="🎭")
    async def set_pending_role(self, interaction: discord.Interaction, button: Button):
        """Set Birthday Pending role"""
        await interaction.response.defer(ephemeral=True)
        
        view = View()
        select = discord.ui.RoleSelect(placeholder="Select role", min_values=1, max_values=1)
        
        async def role_callback(interaction: discord.Interaction):
            role = select.values[0]
            await self.db_manager.set_setting("birthday_pending_role", str(role.id), self.guild_id)
            
            enabled = await self.db_manager.get_setting("birthday_pending_enabled", self.guild_id)
            if enabled == "true":
                role_conn_cog = interaction.client.get_cog("RoleConnections")
                if role_conn_cog:
                    await role_conn_cog.manager.add_protected_role(self.guild_id, role.id)
            
            embed = discord.Embed(
                title="✅ Role Set",
                description=f"Birthday Pending role: {role.mention}",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        select.callback = role_callback
        view.add_item(select)
        
        embed = discord.Embed(title="🎭 Select Role", color=COLORS["primary"])
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Set Channel", style=ButtonStyle.primary, emoji="📢")
    async def set_reminder_channel(self, interaction: discord.Interaction, button: Button):
        """Set reminder channel"""
        await interaction.response.defer(ephemeral=True)
        
        view = View()
        select = discord.ui.ChannelSelect(
            placeholder="Select channel",
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1,
        )
        
        async def channel_callback(interaction: discord.Interaction):
            channel = select.values[0]
            await self.db_manager.set_setting("birthday_reminder_channel", str(channel.id), self.guild_id)
            
            embed = discord.Embed(
                title="✅ Channel Set",
                description=f"Reminder channel: {channel.mention}",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        select.callback = channel_callback
        view.add_item(select)
        
        embed = discord.Embed(title="📢 Select Channel", color=COLORS["primary"])
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Setup Message", style=ButtonStyle.success, emoji="📝", row=1)
    async def setup_reminder_message(self, interaction: discord.Interaction, button: Button):
        """Setup persistent reminder message"""
        await interaction.response.defer(ephemeral=True)
        
        reminder_channel_id = await self.db_manager.get_setting("birthday_reminder_channel", self.guild_id)
        
        if not reminder_channel_id:
            embed = discord.Embed(
                title="❌ No Channel Set",
                description="Set a reminder channel first.",
                color=COLORS["error"],
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        channel = interaction.guild.get_channel(int(reminder_channel_id))
        if not channel:
            embed = discord.Embed(
                title="❌ Channel Not Found",
                color=COLORS["error"],
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        birthdays_cog = interaction.client.get_cog("Birthdays")
        if not birthdays_cog:
            embed = discord.Embed(
                title="❌ Cog Not Loaded",
                color=COLORS["error"],
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        try:
            await birthdays_cog.setup_birthday_reminder_message(self.guild_id, channel)
            
            embed = discord.Embed(
                title="✅ Setup Complete",
                description=f"Message posted in {channel.mention}",
                color=COLORS["success"],
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Setup Failed",
                description=str(e),
                color=COLORS["error"],
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="View Config", style=ButtonStyle.secondary, emoji="📋", row=2)
    async def view_birthday_pending_config(self, interaction: discord.Interaction, button: Button):
        """View current Birthday Pending system configuration"""
        enabled = await self.db_manager.get_setting("birthday_pending_enabled", self.guild_id)
        pending_role_id = await self.db_manager.get_setting("birthday_pending_role", self.guild_id)
        reminder_channel_id = await self.db_manager.get_setting("birthday_reminder_channel", self.guild_id)
        reminder_message_id = await self.db_manager.get_setting("birthday_reminder_message_id", self.guild_id)
        
        config_text = f"**Status:** {'✅ Enabled' if enabled == 'true' else '❌ Disabled'}\n"
        
        if pending_role_id:
            config_text += f"**Pending Role:** <@&{pending_role_id}>\n"
        else:
            config_text += "**Pending Role:** Not set\n"
            
        if reminder_channel_id:
            config_text += f"**Reminder Channel:** <#{reminder_channel_id}>\n"
        else:
            config_text += "**Reminder Channel:** Not set\n"
            
        if reminder_message_id:
            config_text += f"**Reminder Message:** Configured (ID: {reminder_message_id})\n"
        else:
            config_text += "**Reminder Message:** Not configured\n"
        
        embed = discord.Embed(
            title="📋 Birthday Pending System Configuration",
            description=config_text,
            color=COLORS["primary"],
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class LevelRolesView(View):
    def __init__(self, guild_id: int, db_manager):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.db_manager = db_manager

    @discord.ui.button(label="Add Level Role", style=ButtonStyle.success, emoji="➕")
    async def add_level_role(self, interaction: discord.Interaction, button: Button):
        """Add a level role reward"""
        modal = Modal(title="Add Level Role")

        level_input = discord.ui.TextInput(
            label="Level",
            placeholder="10",
            style=discord.TextStyle.short,
            required=True,
            max_length=3,
        )
        modal.add_item(level_input)

        role_input = discord.ui.TextInput(
            label="Role ID or Name",
            placeholder="Role ID or exact role name",
            style=discord.TextStyle.short,
            required=True,
            max_length=100,
        )
        modal.add_item(role_input)

        async def modal_callback(interaction: discord.Interaction):
            try:
                level = int(level_input.value)

                if level < 1:
                    raise ValueError("Level must be 1 or higher")

                # Try to find role by ID first, then by name
                role = None
                try:
                    role_id = int(role_input.value)
                    role = interaction.guild.get_role(role_id)
                except ValueError:
                    # Not an ID, search by name
                    role = discord.utils.get(
                        interaction.guild.roles, name=role_input.value
                    )

                if not role:
                    embed = discord.Embed(
                        title="❌ Role Not Found",
                        description=f"Could not find role: {role_input.value}",
                        color=COLORS["error"],
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

                # Save directly to level_roles table
                try:
                    conn = await self.db_manager.get_connection()
                    log_system(f"Saving level role: guild={self.guild_id}, level={level}, role_id={role.id}")
                    await conn.execute(
                        """
                        INSERT OR REPLACE INTO level_roles (guild_id, level, role_id)
                        VALUES (?, ?, ?)
                        """,
                        (self.guild_id, level, role.id)
                    )
                    await conn.commit()
                    log_system(f"Level role saved successfully!")
                except Exception as save_error:
                    log_system(f"Failed to save level role: {save_error}", level="error")
                    raise


                embed = discord.Embed(
                    title="✅ Level Role Added",
                    description=f"Users will receive {role.mention} when they reach **Level {level}**",
                    color=COLORS["success"],
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

            except ValueError as e:
                embed = discord.Embed(
                    title="❌ Invalid Input", description=str(e), color=COLORS["error"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Remove Level Role", style=ButtonStyle.danger, emoji="➖")
    async def remove_level_role(self, interaction: discord.Interaction, button: Button):
        """Remove a level role reward"""
        modal = Modal(title="Remove Level Role")

        level_input = discord.ui.TextInput(
            label="Level",
            placeholder="10",
            style=discord.TextStyle.short,
            required=True,
            max_length=3,
        )
        modal.add_item(level_input)

        async def modal_callback(interaction: discord.Interaction):
            try:
                level = int(level_input.value)

                # Get current level roles
                level_roles = await self.db_manager.get_setting(
                    "level_roles", self.guild_id
                )

                if not level_roles:
                    embed = discord.Embed(
                        title="❌ No Level Roles",
                        description="There are no level roles configured.",
                        color=COLORS["error"],
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

                # Parse and remove
                roles_dict = {}
                for entry in level_roles.split(","):
                    if ":" in entry:
                        lvl, rid = entry.split(":")
                        roles_dict[int(lvl)] = rid

                if level not in roles_dict:
                    embed = discord.Embed(
                        title="❌ Level Not Found",
                        description=f"No role configured for Level {level}",
                        color=COLORS["error"],
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

                # Remove the level
                del roles_dict[level]

                # Save back
                if roles_dict:
                    new_level_roles = ",".join(
                        [f"{lvl}:{rid}" for lvl, rid in sorted(roles_dict.items())]
                    )
                    await self.db_manager.set_setting(
                        "level_roles", new_level_roles, self.guild_id
                    )
                else:
                    # No roles left, delete the setting
                    await self.db_manager.set_setting("level_roles", "", self.guild_id)

                embed = discord.Embed(
                    title="✅ Level Role Removed",
                    description=f"Removed role reward for Level {level}",
                    color=COLORS["success"],
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

            except ValueError:
                embed = discord.Embed(
                    title="❌ Invalid Level",
                    description="Please enter a valid level number.",
                    color=COLORS["error"],
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="View Config", style=ButtonStyle.secondary, emoji="📋")
    async def view_level_roles_config(self, interaction: discord.Interaction, button: Button):
        """View current level roles configuration"""
        level_roles_setting = await self.db_manager.get_setting("level_roles", self.guild_id)
        
        if not level_roles_setting:
            embed = discord.Embed(
                title="📋 Level Roles Configuration",
                description="**No level roles configured**\n\nUse the 'Add Level Role' button to add role rewards for specific levels.",
                color=COLORS["info"],
            )
        else:
            # Parse the level roles
            roles = {}
            for role_pair in level_roles_setting.split(","):
                if ":" in role_pair:
                    level, role_id = role_pair.split(":")
                    roles[int(level)] = role_id
            
            # Sort by level
            sorted_roles = sorted(roles.items())
            
            config_text = "**Current Level Roles:**\n\n"
            for level, role_id in sorted_roles:
                role = discord.utils.get(interaction.guild.roles, id=int(role_id))
                if role:
                    config_text += f"Level {level}: {role.mention}\n"
                else:
                    config_text += f"Level {level}: (Invalid role ID: {role_id})\n"
            
            embed = discord.Embed(
                title="📋 Level Roles Configuration",
                description=config_text,
                color=COLORS["info"],
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Back to XP Setup", style=ButtonStyle.secondary, emoji="◀️")
    async def back_button(self, interaction: discord.Interaction, button: Button):
        """Go back to XP setup"""
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title="🏆 XP System Setup",
            description="Configure the XP and leveling system for your server.",
            color=COLORS["primary"],
        )

        view = XPSetupView(self.guild_id, self.db_manager)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


class XPSetupView(View):
    def __init__(self, guild_id: int, db_manager):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.db_manager = db_manager

    @discord.ui.button(
        label="Set Level-up Channel", style=ButtonStyle.primary, emoji="📢"
    )
    async def set_channel(self, interaction: discord.Interaction, button: Button):
        """Set level-up announcement channel"""
        # Defer immediately to prevent timeout
        await interaction.response.defer(ephemeral=True)

        view = View()
        select = discord.ui.ChannelSelect(
            placeholder="Select level-up announcement channel",
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1,
        )

        async def channel_callback(interaction: discord.Interaction):
            channel = select.values[0]
            await self.db_manager.set_setting(
                "xp_channel", str(channel.id), self.guild_id
            )
            embed = discord.Embed(
                title="✅ Level-up Channel Set",
                description=f"Level-up announcements will be sent to {channel.mention}",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        select.callback = channel_callback
        view.add_item(select)

        embed = discord.Embed(
            title="📢 Select Level-up Channel",
            description="Choose the channel where level-up announcements will be sent.",
            color=COLORS["primary"],
        )
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Message XP", style=ButtonStyle.primary, emoji="💬")
    async def set_message_xp(self, interaction: discord.Interaction, button: Button):
        """Set XP per message"""
        modal = Modal(title="Set Message XP")
        xp_input = discord.ui.TextInput(
            label="XP per message",
            placeholder="10",
            style=discord.TextStyle.short,
            required=True,
            max_length=3,
        )
        modal.add_item(xp_input)

        async def modal_callback(interaction: discord.Interaction):
            try:
                xp_val = int(xp_input.value)

                if xp_val < 1:
                    raise ValueError

                await self.db_manager.set_setting(
                    "xp_per_message", str(xp_val), self.guild_id
                )

                embed = discord.Embed(
                    title="✅ Message XP Set",
                    description=f"Users will gain {xp_val} XP per message",
                    color=COLORS["success"],
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except ValueError:
                embed = discord.Embed(
                    title="❌ Invalid Value",
                    description="Please enter a valid number (minimum 1).",
                    color=COLORS["error"],
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Reaction XP", style=ButtonStyle.primary, emoji="👍")
    async def set_reaction_xp(self, interaction: discord.Interaction, button: Button):
        """Set XP per reaction received"""
        modal = Modal(title="Set Reaction XP")
        xp_input = discord.ui.TextInput(
            label="XP per reaction received",
            placeholder="2",
            style=discord.TextStyle.short,
            required=True,
            max_length=3,
        )
        modal.add_item(xp_input)

        async def modal_callback(interaction: discord.Interaction):
            try:
                xp_val = int(xp_input.value)

                if xp_val < 0:
                    raise ValueError

                await self.db_manager.set_setting(
                    "xp_per_reaction", str(xp_val), self.guild_id
                )

                embed = discord.Embed(
                    title="✅ Reaction XP Set",
                    description=f"Users will gain {xp_val} XP per reaction received (0 to disable)",
                    color=COLORS["success"],
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except ValueError:
                embed = discord.Embed(
                    title="❌ Invalid Value",
                    description="Please enter a valid number (0 or higher).",
                    color=COLORS["error"],
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Voice XP", style=ButtonStyle.primary, emoji="🎤")
    async def set_voice_xp(self, interaction: discord.Interaction, button: Button):
        """Set XP per minute in voice chat"""
        modal = Modal(title="Set Voice XP")
        xp_input = discord.ui.TextInput(
            label="XP per minute in voice",
            placeholder="5",
            style=discord.TextStyle.short,
            required=True,
            max_length=3,
        )
        modal.add_item(xp_input)

        async def modal_callback(interaction: discord.Interaction):
            try:
                xp_val = int(xp_input.value)

                if xp_val < 0:
                    raise ValueError

                await self.db_manager.set_setting(
                    "xp_per_voice_minute", str(xp_val), self.guild_id
                )

                embed = discord.Embed(
                    title="✅ Voice XP Set",
                    description=f"Users will gain {xp_val} XP per minute in voice (0 to disable)",
                    color=COLORS["success"],
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except ValueError:
                embed = discord.Embed(
                    title="❌ Invalid Value",
                    description="Please enter a valid number (0 or higher).",
                    color=COLORS["error"],
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="XP Cooldown", style=ButtonStyle.primary, emoji="⏱️", row=1)
    async def set_xp_cooldown(self, interaction: discord.Interaction, button: Button):
        """Set cooldown between XP gains"""
        modal = Modal(title="Set XP Cooldown")
        cooldown_input = discord.ui.TextInput(
            label="Cooldown in seconds",
            placeholder="60",
            style=discord.TextStyle.short,
            required=True,
            max_length=4,
        )
        modal.add_item(cooldown_input)

        async def modal_callback(interaction: discord.Interaction):
            try:
                cooldown_val = int(cooldown_input.value)

                if cooldown_val < 0:
                    raise ValueError

                await self.db_manager.set_setting(
                    "xp_cooldown", str(cooldown_val), self.guild_id
                )

                embed = discord.Embed(
                    title="✅ XP Cooldown Set",
                    description=f"Users must wait {cooldown_val} seconds between XP gains",
                    color=COLORS["success"],
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except ValueError:
                embed = discord.Embed(
                    title="❌ Invalid Value",
                    description="Please enter a valid number (0 or higher).",
                    color=COLORS["error"],
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)

    @discord.ui.button(
        label="XP Progression Type", style=ButtonStyle.primary, emoji="⚙️", row=1
    )
    async def set_progression(self, interaction: discord.Interaction, button: Button):
        """Set XP progression type"""
        view = View(timeout=60)
        
        select = Select(
            placeholder="Choose XP progression type...",
            options=[
                discord.SelectOption(
                    label="Linear (100 XP per level)",
                    value="basic",
                    description="Steady: Level 10=1,000 XP, Level 50=5,000 XP, Level 100=10,000 XP",
                    emoji="📊"
                ),
                discord.SelectOption(
                    label="Exponential (Gets harder fast)",
                    value="gradual",
                    description="Steep: Level 10=5,500 XP, Level 50=127,500 XP, Level 100=505,000 XP",
                    emoji="📈"
                ),
                discord.SelectOption(
                    label="Hybrid (Linear → Exponential)",
                    value="custom",
                    description="Balanced: Easy start, harder later. Level 10=1,900 XP, Level 50=160,000 XP",
                    emoji="🎯"
                )
            ]
        )
        
        async def progression_callback(interaction: discord.Interaction):
            progression_type = select.values[0]
            await self.db_manager.set_setting("xp_progression_type", progression_type, self.guild_id)
            
            type_names = {
                "basic": "Linear (100 XP per level)",
                "gradual": "Exponential (Gets harder fast)",
                "custom": "Hybrid (Linear → Exponential)"
            }
            
            embed = discord.Embed(
                title="✅ XP Progression Set",
                description=f"XP progression type set to: **{type_names[progression_type]}**",
                color=COLORS["success"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        select.callback = progression_callback
        view.add_item(select)
        
        embed = discord.Embed(
            title="⚙️ Select XP Progression Type",
            description=(
                "**📊 Linear:** 100 XP per level (predictable, steady growth)\n"
                "• Level 10 = 1,000 XP\n"
                "• Level 50 = 5,000 XP\n"
                "• Level 100 = 10,000 XP\n"
                "• Best for: Casual servers, easy to understand\n\n"
                "**📈 Exponential:** Gets much harder each level\n"
                "• Level 10 = 5,500 XP\n"
                "• Level 50 = 127,500 XP\n"
                "• Level 100 = 505,000 XP\n"
                "• Best for: Competitive servers, long-term engagement\n\n"
                "**🎯 Hybrid:** Starts easy, becomes exponential\n"
                "• Level 10 = 1,900 XP (easy early levels)\n"
                "• Level 20 = 15,000 XP (moderate)\n"
                "• Level 50 = 160,000 XP (challenging)\n"
                "• Best for: Balanced progression, rewards dedication\n\n"
                "Choose the progression that fits your server!"
            ),
            color=COLORS["primary"]
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(
        label="Manage Level Roles", style=ButtonStyle.secondary, emoji="🎭", row=2
    )
    async def manage_level_roles(
        self, interaction: discord.Interaction, button: Button
    ):
        """Manage level role rewards"""
        await interaction.response.defer(ephemeral=True)

        # Get current level roles from database table
        rows = await self.db_manager.get_level_roles(self.guild_id)

        # Build description
        if rows:
            description = "**Current Level Roles:**\n\n"
            for level, role_id in rows:
                role = interaction.guild.get_role(int(role_id))
                if role:
                    description += f"Level {level}: {role.mention}\n"
        else:
            description = "No level roles configured yet.\n\n"

        description += "\n**Actions:**\n• Add Level Role - Assign a role at a specific level\n• Remove Level Role - Remove a level role reward\n• Back - Return to XP setup"

        embed = discord.Embed(
            title="🎭 Manage Level Roles",
            description=description,
            color=COLORS["primary"],
        )

        view = LevelRolesView(self.guild_id, self.db_manager)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(
        label="Toggle Message XP", style=ButtonStyle.secondary, emoji="💬", row=1
    )
    async def toggle_message_xp(self, interaction: discord.Interaction, button: Button):
        """Toggle message XP on/off"""
        current = await self.db_manager.get_setting("xp_message_enabled", self.guild_id)
        
        if current == "false":
            new_state = "true"
        else:
            new_state = "false"
            
        await self.db_manager.set_setting("xp_message_enabled", new_state, self.guild_id)
        
        status = "✅ Enabled" if new_state == "true" else "❌ Disabled"
        embed = discord.Embed(
            title=f"Message XP {status}",
            description=f"Message XP is now **{status.split()[1]}**",
            color=COLORS["success"] if new_state == "true" else COLORS["error"],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="Toggle Reaction XP", style=ButtonStyle.secondary, emoji="👍", row=1
    )
    async def toggle_reaction_xp(self, interaction: discord.Interaction, button: Button):
        """Toggle reaction XP on/off"""
        current = await self.db_manager.get_setting("xp_reaction_enabled", self.guild_id)
        
        if current == "false":
            new_state = "true"
        else:
            new_state = "false"
            
        await self.db_manager.set_setting("xp_reaction_enabled", new_state, self.guild_id)
        
        status = "✅ Enabled" if new_state == "true" else "❌ Disabled"
        embed = discord.Embed(
            title=f"Reaction XP {status}",
            description=f"Reaction XP is now **{status.split()[1]}**",
            color=COLORS["success"] if new_state == "true" else COLORS["error"],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="Toggle Voice XP", style=ButtonStyle.secondary, emoji="🎙️", row=2
    )
    async def toggle_voice_xp(self, interaction: discord.Interaction, button: Button):
        """Toggle voice XP on/off"""
        current = await self.db_manager.get_setting("xp_voice_enabled", self.guild_id)
        
        if current == "false":
            new_state = "true"
        else:
            new_state = "false"
            
        await self.db_manager.set_setting("xp_voice_enabled", new_state, self.guild_id)
        
        status = "✅ Enabled" if new_state == "true" else "❌ Disabled"
        embed = discord.Embed(
            title=f"Voice XP {status}",
            description=f"Voice XP is now **{status.split()[1]}**",
            color=COLORS["success"] if new_state == "true" else COLORS["error"],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="View Config", style=ButtonStyle.secondary, emoji="📋", row=2)
    async def view_xp_config(self, interaction: discord.Interaction, button: Button):
        """View current XP system configuration"""
        xp_channel_id = await self.db_manager.get_setting("xp_channel", self.guild_id)
        xp_per_message = await self.db_manager.get_setting("xp_per_message", self.guild_id)
        xp_per_reaction = await self.db_manager.get_setting("xp_per_reaction", self.guild_id)
        xp_per_voice = await self.db_manager.get_setting("xp_per_voice_minute", self.guild_id)
        xp_cooldown = await self.db_manager.get_setting("xp_cooldown", self.guild_id)
        message_enabled = await self.db_manager.get_setting("xp_message_enabled", self.guild_id)
        reaction_enabled = await self.db_manager.get_setting("xp_reaction_enabled", self.guild_id)
        voice_enabled = await self.db_manager.get_setting("xp_voice_enabled", self.guild_id)
        
        config_text = "**Toggles:**\n"
        config_text += f"Message XP: {'✅ Enabled' if message_enabled == 'true' else '❌ Disabled'}\n"
        config_text += f"Reaction XP: {'✅ Enabled' if reaction_enabled == 'true' else '❌ Disabled'}\n"
        config_text += f"Voice XP: {'✅ Enabled' if voice_enabled == 'true' else '❌ Disabled'}\n\n"
        
        config_text += "**Settings:**\n"
        if xp_channel_id:
            config_text += f"Level-up Channel: <#{xp_channel_id}>\n"
        else:
            config_text += "Level-up Channel: Not set\n"
            
        if xp_per_message:
            config_text += f"XP per Message: {xp_per_message}\n"
        else:
            config_text += "XP per Message: Not set\n"
            
        if xp_per_reaction:
            config_text += f"XP per Reaction: {xp_per_reaction}\n"
        else:
            config_text += "XP per Reaction: Not set\n"
            
        if xp_per_voice:
            config_text += f"XP per Voice Minute: {xp_per_voice}\n"
        else:
            config_text += "XP per Voice Minute: Not set\n"
            
        if xp_cooldown:
            config_text += f"XP Cooldown: {xp_cooldown}s\n"
        else:
            config_text += "XP Cooldown: Not set\n"
        
        embed = discord.Embed(
            title="📋 XP System Configuration",
            description=config_text,
            color=COLORS["primary"],
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db_manager

    @app_commands.command(
        name="setup", description="Configure bot settings (Server Owner only)"
    )
    async def setup(self, interaction: discord.Interaction):
        """Main setup command with interactive menu"""
        # Check if user is server owner BEFORE any async operations
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

    @app_commands.command(
        name="sync_onboarding",
        description="Assign onboarding role to all pending members (Server Owner only)"
    )
    async def sync_onboarding(self, interaction: discord.Interaction):
        """Sync onboarding role to all pending members"""
        if interaction.guild.owner_id != interaction.user.id:
            embed = discord.Embed(
                title="🚫 Permission Denied",
                description="This command is only available to the server owner.",
                color=COLORS["error"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        onboarding_role_id = await self.db.get_setting("onboarding_role", interaction.guild.id)
        
        if not onboarding_role_id:
            embed = discord.Embed(
                title="❌ No Onboarding Role Set",
                description="Please set an onboarding role first using `/setup` → General Settings → Set Onboarding Role",
                color=COLORS["error"],
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        onboarding_role = interaction.guild.get_role(int(onboarding_role_id))
        
        if not onboarding_role:
            embed = discord.Embed(
                title="❌ Onboarding Role Not Found",
                description=f"The configured onboarding role (ID: {onboarding_role_id}) no longer exists.",
                color=COLORS["error"],
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Find all pending members
        pending_members = [m for m in interaction.guild.members if m.pending and not m.bot]
        
        if not pending_members:
            embed = discord.Embed(
                title="✅ No Pending Members",
                description="There are no members currently completing onboarding.",
                color=COLORS["success"],
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Assign role to pending members
        success_count = 0
        fail_count = 0
        
        for member in pending_members:
            if onboarding_role not in member.roles:
                try:
                    await member.add_roles(onboarding_role, reason="Onboarding sync")
                    success_count += 1
                except discord.Forbidden:
                    fail_count += 1
                except Exception as e:
                    log_system(f"Error assigning onboarding role to {member.name}: {e}", level="error")
                    fail_count += 1

        embed = discord.Embed(
            title="✅ Onboarding Sync Complete",
            description=(
                f"**Assigned {onboarding_role.mention} to {success_count} pending member(s)**\n\n"
                f"✅ Success: {success_count}\n"
                f"❌ Failed: {fail_count}\n\n"
                f"Total pending members: {len(pending_members)}"
            ),
            color=COLORS["success"],
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    setup_cog = Setup(bot)
    await bot.add_cog(setup_cog)
    # Commands are automatically registered when cog is loaded
