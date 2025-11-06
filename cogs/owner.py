import discord
from discord import app_commands
from discord.ext import commands
import utils.embed_helper as embed_helper

class Owner(commands.Cog):
    """Owner Cog - Minimal Working Version"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = bot.logger
    
    async def cog_load(self):
        """Called when the cog is loaded"""
        self.logger.info(f"Owner cog loaded successfully")
    
    async def cog_unload(self):
        """Called when the cog is unloaded"""
        self.logger.info(f"Owner cog unloaded")

async def setup(bot: commands.Bot):
    """Setup function for the cog"""
    await bot.add_cog(Owner(bot))
