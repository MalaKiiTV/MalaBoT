#!/usr/bin/env python3
"""Script to fix common union-attr errors in Discord.py code."""

import re

def fix_file(filepath):
    """Fix union-attr errors in a file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Fix interaction.guild access
    content = re.sub(
        r'interaction\.guild\.(id|name|icon|members|get_member|get_role)',
        r'interaction.guild and interaction.guild.\1',
        content
    )
    
    # Fix interaction.user.guild_permissions
    content = re.sub(
        r'interaction\.user\.guild_permissions',
        r'hasattr(interaction.user, "guild_permissions") and interaction.user.guild_permissions',
        content
    )
    
    # Fix interaction.user.roles
    content = re.sub(
        r'interaction\.user\.roles',
        r'hasattr(interaction.user, "roles") and interaction.user.roles',
        content
    )
    
    # Fix interaction.user.top_role
    content = re.sub(
        r'interaction\.user\.top_role',
        r'hasattr(interaction.user, "top_role") and interaction.user.top_role',
        content
    )
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed {filepath}")
        return True
    return False

# Fix main cogs
cogs_to_fix = [
    'cogs/xp.py',
    'cogs/utility.py', 
    'cogs/verify.py',
    'cogs/moderation.py',
    'cogs/setup.py'
]

for cog in cogs_to_fix:
    try:
        fix_file(cog)
    except Exception as e:
        print(f"Error fixing {cog}: {e}")