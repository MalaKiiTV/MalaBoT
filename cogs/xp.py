"""
XP and Leveling Cog for MalaBoT.
Handles user XP gain, levels, and leaderboards.
"""

import discord
from discord import app_commands
from discord.ext import commands
import random
from datetime import datetime, timedelta

from utils.logger import get_logger
from utils.helpers import create_embed
from config.constants import COLORS, XP_PER_MESSAGE_MIN, XP_PER_MESSAGE_MAX, XP_COOLDOWN_SECONDS

class XpGroup(app_commands.Group):
    """XP and leveling command group."""
    def __init__(self, cog):
        super().__init__(name="xp", description="XP and leveling commands")
        self.cog = cog

    @app_commands.command(name="rank", description="Check your or another user's rank")
    async def rank(self, interaction: discord.Interaction, user: discord.Member = None):
        """Shows the XP, level, and rank of a user."""
        target = user or interaction.user
        
        try:
            user_xp = await self.cog.db.get_user_xp(target.id)
            user_level = await self.cog.db.get_user_level(target.id)
            
            # Simple rank calculation (could be improved to query rank directly)
            leaderboard = await self.cog.db.get_leaderboard(limit=1000) # Assuming max 1000 users for rank
            rank = "N/A"
            for i, entry in enumerate(leaderboard):
                if entry[0] == target.id:
                    rank = f"#{i + 1}"
                    break
            
            embed = create_embed(
                f"🏆 Rank for {target.display_name}",
                f"**Level:** `{user_level}`\n"
                f"**XP:** `{user_xp}`\n"
                f"**Rank:** `{rank}`",
                COLORS["primary"]
            )
            embed.set_thumbnail(url=target.display_avatar.url)
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            self.cog.logger.error(f"Error getting rank for {target.id}: {e}")
            await interaction.response.send_message(
                embed=create_embed("Error", "Could not retrieve rank information.", COLORS["error"]),
                ephemeral=True
            )

    @app_commands.command(name="leaderboard", description="Show the server's top 10 users")
    async def leaderboard(self, interaction: discord.Interaction):
        """Displays the top 10 users by XP."""
        try:
            leaderboard_data = await self.cog.db.get_leaderboard(limit=10)
            
            if not leaderboard_data:
                await interaction.response.send_message(embed=create_embed("Leaderboard is Empty", "No users have earned XP yet.", COLORS["info"]))
                return
            
            description = ""
            for i, (user_id, xp, level) in enumerate(leaderboard_data):
                user = interaction.guild.get_member(user_id)
                user_display = user.mention if user else f"ID: {user_id}"
                description += f"**{i+1}.** {user_display} - Level {level} ({xp} XP)\n"
                
            embed = create_embed("🏆 Server Leaderboard", description, COLORS["gold"])
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.cog.logger.error(f"Error getting leaderboard: {e}")
            await interaction.response.send_message(
                embed=create_embed("Error", "Could not retrieve the leaderboard.", COLORS["error"]),
                ephemeral=True
            )


class Xp(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db_manager
        self.logger = get_logger('xp')
        self.cooldowns = {}
        self._xp_group = XpGroup(self)

    async def cog_load(self):
        self.bot.tree.add_command(self._xp_group)
        
    async def cog_unload(self):
        self.bot.tree.remove_command(self._xp_group.name)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Awards XP for messages."""
        if message.author.bot or not message.guild:
            return

        user_id = message.author.id
        now = datetime.now()

        # Check cooldown
        if user_id in self.cooldowns:
            if now < self.cooldowns[user_id]:
                return
        
        # Update cooldown
        self.cooldowns[user_id] = now + timedelta(seconds=XP_COOLDOWN_SECONDS)
        
        # Grant XP
        xp_to_add = random.randint(XP_PER_MESSAGE_MIN, XP_PER_MESSAGE_MAX)
        await self.db.update_user_xp(user_id, xp_to_add)


async def setup(bot: commands.Bot):
    await bot.add_cog(Xp(bot))
