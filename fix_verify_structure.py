"""
Fix verify command structure to properly show as parent with subcommands
The issue: Group defined as class variable doesn't always register correctly
Solution: Define Group in __init__ and add it to the tree
"""

def fix_verify_cog():
    """Rewrite verify cog to properly register the Group"""
    
    with open('cogs/verify.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the class definition and Group initialization
    old_init = '''class Verify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db_manager

    verify = app_commands.Group(name="verify", description="Warzone verification system.")'''
    
    new_init = '''class Verify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db_manager
        
        # Create the verify group
        self.verify = app_commands.Group(name="verify", description="Warzone verification system.")
        
        # Add commands to the group
        self.verify.add_command(app_commands.Command(
            name="submit",
            description="Submit your Warzone verification screenshot.",
            callback=self.submit
        ))
        self.verify.add_command(app_commands.Command(
            name="review",
            description="Review a pending verification (staff only).",
            callback=self.review
        ))
        self.verify.add_command(app_commands.Command(
            name="setup",
            description="Set up the verification review channel (admin only).",
            callback=self.setup_command
        ))
        
        # Add the group to the bot's command tree
        bot.tree.add_command(self.verify)'''
    
    content = content.replace(old_init, new_init)
    
    # Now we need to remove the @verify.command decorators and make them regular methods
    # Replace @verify.command decorators
    content = content.replace('@verify.command(name="submit"', '@app_commands.describe(activision_id="Your Activision ID", platform="Your gaming platform")\n    async def submit(self, interaction: discord.Interaction, activision_id: str, platform: str):\n        """Submit')
    content = content.replace('@verify.command(name="review"', 'async def review(self, interaction: discord.Interaction, user: discord.Member, decision: str):\n        """Review')
    content = content.replace('@verify.command(name="setup"', 'async def setup_command(self, interaction: discord.Interaction, channel: discord.TextChannel):\n        """Set up')
    
    # Actually, this approach is getting too complex. Let me try a simpler fix.
    print("⚠️ The current approach is too complex. Let me try a different solution...")
    return False

def create_proper_verify_cog():
    """Create a properly structured verify cog from scratch"""
    
    print("Creating a new verify cog structure...")
    
    # Read the current file to preserve the logic
    with open('cogs/verify.py', 'r', encoding='utf-8') as f:
        original = f.read()
    
    # The issue is simpler than I thought - we just need to ensure the Group
    # is added to the tree in the setup function
    
    # Check if the setup function adds the group to the tree
    if 'bot.tree.add_command' not in original:
        print("⚠️ The Group is not being added to the command tree!")
        print("   This is why it's showing as separate commands.")
        
        # Find the setup function
        setup_start = original.find('async def setup(bot: commands.Bot):')
        if setup_start != -1:
            # Replace the setup function
            old_setup = '''async def setup(bot: commands.Bot):
    await bot.add_cog(Verify(bot))'''
            
            new_setup = '''async def setup(bot: commands.Bot):
    cog = Verify(bot)
    await bot.add_cog(cog)
    # Ensure the verify group is added to the command tree
    bot.tree.add_command(cog.verify)'''
            
            original = original.replace(old_setup, new_setup)
            
            with open('cogs/verify.py', 'w', encoding='utf-8') as f:
                f.write(original)
            
            print("✅ Fixed setup function to add Group to command tree")
            return True
    
    return False

def main():
    """Main execution"""
    print("🔧 Fixing verify command structure...\n")
    
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    if create_proper_verify_cog():
        print("\n✅ Verify cog fixed!")
        print("\n📝 What changed:")
        print("   • Modified setup() to explicitly add the Group to command tree")
        print("   • This ensures Discord recognizes it as a parent command")
        print("\n🔄 Next steps:")
        print("   1. Restart your bot")
        print("   2. Wait 30 seconds")
        print("   3. Check Discord - /verify should now show as ONE command")
    else:
        print("\n⚠️ Could not apply automatic fix")
        print("   Manual intervention may be needed")

if __name__ == "__main__":
    main()