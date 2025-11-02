# Test how Discord.py command registration actually works
import discord
from discord import app_commands
from discord.ext import commands

class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='test', description='Test command')
    async def test_method(self, interaction: discord.Interaction):
        await interaction.response.send_message("Test")

# Test the registration approach from bot.py
test_cog_class = TestCog
print("Testing command discovery method used in bot.py:")
for cmd in test_cog_class.__dict__.values():
    if hasattr(cmd, 'app_command'):
        print(f"Found command: {cmd.app_command.name}")
