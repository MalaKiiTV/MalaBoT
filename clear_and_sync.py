"""
Command Clear and Sync Script for MalaBoT
This script forcefully clears all commands and prepares for a clean sync.
Run this when commands are not showing up in Discord.

Usage:
    python clear_and_sync.py
"""

import discord
from discord.ext import commands
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings

async def clear_and_sync():
    """Clear all commands from Discord."""
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix="/", intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"✅ Logged in as {bot.user}")
        print(f"📊 Connected to {len(bot.guilds)} guild(s)")
        print("\n" + "="*50)
        print("CLEARING ALL COMMANDS")
        print("="*50 + "\n")
        
        try:
            # Clear all global commands
            bot.tree.clear_commands(guild=None)
            print("🧹 Cleared global commands from tree")
            
            # Clear commands from all guilds
            for guild in bot.guilds:
                print(f"\n📍 Processing guild: {guild.name} (ID: {guild.id})")
                bot.tree.clear_commands(guild=guild)
                synced = await bot.tree.sync(guild=guild)
                print(f"   ✅ Cleared {len(synced)} commands from {guild.name}")
            
            # Sync global commands (empty)
            print("\n🌐 Syncing empty global commands...")
            synced = await bot.tree.sync()
            print(f"✅ Global sync complete: {len(synced)} commands")
            
            print("\n" + "="*50)
            print("✅ ALL COMMANDS CLEARED SUCCESSFULLY!")
            print("="*50)
            print("\n📝 Next steps:")
            print("   1. Close this script")
            print("   2. Start your bot normally: python bot.py")
            print("   3. Wait 30 seconds for commands to sync")
            print("   4. Type / in Discord to see your commands")
            print("\n⏳ Closing in 5 seconds...")
            
            await asyncio.sleep(5)
            await bot.close()
            
        except Exception as e:
            print(f"\n❌ Error during command clear: {e}")
            import traceback
            traceback.print_exc()
            await bot.close()
    
    try:
        await bot.start(settings.DISCORD_TOKEN)
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Failed to start bot: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main entry point."""
    print("\n" + "="*50)
    print("MalaBoT Command Clear & Sync Utility")
    print("="*50 + "\n")
    
    # Validate settings
    errors = settings.validate()
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    print("⚙️  Configuration validated")
    print(f"🤖 Bot: {settings.BOT_NAME}")
    print(f"📌 Version: {settings.BOT_VERSION}")
    print("\n⚠️  WARNING: This will clear ALL commands from Discord!")
    print("   Your bot will need to resync after this.\n")
    
    try:
        response = input("Continue? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("❌ Cancelled by user")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        sys.exit(0)
    
    print("\n🚀 Starting command clear process...\n")
    
    try:
        asyncio.run(clear_and_sync())
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()