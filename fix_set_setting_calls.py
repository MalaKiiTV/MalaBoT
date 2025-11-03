import re

def fix_set_setting_calls():
    """Fix all set_setting calls to use correct parameter order."""
    with open('cogs/setup.py', 'r') as f:
        content = f.read()
    
    # Pattern to match set_setting calls with old format
    pattern = r'await \w+\.db\.set_setting\([^"]*"([^"]+)_{[^}]+}"[^,]*,\s*([^)]+)\)'
    
    def replacement(match):
        key_base = match.group(1)  # e.g., "verify_channel"
        value = match.group(2)     # e.g., "channel.id" or "None"
        # Extract variable name for guild_id
        full_match = match.group(0)
        if 'self.guild_id' in full_match:
            guild_param = 'self.guild_id'
        elif 'guild_id' in full_match:
            guild_param = 'guild_id'
        else:
            guild_param = 'self.guild_id'
        
        return f'await self.db.set_setting("{key_base}", {value}, {guild_param})'
    
    new_content = re.sub(pattern, replacement, content)
    
    with open('cogs/setup.py', 'w') as f:
        f.write(new_content)
    
    print("Fixed set_setting calls")

if __name__ == "__main__":
    fix_set_setting_calls()