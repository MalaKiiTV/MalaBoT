"""
Fix all issues and clear Discord command cache
"""

import asyncio
import os
from dotenv import load_dotenv

async def clear_all_commands():
    """Clear all Discord commands (global and guild)"""
    import discord
    from discord import app_commands
    
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    debug_guilds = os.getenv('DEBUG_GUILDS', '').split(',')
    debug_guilds = [int(g.strip()) for g in debug_guilds if g.strip()]
    
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)
    
    @client.event
    async def on_ready():
        print(f"✅ Logged in as {client.user}")
        
        try:
            # Clear guild commands
            if debug_guilds:
                for guild_id in debug_guilds:
                    guild = discord.Object(id=guild_id)
                    tree.clear_commands(guild=guild)
                    await tree.sync(guild=guild)
                    print(f"✅ Cleared commands for guild {guild_id}")
            
            # Clear global commands
            tree.clear_commands(guild=None)
            await tree.sync(guild=None)
            print("✅ Cleared global commands")
            
            print("\n✅ All commands cleared successfully!")
            print("⚠️ Now restart your bot to re-sync commands properly")
            
        except Exception as e:
            print(f"❌ Error clearing commands: {e}")
        finally:
            await client.close()
    
    await client.start(token)

def main():
    """Main execution"""
    print("🔧 Clearing Discord command cache...\n")
    
    try:
        asyncio.run(clear_all_commands())
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()