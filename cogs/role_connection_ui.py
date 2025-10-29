"""
Role Connection UI Components
Supporting views and modals for role connection management
"""

import discord
from discord.ui import View, Select, Button, Modal, TextInput, RoleSelect
from utils.embed_builder import create_embed, COLORS
from utils.logger import log_system


class AddConnectionView(View):
    """View for adding a new role connection"""
    def __init__(self, manager, guild: discord.Guild):
        super().__init__(timeout=300)
        self.manager = manager
        self.guild = guild
        self.target_role = None
        self.action = None
        self.conditions = []
        self.logic = "AND"
        
        # Add role selector
        self.add_item(AddConnectionRoleSelect(self))

class AddConnectionRoleSelect(RoleSelect):
    """Select target role for connection"""
    def __init__(self, parent_view):
        super().__init__(
            placeholder="Select target role...",
            min_values=1,
            max_values=1
        )
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        self.parent_view.target_role = self.values[0]
        
        # Move to action selection
        view = SelectActionView(self.parent_view.manager, self.parent_view.guild, self.parent_view.target_role)
        
        embed = discord.Embed(
            title="➕ Add Role Connection",
            description=f"**Step 2: Select Action**\n\nTarget Role: {self.parent_view.target_role.mention}\n\nWhat should happen with this role?",
            color=COLORS["primary"]
        )
        
        await interaction.response.edit_message(embed=embed, view=view)


class SelectActionView(View):
    """View for selecting give/remove action"""
    def __init__(self, manager, guild: discord.Guild, target_role: discord.Role):
        super().__init__(timeout=300)
        self.manager = manager
        self.guild = guild
        self.target_role = target_role
        self.conditions = []
        self.logic = "AND"

    @discord.ui.button(label="Give Role", style=discord.ButtonStyle.green, emoji="➕")
    async def give_role(self, interaction: discord.Interaction, button: Button):
        await self.select_conditions(interaction, "give")

    @discord.ui.button(label="Remove Role", style=discord.ButtonStyle.red, emoji="➖")
    async def remove_role(self, interaction: discord.Interaction, button: Button):
        await self.select_conditions(interaction, "remove")

    async def select_conditions(self, interaction: discord.Interaction, action: str):
        """Move to condition selection"""
        view = AddConditionView(self.manager, self.guild, self.target_role, action)
        
        embed = discord.Embed(
            title="➕ Add Role Connection",
            description=(
                f"**Step 3: Add Conditions**\n\n"
                f"Target Role: {self.target_role.mention}\n"
                f"Action: **{action.title()}**\n\n"
                f"Add conditions that must be met for this rule to apply.\n"
                f"You can add multiple conditions and choose AND/OR logic."
            ),
            color=COLORS["primary"]
        )
        
        await interaction.response.edit_message(embed=embed, view=view)


class AddConditionView(View):
    """View for adding conditions"""
    def __init__(self, manager, guild: discord.Guild, target_role: discord.Role, action: str):
        super().__init__(timeout=300)
        self.manager = manager
        self.guild = guild
        self.target_role = target_role
        self.action = action
        self.conditions = []
        self.logic = "AND"
        self.condition_type = None  # "has" or "doesnt_have"
        
        # Add condition type selector
        self.add_item(ConditionTypeSelect(self))

class ConditionTypeSelect(Select):
    """Select condition type (has/doesn't have)"""
    def __init__(self, parent_view):
        options = [
            discord.SelectOption(
                label="User HAS role",
                value="has",
                description="Condition is met when user has the role",
                emoji="✅"
            ),
            discord.SelectOption(
                label="User DOESN'T HAVE role",
                value="doesnt_have",
                description="Condition is met when user lacks the role",
                emoji="❌"
            ),
        ]
        super().__init__(
            placeholder="Select condition type...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        self.parent_view.condition_type = self.values[0]
        
        # Move to role selection for condition
        view = SelectConditionRoleView(
            self.parent_view.manager,
            self.parent_view.guild,
            self.parent_view.target_role,
            self.parent_view.action,
            self.parent_view.conditions,
            self.parent_view.logic,
            self.parent_view.condition_type
        )
        
        cond_text = "HAS" if self.parent_view.condition_type == "has" else "DOESN'T HAVE"
        
        embed = discord.Embed(
            title="➕ Add Role Connection",
            description=(
                f"**Step 4: Select Condition Role**\n\n"
                f"Target Role: {self.parent_view.target_role.mention}\n"
                f"Action: **{self.parent_view.action.title()}**\n"
                f"Condition Type: **User {cond_text} role**\n\n"
                f"Select which role to check:"
            ),
            color=COLORS["primary"]
        )
        
        await interaction.response.edit_message(embed=embed, view=view)


class SelectConditionRoleView(View):
    """View for selecting role in condition"""
    def __init__(self, manager, guild: discord.Guild, target_role: discord.Role, 
                 action: str, conditions: list, logic: str, condition_type: str):
        super().__init__(timeout=300)
        self.manager = manager
        self.guild = guild
        self.target_role = target_role
        self.action = action
        self.conditions = conditions
        self.logic = logic
        self.condition_type = condition_type
        
        self.add_item(ConditionRoleSelect(self))


class ConditionRoleSelect(RoleSelect):
    """Select role for condition"""
    def __init__(self, parent_view):
        super().__init__(
            placeholder="Select role for condition...",
            min_values=1,
            max_values=1
        )
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        condition_role = self.values[0]
        
        # Add condition to list
        self.parent_view.conditions.append({
            "type": self.parent_view.condition_type,
            "role_id": condition_role.id
        })
        
        # Move to finalize or add more conditions
        view = FinalizeConnectionView(
            self.parent_view.manager,
            self.parent_view.guild,
            self.parent_view.target_role,
            self.parent_view.action,
            self.parent_view.conditions,
            self.parent_view.logic
        )
        
        # Build conditions display
        cond_text = []
        for cond in self.parent_view.conditions:
            role = self.parent_view.guild.get_role(cond["role_id"])
            if role:
                cond_type = "HAS" if cond["type"] == "has" else "DOESN'T HAVE"
                cond_text.append(f"• User {cond_type} {role.mention}")
        
        embed = discord.Embed(
            title="➕ Add Role Connection",
            description=(
                f"**Step 5: Finalize Connection**\n\n"
                f"Target Role: {self.parent_view.target_role.mention}\n"
                f"Action: **{self.parent_view.action.title()}**\n\n"
                f"**Conditions ({self.parent_view.logic}):**\n" + "\n".join(cond_text) + "\n\n"
                f"Add more conditions or save this connection."
            ),
            color=COLORS["primary"]
        )
        
        await interaction.response.edit_message(embed=embed, view=view)


class FinalizeConnectionView(View):
    """View for finalizing connection"""
    def __init__(self, manager, guild: discord.Guild, target_role: discord.Role,
                 action: str, conditions: list, logic: str):
        super().__init__(timeout=300)
        self.manager = manager
        self.guild = guild
        self.target_role = target_role
        self.action = action
        self.conditions = conditions
        self.logic = logic

    @discord.ui.button(label="Add Another Condition", style=discord.ButtonStyle.blurple, emoji="➕")
    async def add_condition(self, interaction: discord.Interaction, button: Button):
        view = AddConditionView(self.manager, self.guild, self.target_role, self.action)
        view.conditions = self.conditions
        view.logic = self.logic
        
        embed = discord.Embed(
            title="➕ Add Role Connection",
            description=(
                f"**Add Another Condition**\n\n"
                f"Target Role: {self.target_role.mention}\n"
                f"Action: **{self.action.title()}**\n\n"
                f"Select condition type:"
            ),
            color=COLORS["primary"]
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="Change Logic (AND/OR)", style=discord.ButtonStyle.gray, emoji="🔀")
    async def toggle_logic(self, interaction: discord.Interaction, button: Button):
        self.logic = "OR" if self.logic == "AND" else "AND"
        
        # Rebuild embed with new logic
        cond_text = []
        for cond in self.conditions:
            role = self.guild.get_role(cond["role_id"])
            if role:
                cond_type = "HAS" if cond["type"] == "has" else "DOESN'T HAVE"
                cond_text.append(f"• User {cond_type} {role.mention}")
        
        embed = discord.Embed(
            title="➕ Add Role Connection",
            description=(
                f"**Step 5: Finalize Connection**\n\n"
                f"Target Role: {self.target_role.mention}\n"
                f"Action: **{self.action.title()}**\n\n"
                f"**Conditions ({self.logic}):**\n" + "\n".join(cond_text) + "\n\n"
                f"Logic changed to **{self.logic}**"
            ),
            color=COLORS["primary"]
        )
        
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Save Connection", style=discord.ButtonStyle.green, emoji="💾")
    async def save_connection(self, interaction: discord.Interaction, button: Button):
        try:
            # Save to database
            await self.manager.add_connection(
                self.guild.id,
                self.target_role.id,
                self.action,
                self.conditions,
                self.logic
            )
            
            # Build success message
            cond_text = []
            for cond in self.conditions:
                role = self.guild.get_role(cond["role_id"])
                if role:
                    cond_type = "HAS" if cond["type"] == "has" else "DOESN'T HAVE"
                    cond_text.append(f"• User {cond_type} {role.name}")
            
            embed = create_embed(
                "✅ Connection Created",
                (
                    f"**{self.action.title()} {self.target_role.mention}**\n\n"
                    f"When ({self.logic}):\n" + "\n".join(cond_text)
                ),
                COLORS["success"]
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
            # Auto-return to role connections menu after 2 seconds
            await asyncio.sleep(2)
            
            # Return to role connections menu
            from cogs.setup import RoleConnectionSetupView
            view = RoleConnectionSetupView(self.manager, self.guild)
            
            embed = discord.Embed(
                title="🔗 Role Connection System",
                description="Connection created successfully! Select an option:",
                color=COLORS["primary"]
            )
            
            await interaction.message.edit(embed=embed, view=view)
            
        except Exception as e:
            log_system(f"[ROLE_CONNECTION] Error saving connection: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    f"Failed to save connection: {str(e)}",
                    COLORS["error"]
                ),
                ephemeral=True
            )


class ManageConnectionsView(View):
    """View for managing existing connections"""
    def __init__(self, manager, guild: discord.Guild, connections: list):
        super().__init__(timeout=300)
        self.manager = manager
        self.guild = guild
        self.connections = connections
        
        self.add_item(ManageConnectionSelect(manager, guild, connections))


class ManageConnectionSelect(Select):
    """Select connection to manage"""
    def __init__(self, manager, guild: discord.Guild, connections: list):
        self.manager = manager
        self.guild = guild
        self.connections = connections
        
        options = []
        for i, conn in enumerate(connections[:25], 1):
            target_role = guild.get_role(conn.target_role_id)
            if target_role:
                status = "✅" if conn.enabled else "❌"
                options.append(discord.SelectOption(
                    label=f"{status} {conn.action.title()} {target_role.name}",
                    value=str(conn.id),
                    description=f"ID: {conn.id}"
                ))
        
        super().__init__(
            placeholder="Select connection to manage...",
            min_values=1,
            max_values=1,
            options=options if options else [discord.SelectOption(label="No connections", value="none")]
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            return
        
        conn_id = int(self.values[0])
        connection = next((c for c in self.connections if c.id == conn_id), None)
        
        if not connection:
            await interaction.response.send_message(
                embed=create_embed("Error", "Connection not found.", COLORS["error"]),
                ephemeral=True
            )
            return
        
        view = ConnectionActionsView(self.manager, self.guild, connection)
        
        target_role = self.guild.get_role(connection.target_role_id)
        cond_text = []
        for cond in connection.conditions:
            role = self.guild.get_role(cond["role_id"])
            if role:
                cond_type = "HAS" if cond["type"] == "has" else "DOESN'T HAVE"
                cond_text.append(f"• User {cond_type} {role.mention}")
        
        status = "✅ Enabled" if connection.enabled else "❌ Disabled"
        
        embed = discord.Embed(
            title=f"Manage Connection #{connection.id}",
            description=(
                f"**Action:** {connection.action.title()} {target_role.mention}\n"
                f"**Status:** {status}\n\n"
                f"**Conditions ({connection.logic}):**\n" + "\n".join(cond_text)
            ),
            color=COLORS["primary"]
        )
        
        await interaction.response.edit_message(embed=embed, view=view)


class ConnectionActionsView(View):
    """View for connection actions (toggle/delete)"""
    def __init__(self, manager, guild: discord.Guild, connection):
        super().__init__(timeout=300)
        self.manager = manager
        self.guild = guild
        self.connection = connection

    @discord.ui.button(label="Toggle On/Off", style=discord.ButtonStyle.blurple, emoji="🔄")
    async def toggle(self, interaction: discord.Interaction, button: Button):
        await self.manager.toggle_connection(self.guild.id, self.connection.id)
        self.connection.enabled = not self.connection.enabled
        
        status = "enabled" if self.connection.enabled else "disabled"
        
        await interaction.response.send_message(
            embed=create_embed(
                "Connection Updated",
                f"Connection #{self.connection.id} has been {status}.",
                COLORS["success"]
            ),
            ephemeral=True
        )

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red, emoji="🗑️")
    async def delete(self, interaction: discord.Interaction, button: Button):
        await self.manager.remove_connection(self.guild.id, self.connection.id)
        
        await interaction.response.send_message(
            embed=create_embed(
                "Connection Deleted",
                f"Connection #{self.connection.id} has been removed.",
                COLORS["success"]
            ),
            ephemeral=True
        )


class ProtectedRolesView(View):
    """View for managing protected roles"""
    def __init__(self, manager, guild: discord.Guild):
        super().__init__(timeout=300)
        self.manager = manager
        self.guild = guild

    @discord.ui.button(label="Add Protected Role", style=discord.ButtonStyle.green, emoji="➕")
    async def add_protected(self, interaction: discord.Interaction, button: Button):
        view = AddProtectedRoleView(self.manager, self.guild)
        
        embed = discord.Embed(
            title="🛡️ Add Protected Role",
            description="Select a role to protect from role connections:",
            color=COLORS["primary"]
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="Remove Protected Role", style=discord.ButtonStyle.red, emoji="➖")
    async def remove_protected(self, interaction: discord.Interaction, button: Button):
        await self.manager.load_protected_roles(self.guild.id)
        protected = self.manager.protected_roles_cache.get(self.guild.id, [])
        
        if not protected:
            await interaction.response.send_message(
                embed=create_embed(
                    "No Protected Roles",
                    "There are no protected roles to remove.",
                    COLORS["warning"]
                ),
                ephemeral=True
            )
            return
        
        view = RemoveProtectedRoleView(self.manager, self.guild, protected)
        
        embed = discord.Embed(
            title="🛡️ Remove Protected Role",
            description="Select a role to remove from protection:",
            color=COLORS["primary"]
        )
        
        await interaction.response.edit_message(embed=embed, view=view)


class AddProtectedRoleView(View):
    """View for adding protected role"""
    def __init__(self, manager, guild: discord.Guild):
        super().__init__(timeout=300)
        self.manager = manager
        self.guild = guild
        self.add_item(AddProtectedRoleSelect(manager, guild))


class AddProtectedRoleSelect(RoleSelect):
    """Select role to protect"""
    def __init__(self, manager, guild: discord.Guild):
        super().__init__(
            placeholder="Select role to protect...",
            min_values=1,
            max_values=1
        )
        self.manager = manager
        self.guild = guild

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]
        await self.manager.add_protected_role(self.guild.id, role.id)
        
        await interaction.response.send_message(
            embed=create_embed(
                "Protected Role Added",
                f"{role.mention} is now protected from role connections.",
                COLORS["success"]
            ),
            ephemeral=True
        )


class RemoveProtectedRoleView(View):
    """View for removing protected role"""
    def __init__(self, manager, guild: discord.Guild, protected_roles: list):
        super().__init__(timeout=300)
        self.manager = manager
        self.guild = guild
        self.add_item(RemoveProtectedRoleSelect(manager, guild, protected_roles))


class RemoveProtectedRoleSelect(Select):
    """Select protected role to remove"""
    def __init__(self, manager, guild: discord.Guild, protected_roles: list):
        self.manager = manager
        self.guild = guild
        
        options = []
        for role_id in protected_roles[:25]:
            role = guild.get_role(role_id)
            if role:
                options.append(discord.SelectOption(
                    label=role.name,
                    value=str(role_id),
                    emoji="🛡️"
                ))
        
        super().__init__(
            placeholder="Select role to unprotect...",
            min_values=1,
            max_values=1,
            options=options if options else [discord.SelectOption(label="No roles", value="none")]
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            return
        
        role_id = int(self.values[0])
        await self.manager.remove_protected_role(self.guild.id, role_id)
        
        role = self.guild.get_role(role_id)
        role_name = role.mention if role else f"Role ID {role_id}"
        
        await interaction.response.send_message(
            embed=create_embed(
                "Protected Role Removed",
                f"{role_name} is no longer protected.",
                COLORS["success"]
            ),
            ephemeral=True
        )


import asyncio