import discord
from discord import app_commands
from discord.ext import commands
import time

# Test decorator behavior
class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='test', description='Test command')
    async def test_method(self, interaction: discord.Interaction):
        pass

# Check raw method in class dict
raw_method = TestCog.__dict__['test_method']
print(f'Raw method type: {type(raw_method)}')
print(f'Raw method dir: {[attr for attr in dir(raw_method) if "command" in attr.lower() or "app" in attr.lower()]}')

# Try accessing the actual command
if hasattr(raw_method, '__discord_app_commands_hook__'):
    print('Has __discord_app_commands_hook__')
    
# Check what the decorator actually returns
print(f'Raw method: {raw_method}')

# Test the iteration method from bot.py
print('\nTesting iteration method:')
for cmd in TestCog.__dict__.values():
    print(f'Checking: {type(cmd)} - {cmd}')
    if hasattr(cmd, 'app_command'):
        print(f'  -> Found command!')
    if hasattr(cmd, '__discord_app_commands_hook__'):
        print(f'  -> Has hook!')
