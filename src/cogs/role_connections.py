import json
import logging

import discord
from discord.ext import commands, tasks

from src.utils.logger import log_system


class RoleConnection:
    """Represents a single role connection rule"""

    def __init__(
        self,
        connection_id: int,
        guild_id: int,
        target_role_id: int,
        action: str,
        conditions: list[dict],
        logic: str = "AND",
        enabled: bool = True,
    ):
        self.id = connection_id
        self.guild_id = guild_id
        self.target_role_id = target_role_id
        self.action = action  # "give" or "remove"
        self.conditions = conditions  # [{"type": "has/doesnt_have", "role_id": 123}]
        self.logic = logic  # "AND" or "OR"
        self.enabled = enabled

    def check_conditions(self, member: discord.Member) -> bool:
        """Check if member meets the conditions"""
        if not self.conditions:
            return False

        member_role_ids = [role.id for role in member.roles]

        results = []
        for condition in self.conditions:
            role_id = condition["role_id"]
            condition_type = condition["type"]

            if condition_type == "has":
                results.append(role_id in member_role_ids)
            elif condition_type == "doesnt_have":
                results.append(role_id not in member_role_ids)

        if not results:
            return False

        if self.logic == "AND":
            return all(results)
        else:  # OR
            return any(results)

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "target_role_id": self.target_role_id,
            "action": self.action,
            "conditions": self.conditions,
            "logic": self.logic,
            "enabled": self.enabled,
        }


class RoleConnectionManager:
    """Manages role connections and protected roles"""

    def __init__(self, bot, db_manager):
        self.bot = bot
        self.db = db_manager
        self.logger = logging.getLogger("role_connections")
        self.connections_cache = {}  # {guild_id: [RoleConnection]}
        self.protected_roles_cache = {}  # {guild_id: [role_ids]}


    async def load_connections(self, guild_id: int):
        """Load all connections for a guild from database"""
        connections_data = await self.db.get_setting("role_connections", guild_id)
        if connections_data:
            try:
                # Handle both string (JSON) and list (already parsed) formats
                if isinstance(connections_data, str):
                    data = json.loads(connections_data)
                elif isinstance(connections_data, list):
                    data = connections_data
                else:
                    log_system(
                        f"[ROLE_CONNECTION] Unexpected data type: {type(connections_data)}",
                        level="error",
                    )
                    self.connections_cache[guild_id] = []
                    return

                self.connections_cache[guild_id] = [
                    RoleConnection(
                        connection_id=conn["id"],
                        guild_id=guild_id,
                        target_role_id=conn["target_role_id"],
                        action=conn["action"],
                        conditions=conn["conditions"],
                        logic=conn.get("logic", "AND"),
                        enabled=conn.get("enabled", True),
                    )
                    for conn in data
                ]
            except Exception as e:
                log_system(
                    f"[ROLE_CONNECTION] Error loading connections: {e}", level="error"
                )
                self.connections_cache[guild_id] = []
        else:
            self.connections_cache[guild_id] = []

    async def load_protected_roles(self, guild_id: int):
        """Load protected roles for a guild"""
        self.logger.debug(f"Loading protected roles for guild {guild_id}")

        protected_data = await self.db.get_setting("protected_roles", guild_id)
        if protected_data:
            try:
                self.protected_roles_cache[guild_id] = json.loads(protected_data)
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to parse protected roles for guild {guild_id}: {e}")
                self.protected_roles_cache[guild_id] = []
        else:
            self.protected_roles_cache[guild_id] = []

    async def save_connections(self, guild_id: int):
        """Save connections to database"""
        connections = self.connections_cache.get(guild_id, [])
        data = [conn.to_dict() for conn in connections]
        await self.db.set_setting("role_connections", json.dumps(data), guild_id)

    async def save_protected_roles(self, guild_id: int):
        """Save protected roles to database"""
        protected = self.protected_roles_cache.get(guild_id, [])
        await self.db.set_setting("protected_roles", json.dumps(protected), guild_id)

    async def add_connection(
        self,
        guild_id: int,
        target_role_id: int,
        action: str,
        conditions: list[dict],
        logic: str = "AND",
    ) -> int:
        """Add a new connection"""
        await self.load_connections(guild_id)
        connections = self.connections_cache.get(guild_id, [])

        # Generate new ID
        new_id = max([conn.id for conn in connections], default=0) + 1

        new_connection = RoleConnection(
            connection_id=new_id,
            guild_id=guild_id,
            target_role_id=target_role_id,
            action=action,
            conditions=conditions,
            logic=logic,
        )

        connections.append(new_connection)
        self.connections_cache[guild_id] = connections
        await self.save_connections(guild_id)

        return new_id

    async def remove_connection(self, guild_id: int, connection_id: int):
        """Remove a connection"""
        await self.load_connections(guild_id)
        connections = self.connections_cache.get(guild_id, [])
        self.connections_cache[guild_id] = [
            c for c in connections if c.id != connection_id
        ]
        await self.save_connections(guild_id)

    async def toggle_connection(self, guild_id: int, connection_id: int):
        """Toggle a connection on/off"""
        await self.load_connections(guild_id)
        connections = self.connections_cache.get(guild_id, [])
        for conn in connections:
            if conn.id == connection_id:
                conn.enabled = not conn.enabled
                break
        await self.save_connections(guild_id)

    async def update_connection_logic(
        self, guild_id: int, connection_id: int, new_logic: str
    ):
        """Update the logic (AND/OR) of a connection"""
        await self.load_connections(guild_id)
        connections = self.connections_cache.get(guild_id, [])
        for conn in connections:
            if conn.id == connection_id:
                conn.logic = new_logic
                log_system(
                    f"[ROLE_CONNECTION] Updated connection #{connection_id} logic to {new_logic}"
                )
                break
        await self.save_connections(guild_id)

    async def add_protected_role(self, guild_id: int, role_id: int):
        """Add a protected role"""
        await self.load_protected_roles(guild_id)
        protected = self.protected_roles_cache.get(guild_id, [])
        if role_id not in protected:
            protected.append(role_id)
            self.protected_roles_cache[guild_id] = protected
            await self.save_protected_roles(guild_id)

    async def remove_protected_role(self, guild_id: int, role_id: int):
        """Remove a protected role"""
        await self.load_protected_roles(guild_id)
        protected = self.protected_roles_cache.get(guild_id, [])
        if role_id in protected:
            protected.remove(role_id)
            self.protected_roles_cache[guild_id] = protected
            await self.save_protected_roles(guild_id)

    def is_protected(self, member: discord.Member) -> bool:
        """Check if member has any protected role"""
        protected_roles = self.protected_roles_cache.get(member.guild.id, [])
        member_role_ids = [role.id for role in member.roles]
        return any(role_id in member_role_ids for role_id in protected_roles)

    async def process_member(self, member: discord.Member):
        """Process role connections for a member"""
        if member.bot:
            return

        # Skip if member has protected role
        if self.is_protected(member):
            return

        guild_id = member.guild.id
        connections = self.connections_cache.get(guild_id, [])

        for connection in connections:
            if not connection.enabled:
                continue

            # Check if conditions are met
            conditions_met = connection.check_conditions(member)
            target_role = member.guild.get_role(connection.target_role_id)

            if not target_role:
                continue

            has_role = target_role in member.roles

            try:
                if connection.action == "give" and conditions_met and not has_role:
                    await member.add_roles(target_role, reason="Role connection rule")
                    log_system(
                        f"[ROLE_CONNECTION] Added {target_role.name} to {member.name}"
                    )
                elif connection.action == "remove" and conditions_met and has_role:
                    await member.remove_roles(
                        target_role, reason="Role connection rule"
                    )
                    log_system(
                        f"[ROLE_CONNECTION] Removed {target_role.name} from {member.name}"
                    )
                elif connection.action == "give" and not conditions_met and has_role:
                    # Remove role if conditions no longer met
                    await member.remove_roles(
                        target_role, reason="Role connection conditions no longer met"
                    )
                    log_system(
                        f"[ROLE_CONNECTION] Removed {target_role.name} from {member.name} (conditions not met)"
                    )
            except discord.Forbidden:
                log_system(
                    f"[ROLE_CONNECTION] Missing permissions to modify {member.name}",
                    level="error",
                )
            except Exception as e:
                log_system(
                    f"[ROLE_CONNECTION] Error processing {member.name}: {e}",
                    level="error",
                )


class RoleConnections(commands.Cog):
    """Role connection system for automatic role management"""

    def __init__(self, bot):
        self.bot = bot
        self.manager = RoleConnectionManager(bot, bot.db_manager)
        self.check_connections.start()

    def cog_unload(self):
        self.check_connections.cancel()

    @tasks.loop(minutes=5)
    async def check_connections(self):
        """Periodic check of all members in all guilds"""
        for guild in self.bot.guilds:
            try:
                await self.manager.load_connections(guild.id)
                await self.manager.load_protected_roles(guild.id)

                for member in guild.members:
                    await self.manager.process_member(member)
            except Exception as e:
                log_system(
                    f"[ROLE_CONNECTION] Error in periodic check for {guild.name}: {e}",
                    level="error",
                )

    @check_connections.before_loop
    async def before_check_connections(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Process role connections when member roles change"""
        # Check if member completed onboarding (pending changed from True to False)
        if before.pending and not after.pending:
            log_system(f"[ROLE_CONNECTION] {after.name} completed onboarding!")
            # Remove "Onboarding" role
            onboarding_role_id = await self.bot.db_manager.get_setting("onboarding_role", after.guild.id)
            if onboarding_role_id:
                onboarding_role = discord.utils.get(after.guild.roles, id=int(onboarding_role_id))
                if onboarding_role and onboarding_role in after.roles:
                    try:
                        await after.remove_roles(onboarding_role, reason="Completed onboarding")
                        log_system(f"[ROLE_CONNECTION] Removed Onboarding role from {after.name}")
                    except discord.Forbidden:
                        log_system(f"[ROLE_CONNECTION] Missing permissions to remove Onboarding role from {after.name}", level="error")
        
        if before.roles != after.roles:
            # Skip if member is being processed by another system (e.g., cheater assignment)
            if after.id in self.bot.processing_members:
                log_system(
                    f"[ROLE_CONNECTION] Skipping {after.name} - member is locked for processing"
                )
                return

            try:
                await self.manager.load_connections(after.guild.id)
                await self.manager.load_protected_roles(after.guild.id)
                await self.manager.process_member(after)
            except Exception as e:
                log_system(
                    f"[ROLE_CONNECTION] Error processing member update: {e}",
                    level="error",
                )


async def setup(bot):
    await bot.add_cog(RoleConnections(bot))

