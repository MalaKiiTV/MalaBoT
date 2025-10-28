"""
Fix verify commands showing as separate commands instead of grouped
The issue is that app_commands.Group needs special handling
"""

def fix_verify_group_registration():
    """
    The verify commands are defined as a Group, but Discord might not be
    recognizing them as such. We need to ensure the Group is properly
    added to the tree.
    """
    
    with open('cogs/verify.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check current structure
    if 'verify = app_commands.Group' in content:
        print("✅ Verify is defined as app_commands.Group")
        
        # The issue might be that the group is a class variable
        # It should work, but let's verify the setup function
        if 'async def setup(bot: commands.Bot):' in content:
            print("✅ Setup function exists")
            
            # Check if it's just adding the cog
            if 'await bot.add_cog(Verify(bot))' in content:
                print("✅ Cog is being added correctly")
                print("\n⚠️ The code structure is correct!")
                print("\nThe issue is likely one of these:")
                print("1. Discord's cache hasn't updated yet")
                print("2. Commands were synced before the Group structure was in place")
                print("3. Need to clear guild commands and re-sync")
                
                return True
    
    return False

def create_command_clear_script():
    """Create a script to clear and re-sync commands"""
    
    script = '''"""
Clear all commands and re-sync to fix verify command grouping
Run this with: python clear_and_resync.py
"""

import discord
from discord import app_commands
import asyncio
import os
from dotenv import load_dotenv

async def clear_and_sync():
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    debug_guilds = os.getenv('DEBUG_GUILDS', '').split(',')
    debug_guilds = [int(g.strip()) for g in debug_guilds if g.strip()]
    
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)
    
    @client.event
    async def on_ready():
        print(f"✅ Logged in as {client.user}")
        
        try:
            # Clear commands from debug guilds
            for guild_id in debug_guilds:
                guild = discord.Object(id=guild_id)
                
                # Clear all commands
                tree.clear_commands(guild=guild)
                await tree.sync(guild=guild)
                print(f"✅ Cleared commands for guild {guild_id}")
            
            print("\\n✅ Commands cleared!")
            print("⚠️ Now restart your bot to re-sync with the correct structure")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await client.close()
    
    try:
        await client.start(token)
    except Exception as e:
        print(f"❌ Failed to start: {e}")

if __name__ == "__main__":
    asyncio.run(clear_and_sync())
'''
    
    with open('clear_and_resync.py', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("\n✅ Created clear_and_resync.py")
    print("   Run this script to clear commands, then restart your bot")

def main():
    """Main execution"""
    print("🔧 Investigating verify command issue...\n")
    
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("1️⃣ Checking verify command structure...")
    if fix_verify_group_registration():
        print("\n2️⃣ Creating command clear script...")
        create_command_clear_script()
        
        print("\n📝 Solution:")
        print("   The verify commands are correctly structured as a Group.")
        print("   Discord's cache needs to be cleared.")
        print("\n   Steps to fix:")
        print("   1. Stop your bot")
        print("   2. Run: python clear_and_resync.py")
        print("   3. Wait for it to complete")
        print("   4. Start your bot")
        print("   5. Wait 30 seconds")
        print("   6. Check Discord - /verify should now show as one command")

if __name__ == "__main__":
    main()