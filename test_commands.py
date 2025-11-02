import discord
from discord import app_commands
from discord.ext import commands

class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='test', description='Test command')
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("Test")

def find_app_command_methods(cog_class):
    """Find methods with @app_commands.command decorator"""
    commands = []
    for name, method in inspect.getmembers(cog_class, predicate=inspect.isfunction):
        if hasattr(method, 'app_command'):
            commands.append(method.app_command)
            print(f"Found decorated method: {name}")
    return commands

import inspect
test_commands = find_app_command_methods(TestCog)
print(f"Found {len(test_commands)} commands: {[cmd.name for cmd in test_commands]}")

# Test with actual instance
test_instance = TestCog(None)
print("\nTesting with instance:")
for name in dir(test_instance):
    attr = getattr(test_instance, name)
    if hasattr(attr, 'app_command'):
        print(f"Instance method with command: {name} -> {attr.app_command.name}")
