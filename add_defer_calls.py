def add_defer_calls():
    """Add defer() calls to all setup methods to prevent timeouts."""
    with open('cogs/setup.py', 'r') as f:
        content = f.read()
    
    # Methods that need defer calls
    methods = [
        'setup_verification',
        'setup_welcome', 
        'setup_birthday',
        'setup_xp',
        'setup_general',
        'setup_role_connections',
        'view_config'
    ]
    
    for method in methods:
        # Find the method definition and add defer call after it
        pattern = f'(    async def {method}\\(self, interaction: discord\\.Interaction\\):[^\\n]*\\n[^\\n]*\\n)'
        replacement = f'\\1        await interaction.response.defer(ephemeral=True)\\n'
        content = __import__('re').sub(pattern, replacement, content)
    
    # Change send_message to followup.send since we're using defer
    content = content.replace('await interaction.response.send_message(', 'await interaction.followup.send(')
    
    with open('cogs/setup.py', 'w') as f:
        f.write(content)
    
    print("Added defer calls and fixed response methods")

if __name__ == "__main__":
    add_defer_calls()