"""
Clear and sync Discord commands for MalaBoT
Clears all commands and forces a fresh sync
"""

import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DEBUG_GUILD_ID = os.getenv('DEBUG_GUILD_ID')

if not TOKEN:
    print("ERROR: DISCORD_TOKEN not found in .env file")
    exit(1)

class CommandClearer(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        """Clear and sync commands"""
        print("=" * 50)
        print("Discord Command Clear & Sync")
        print("=" * 50)
        print()
        
        try:
            # Clear global commands
            print("Clearing global commands...")
            self.tree.clear_commands(guild=None)
            await self.tree.sync()
            print("✓ Global commands cleared")
            print()
            
            # Clear guild commands if DEBUG_GUILD_ID is set
            if DEBUG_GUILD_ID:
                print(f"Clearing guild commands for guild {DEBUG_GUILD_ID}...")
                guild = discord.Object(id=int(DEBUG_GUILD_ID))
                self.tree.clear_commands(guild=guild)
                await self.tree.sync(guild=guild)
                print("✓ Guild commands cleared")
                print()
            
            print("=" * 50)
            print("Command clear completed!")
            print("=" * 50)
            print()
            print("Next steps:")
            print("1. Start your bot normally")
            print("2. Wait 30 seconds for commands to sync")
            print("3. Commands should appear fresh in Discord")
            print()
            
        except Exception as e:
            print(f"ERROR: Failed to clear commands: {e}")
        
        await self.close()

async def main():
    """Run the command clearer"""
    bot = CommandClearer()
    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        await bot.close()
    except Exception as e:
        print(f"ERROR: {e}")
        await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled")