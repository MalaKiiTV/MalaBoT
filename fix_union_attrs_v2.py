#!/usr/bin/env python3
"""Script to fix common union-attr errors more carefully."""

import re

def fix_file(filepath):
    """Fix union-attr errors in a file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Fix interaction.guild access patterns
    patterns = [
        (r'(\s+)if interaction\.guild\.owner_id ==', r'\1if interaction.guild and interaction.guild.owner_id =='),
        (r'(\s+)if interaction\.guild\.members:', r'\1if interaction.guild and interaction.guild.members:'),
        (r'(\s+)if interaction\.guild\.get_member\(', r'\1if interaction.guild and interaction.guild.get_member('),
        (r'(\s+)if interaction\.guild\.get_role\(', r'\1if interaction.guild and interaction.guild.get_role('),
        (r'(\s+)if interaction\.user\.guild_permissions\.', r'\1if hasattr(interaction.user, "guild_permissions") and interaction.user.guild_permissions.'),
        (r'(\s+)if interaction\.user\.roles', r'\1if hasattr(interaction.user, "roles") and interaction.user.roles'),
        (r'(\s+)if interaction\.user\.top_role', r'\1if hasattr(interaction.user, "top_role") and interaction.user.top_role'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed {filepath}")
        return True
    return False

# Fix remaining cogs
cogs_to_fix = [
    'cogs/moderation.py',
    'cogs/utility.py',
    'cogs/verify.py',
    'cogs/setup.py',
    'cogs/appeal.py'
]

for cog in cogs_to_fix:
    try:
        fix_file(cog)
    except Exception as e:
        print(f"Error fixing {cog}: {e}")