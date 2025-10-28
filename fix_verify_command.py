"""
Fix /verify command structure in Discord
This script will properly clear and resync the verify command as a parent with subcommands.

Usage:
    python fix_verify_command.py
"""

import discord
from discord.ext import commands
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings

async def fix_verify_command():
    """Fix the verify command structure."""
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix="/", intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"✅ Logged in as {bot.user}")
        print(f"📊 Connected to {len(bot.guilds)} guild(s)")
        print("\n" + "="*60)
        print("FIXING /VERIFY COMMAND STRUCTURE")
        print("="*60 + "\n")
        
        try:
            # Step 1: Clear ALL commands globally
            print("🧹 Step 1: Clearing all global commands...")
            bot.tree.clear_commands(guild=None)
            await bot.tree.sync()
            print("   ✅ Global commands cleared")
            
            # Step 2: Clear commands from all guilds
            for guild in bot.guilds:
                print(f"\n🧹 Step 2: Clearing commands from {guild.name}...")
                bot.tree.clear_commands(guild=guild)
                await bot.tree.sync(guild=guild)
                print(f"   ✅ Commands cleared from {guild.name}")
            
            # Step 3: Wait for Discord to process
            print("\n⏳ Step 3: Waiting 5 seconds for Discord to process...")
            await asyncio.sleep(5)
            
            # Step 4: Load the verify cog
            print("\n📦 Step 4: Loading verify cog...")
            await bot.load_extension('cogs.verify')
            print("   ✅ Verify cog loaded")
            
            # Step 5: Sync commands to guilds (instant)
            for guild in bot.guilds:
                print(f"\n🔄 Step 5: Syncing commands to {guild.name}...")
                bot.tree.copy_global_to(guild=guild)
                synced = await bot.tree.sync(guild=guild)
                print(f"   ✅ Synced {len(synced)} commands to {guild.name}")
                for cmd in synced:
                    if hasattr(cmd, 'name'):
                        print(f"      - /{cmd.name}")
            
            # Step 6: Global sync
            print("\n🌐 Step 6: Syncing global commands...")
            synced = await bot.tree.sync()
            print(f"   ✅ Synced {len(synced)} global commands")
            
            print("\n" + "="*60)
            print("✅ /VERIFY COMMAND STRUCTURE FIXED!")
            print("="*60)
            print("\n📝 Next steps:")
            print("   1. Wait 30 seconds")
            print("   2. In Discord, type /verify and press space")
            print("   3. You should see: submit, review, setup as subcommands")
            print("   4. If not, restart Discord (Ctrl+R)")
            print("\n⏳ Closing in 5 seconds...")
            
            await asyncio.sleep(5)
            await bot.close()
            
        except Exception as e:
            print(f"\n❌ Error fixing verify command: {e}")
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
    print("\n" + "="*60)
    print("MalaBoT /verify Command Structure Fix")
    print("="*60 + "\n")
    
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
    print("\n⚠️  This will fix the /verify command structure in Discord")
    print("   The command will appear as a parent with subcommands.\n")
    
    try:
        response = input("Continue? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("❌ Cancelled by user")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        sys.exit(0)
    
    print("\n🚀 Starting fix process...\n")
    
    try:
        asyncio.run(fix_verify_command())
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()