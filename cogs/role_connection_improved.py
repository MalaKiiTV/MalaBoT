import discord
from discord import app_commands, ui
from discord.ext import commands
import asyncio
from typing import List, Dict, Optional
from utils.logger import log_system
from utils.helpers import create_embed
from config.constants import COLORS

class SmartRoleSelect(ui.Select):
    """Smart role selector with search and descriptions"""
    
    def __init__(self, guild: discord.Guild, placeholder: str, max_values: int = 1):
        self.guild = guild
        roles = [r for r in guild.roles if r.name != "@everyone"]
        
        # Sort roles by position and create options
        options = []
        for role in sorted(roles, key=lambda r: r.position, reverse=True)[:25]:
            # Create helpful description
            member_count = len([m for m in guild.members if role in m.roles])
            description = f"{member_count} members • Position: {role.position}"
            
            # Add special indicators for common role types
            role_type = ""
            if any(keyword in role.name.lower() for keyword in ['admin', 'moderator', 'mod']):
                role_type = "👨‍💼 Staff • "
            elif any(keyword in role.name.lower() for keyword in ['vip', 'donor', 'premium', 'supporter']):
                role_type = "💎 VIP • "
            elif any(keyword in role.name.lower() for keyword in ['member', 'verified']):
                role_type = "✅ Member • "
            elif any(keyword in role.name.lower() for keyword in ['guest', 'new']):
                role_type = "👋 Guest • "
            elif any(keyword in role.name.lower() for keyword in ['mute', 'jail', 'ban']):
                role_type = "🔒 Restriction • "
            
            options.append(discord.SelectOption(
                label=role.name[:25],  # Discord limit
                value=str(role.id),
                description=f"{role_type}{description}",
                emoji=self._get_role_emoji(role)
            ))
        
        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=max_values,
            options=options
        )
    
    def _get_role_emoji(self, role: discord.Role):
        """Get appropriate emoji for role"""
        if role.color:
            # Use colored circle emoji based on role color
            if role.color.value >= 16711680:  # Red
                return "🔴"
            elif role.color.value >= 16744448:  # Orange  
                return "🟠"
            elif role.color.value >= 16776960:  # Yellow
                return "🟡"
            elif role.color.value >= 65280:  # Green
                return "🟢"
            elif role.color.value >= 255:  # Blue
                return "🔵"
            elif role.color.value >= 8388736:  # Purple
                return "🟣"
        return "⚪"

class RoleActionSelect(ui.Select):
    """Selector for role action with clear descriptions"""
    
    def __init__(self):
        options = [
            discord.SelectOption(
                label="➕ Give Role",
                value="give",
                description="Automatically assign this role when conditions are met",
                emoji="➕"
            ),
            discord.SelectOption(
                label="➖ Remove Role", 
                value="remove",
                description="Automatically remove this role when conditions are met",
                emoji="➖"
            )
        ]
        
        super().__init__(
            placeholder="📋 What should happen to the target role?",
            min_values=1,
            max_values=1,
            options=options
        )

class ConditionTypeSelect(ui.Select):
    """Selector for condition types with examples"""
    
    def __init__(self):
        options = [
            discord.SelectOption(
                label="✅ User HAS these roles",
                value="has",
                description="Rule triggers when user already has the selected roles",
                emoji="✅"
            ),
            discord.SelectOption(
                label="❌ User DOESN'T HAVE these roles",
                value="doesnt_have", 
                description="Rule triggers when user doesn't have the selected roles",
                emoji="❌"
            )
        ]
        
        super().__init__(
            placeholder="🔍 When should this rule trigger?",
            min_values=1,
            max_values=1,
            options=options
        )

class LogicOperatorSelect(ui.Select):
    """Selector for logic with visual examples"""
    
    def __init__(self):
        options = [
            discord.SelectOption(
                label="🔗 AND (All roles required)",
                value="AND",
                description="User must have ALL selected roles • More restrictive",
                emoji="🔗"
            ),
            discord.SelectOption(
                label="💫 OR (Any role works)",
                value="OR",
                description="User needs ANY of the selected roles • More flexible",
                emoji="💫"
            )
        ]
        
        super().__init__(
            placeholder="🧠 How should multiple conditions work?",
            min_values=1,
            max_values=1,
            options=options
        )

class LiveRulePreview:
    """Helper class to generate live rule previews"""
    
    @staticmethod
    def generate_preview(target_role: discord.Role, action: str, 
                        condition_roles: List[discord.Role], condition_type: str, 
                        logic: str) -> discord.Embed:
        """Generate a preview embed showing exactly what the rule will do"""
        
        embed = discord.Embed(
            title="🔍 Live Rule Preview",
            description="This is exactly what your rule will do:",
            color=COLORS["primary"]
        )
        
        # Target role section
        embed.add_field(
            name="🎯 Target Role",
            value=f"{target_role.mention} ({target_role.name})",
            inline=True
        )
        
        # Action section with clear description
        action_emoji = "➕" if action == "give" else "➖"
        action_desc = "automatically assigned" if action == "give" else "automatically removed"
        embed.add_field(
            name=f"{action_emoji} Action",
            value=f"Role will be **{action_desc}**",
            inline=True
        )
        
        # Logic section
        logic_emoji = "🔗" if logic == "AND" else "💫"
        logic_desc = "must have ALL roles" if logic == "AND" else "needs ANY role"
        embed.add_field(
            name=f"{logic_emoji} Logic",
            value=f"User {logic_desc}",
            inline=True
        )
        
        # Conditions section with examples
        condition_emoji = "✅" if condition_type == "has" else "❌"
        condition_desc = "already has" if condition_type == "has" else "doesn't have"
        
        condition_list = []
        for role in condition_roles[:5]:  # Show max 5 roles
            condition_list.append(f"• {role.mention}")
        
        if len(condition_roles) > 5:
            condition_list.append(f"• ... and {len(condition_roles) - 5} more roles")
        
        embed.add_field(
            name=f"{condition_emoji} Conditions ({len(condition_roles)} total)",
            value=f"User **{condition_desc}**:\n" + "\n".join(condition_list),
            inline=False
        )
        
        # Plain English explanation
        if logic == "AND":
            if condition_type == "has":
                explanation = f"When a user has **all** of the {len(condition_roles)} selected roles, they will be **{action}** the {target_role.mention} role."
            else:
                explanation = f"When a user **doesn't have** any of the {len(condition_roles)} selected roles, they will be **{action}** the {target_role.mention} role."
        else:  # OR
            if condition_type == "has":
                explanation = f"When a user has **any** of the {len(condition_roles)} selected roles, they will be **{action}** the {target_role.mention} role."
            else:
                explanation = f"When a user **doesn't have** any of the {len(condition_roles)} selected roles, they will be **{action}** the {target_role.mention} role."
        
        embed.add_field(
            name="💡 In Plain English",
            value=explanation,
            inline=False
        )
        
        # Real-world examples
        embed.add_field(
            name="📚 Example Scenarios",
            value=LiveRulePreview._get_examples(action, condition_type, logic),
            inline=False
        )
        
        return embed
    
    @staticmethod
    def _get_examples(action: str, condition_type: str, logic: str) -> str:
        """Get relevant examples based on rule parameters"""
        examples = []
        
        if action == "give":
            if condition_type == "has":
                if logic == "AND":
                    examples.extend([
                        "• Give `Staff` role when user has both `Admin` AND `Moderator`",
                        "• Give `VIP` role when user has `Donor` AND `Supporter` AND `Active`"
                    ])
                else:
                    examples.extend([
                        "• Give `Gamer` role when user has `Minecraft` OR `Valorant` OR `Among Us`",
                        "• Give `Member` role when user has `Verified` OR `Email Confirmed`"
                    ])
            else:  # doesnt_have
                if logic == "AND":
                    examples.extend([
                        "• Give `Full Access` when user doesn't have `Guest` AND doesn't have `Muted`",
                        "• Give `Trusted` when user doesn't have `New Member` AND doesn't have `Warning`"
                    ])
                else:
                    examples.extend([
                        "• Give `Clean Record` when user doesn't have any warning roles",
                        "• Give `Experienced` when user doesn't have `New` OR `Trial`"
                    ])
        else:  # remove
            if condition_type == "has":
                if logic == "AND":
                    examples.extend([
                        "• Remove `Trial` when user gets `Full Member` AND `Verified`",
                        "• Remove `Guest` when user gets `Member` AND `Email Confirmed`"
                    ])
                else:
                    examples.extend([
                        "• Remove `New Member` when user gets any staff role",
                        "• Remove `Game Access` when user gets banned role"
                    ])
            else:  # doesnt_have
                examples.extend([
                    "• Remove `VIP` when user no longer has any donor roles",
                    "• Remove `Staff` when user loses all position roles"
                ])
        
        return "\n".join(examples[:3])  # Return max 3 examples

class RoleConnectionBuilderView(ui.View):
    """Step-by-step role connection builder with live preview"""
    
    def __init__(self, manager, guild: discord.Guild):
        super().__init__(timeout=600)  # 10 minute timeout
        self.manager = manager
        self.guild = guild
        self.current_step = 1
        self.total_steps = 5
        
        # Rule data
        self.target_role = None
        self.action = None
        self.condition_roles = []
        self.condition_type = None
        self.logic = None
        
        # Start with step 1
        self.show_step_1()
    
    def show_step_1(self):
        """Step 1: Select target role"""
        self.clear_items()
        self.add_item(SmartRoleSelect(
            self.guild, 
            "🎯 Select the role you want to give or remove (Target Role)",
            max_values=1
        ))
        
        # Add instruction button
        self.add_item(ui.Button(
            label="ℹ️ What is a Target Role?",
            style=discord.ButtonStyle.secondary,
            custom_id="help_target_role"
        ))
    
    def show_step_2(self):
        """Step 2: Select action"""
        self.clear_items()
        self.add_item(RoleActionSelect())
        
        self.add_item(ui.Button(
            label="⬅️ Back to Role Selection",
            style=discord.ButtonStyle.secondary,
            custom_id="back_step_1"
        ))
    
    def show_step_3(self):
        """Step 3: Select condition roles"""
        self.clear_items()
        self.add_item(SmartRoleSelect(
            self.guild,
            "🔍 Select roles to check for (Condition Roles) - Choose up to 10",
            max_values=10
        ))
        
        self.add_item(ui.Button(
            label="⬅️ Back to Action Selection",
            style=discord.ButtonStyle.secondary,
            custom_id="back_step_2"
        ))
    
    def show_step_4(self):
        """Step 4: Select condition type"""
        self.clear_items()
        self.add_item(ConditionTypeSelect())
        
        self.add_item(ui.Button(
            label="⬅️ Back to Condition Roles",
            style=discord.ButtonStyle.secondary,
            custom_id="back_step_3"
        ))
    
    def show_step_5(self):
        """Step 5: Select logic and finalize"""
        self.clear_items()
        self.add_item(LogicOperatorSelect())
        
        self.add_item(ui.Button(
            label="⬅️ Back to Condition Type",
            style=discord.ButtonStyle.secondary,
            custom_id="back_step_4"
        ))
    
    def show_final_preview(self):
        """Show final preview with save option"""
        self.clear_items()
        
        # Add save and back buttons
        self.add_item(ui.Button(
            label="💾 Save This Rule",
            style=discord.ButtonStyle.success,
            custom_id="save_rule",
            emoji="💾"
        ))
        
        self.add_item(ui.Button(
            label="⬅️ Back to Logic Selection",
            style=discord.ButtonStyle.secondary,
            custom_id="back_step_5"
        ))
        
        self.add_item(ui.Button(
            label="❌ Cancel",
            style=discord.ButtonStyle.danger,
            custom_id="cancel",
            emoji="❌"
        ))
    
    async def update_message(self, interaction: discord.Interaction):
        """Update the message with current step and preview"""
        
        # Create main embed
        if self.current_step <= 5:
            embed = discord.Embed(
                title=f"🔗 Role Connection Builder - Step {self.current_step}/{self.total_steps}",
                description=self._get_step_description(),
                color=COLORS["primary"]
            )
            
            # Add progress bar
            progress = "🟩" * self.current_step + "⬜" * (self.total_steps - self.current_step)
            embed.add_field(name="📊 Progress", value=progress, inline=False)
            
            # Add current selections
            selections = self._get_current_selections()
            if selections:
                embed.add_field(name="📋 Current Selections", value=selections, inline=False)
            
            # Add live preview if we have enough data
            if self.current_step >= 3 and self.target_role and self.condition_roles:
                try:
                    action = self.action or "give"
                    condition_type = self.condition_type or "has"
                    logic = self.logic or "AND"
                    
                    preview = LiveRulePreview.generate_preview(
                        self.target_role, action, self.condition_roles, 
                        condition_type, logic
                    )
                    
                    # Add preview as a separate field
                    preview_text = (
                        f"**Target:** {self.target_role.mention}\n"
                        f"**Action:** {action.title()}\n"
                        f"**Conditions:** {len(self.condition_roles)} roles\n"
                        f"**Type:** {condition_type.replace('_', ' ').title()}\n"
                        f"**Logic:** {logic}"
                    )
                    embed.add_field(name="🔍 Live Preview", value=preview_text, inline=False)
                    
                except Exception as e:
                    log_system(f"[ROLE_CONNECTION] Error generating preview: {e}", level="error")
        
        else:  # Final preview step
            embed = LiveRulePreview.generate_preview(
                self.target_role, self.action, self.condition_roles,
                self.condition_type, self.logic
            )
            
            embed.title = "✅ Final Rule Review"
            embed.description = "Review your rule before saving. Click '💾 Save This Rule' to create it."
            
            embed.set_footer(text="This rule will be active immediately after saving")
        
        # Update view based on current step
        if self.current_step == 1:
            self.show_step_1()
        elif self.current_step == 2:
            self.show_step_2()
        elif self.current_step == 3:
            self.show_step_3()
        elif self.current_step == 4:
            self.show_step_4()
        elif self.current_step == 5:
            self.show_step_5()
        else:  # Final step
            self.show_final_preview()
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    def _get_step_description(self) -> str:
        """Get description for current step"""
        descriptions = {
            1: "🎯 **Select Target Role**\n\nChoose the role that will be automatically given or removed when conditions are met.\n\n💡 *This is the role the bot will manage automatically.*",
            2: "⚡ **Select Action**\n\nChoose whether to **give** or **remove** the target role when conditions are met.\n\n💡 *Give = Assign role • Remove = Take away role*",
            3: "🔍 **Select Condition Roles**\n\nChoose which roles the bot should check for. Users must meet conditions related to these roles.\n\n💡 *You can select multiple roles - up to 10 at once!*",
            4: "🔎 **Select Condition Type**\n\nChoose whether the rule triggers when users **HAVE** or **DON'T HAVE** the condition roles.\n\n💡 *This determines when your rule will activate*",
            5: "🧠 **Select Logic**\n\nChoose how multiple conditions work together.\n\n💡 *AND = All conditions required • OR = Any condition works*"
        }
        return descriptions.get(self.current_step, "Review your rule before saving.")
    
    def _get_current_selections(self) -> str:
        """Get formatted current selections"""
        selections = []
        
        if self.target_role:
            selections.append(f"🎯 **Target:** {self.target_role.mention}")
        
        if self.action:
            action_emoji = "➕" if self.action == "give" else "➖"
            selections.append(f"{action_emoji} **Action:** {self.action.title()}")
        
        if self.condition_roles:
            selections.append(f"🔍 **Conditions:** {len(self.condition_roles)} role(s) selected")
        
        if self.condition_type:
            condition_emoji = "✅" if self.condition_type == "has" else "❌"
            selections.append(f"{condition_emoji} **Type:** User {self.condition_type.replace('_', ' ').upper()} these roles")
        
        if self.logic:
            logic_emoji = "🔗" if self.logic == "AND" else "💫"
            logic_desc = "All required" if self.logic == "AND" else "Any works"
            selections.append(f"{logic_emoji} **Logic:** {logic_desc}")
        
        return "\n".join(selections) if selections else "No selections made yet"
    
    async def interaction_check(self, interaction: discord.Interaction):
        """Handle user interactions"""
        
        # Handle help buttons
        if hasattr(interaction.data, 'custom_id'):
            custom_id = interaction.data.get('custom_id')
            if custom_id == 'help_target_role':
                await self.show_help(interaction, "target_role")
                return
        
        # Handle navigation buttons
        if hasattr(interaction.data, 'custom_id'):
            custom_id = interaction.data.get('custom_id')
            if custom_id == 'cancel':
                await interaction.response.edit_message(
                    embed=create_embed(
                        "❌ Cancelled",
                        "Role connection creation has been cancelled.",
                        COLORS["error"]
                    ),
                    view=None
                )
                self.stop()
                return
            elif custom_id == 'save_rule':
                await self.save_rule(interaction)
                return
            elif custom_id.startswith('back_step_'):
                step_num = int(custom_id.split('_')[-1])
                self.current_step = step_num
                await self.update_message(interaction)
                return
        
        # Handle select menu interactions
        if isinstance(interaction.data, dict) and 'values' in interaction.data:
            component = interaction.data.get('custom_id')
            values = interaction.data.get('values', [])
            
            if values:
                if self.current_step == 1:  # Target role selected
                    role_id = int(values[0])
                    self.target_role = self.guild.get_role(role_id)
                    self.current_step = 2
                    
                elif self.current_step == 2:  # Action selected
                    self.action = values[0]
                    self.current_step = 3
                    
                elif self.current_step == 3:  # Condition roles selected
                    self.condition_roles = []
                    for role_id in values:
                        role = self.guild.get_role(int(role_id))
                        if role:
                            self.condition_roles.append(role)
                    self.current_step = 4
                    
                elif self.current_step == 4:  # Condition type selected
                    self.condition_type = values[0]
                    self.current_step = 5
                    
                elif self.current_step == 5:  # Logic selected
                    self.logic = values[0]
                    self.current_step = 6  # Final review step
                
                await self.update_message(interaction)
    
    async def show_help(self, interaction: discord.Interaction, help_type: str):
        """Show help for specific step"""
        if help_type == "target_role":
            embed = discord.Embed(
                title="🎯 What is a Target Role?",
                description=(
                    "The **target role** is the role that will be automatically **given** or **removed** "
                    "when your conditions are met.\n\n"
                    "**Examples:**\n"
                    "• `VIP` - Give VIP role when user has donor roles\n"
                    "• `Guest` - Remove Guest role when user gets Member role\n"
                    "• `Staff` - Give Staff role when user has admin positions\n"
                    "• `Muted` - Remove Muted role when user is unmuted\n\n"
                    "**💡 Think:** What role do I want the bot to manage automatically?"
                ),
                color=COLORS["info"]
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def save_rule(self, interaction: discord.Interaction):
        """Save the completed rule"""
        try:
            # Validate we have all required data
            if not all([self.target_role, self.action, self.condition_roles, self.condition_type, self.logic]):
                await interaction.response.send_message(
                    embed=create_embed(
                        "❌ Incomplete Rule",
                        "Please complete all steps before saving.",
                        COLORS["error"]
                    ),
                    ephemeral=True
                )
                return
            
            # Build conditions
            conditions = []
            for role in self.condition_roles:
                conditions.append({
                    "type": self.condition_type,
                    "role_id": role.id
                })
            
            # Save the connection
            connection_id = await self.manager.add_connection(
                self.guild.id,
                self.target_role.id,
                self.action,
                conditions,
                self.logic
            )
            
            # Success message
            embed = create_embed(
                "✅ Role Connection Rule Created!",
                f"Rule #{connection_id} has been saved and is now active.\n\n"
                f"**Target:** {self.target_role.mention}\n"
                f"**Action:** {self.action.title()}\n"
                f"**Conditions:** {len(self.condition_roles)} roles\n\n"
                f"Use `/setup` → **Role Connections** → **Manage Existing Rules** to edit this rule later.",
                COLORS["success"]
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
            self.stop()
            
        except Exception as e:
            log_system(f"[ROLE_CONNECTION] Error saving rule: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "❌ Error Saving Rule",
                    f"An error occurred: {str(e)}",
                    COLORS["error"]
                ),
                ephemeral=True
            )