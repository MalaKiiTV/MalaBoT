import discord
from discord import app_commands
from discord.ext import commands
import time

# Test decorator behavior - this is what actually works
class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='test', description='Test command')
    async def test_method(self, interaction: discord.Interaction):
        pass

# The decorator returns a Command object, not the original function
print('Testing correct iteration method:')
for cmd in TestCog.__dict__.values():
    if isinstance(cmd, discord.app_commands.commands.Command):
        print(f'Found Command object: {cmd.name}')
        # This is what we should add to the tree
    elif hasattr(cmd, 'app_command'):
        print(f'Found method with app_command: {cmd.app_command.name}')

print('\n--- Testing utility cog ---')
import cogs.utility
utility_class = cogs.utility.Utility

commands_found = []
for cmd in utility_class.__dict__.values():
    if isinstance(cmd, discord.app_commands.commands.Command):
        print(f'Found command: {cmd.name}')
        commands_found.append(cmd)

print(f'\nTotal commands found in utility: {len(commands_found)}')
