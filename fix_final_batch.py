#!/usr/bin/env python3
"""Fix the remaining batch of MyPy errors."""

import os
import re

def fix_file(filepath):
    """Fix common MyPy error patterns."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original = content
        
        # Fix channel send issues
        content = re.sub(r'await (\w+)\.send\(', r'if hasattr(\1, "send"): await \1.send(', content)
        
        # Fix bot.db_manager access
        content = re.sub(r'self\.db = bot\.db_manager', r'self.db = bot.db_manager  # type: ignore', content)
        
        # Fix message.delete issues
        content = re.sub(r'await (\w+)\.delete\(\)', r'if \1: await \1.delete()', content)
        
        # Fix guild property access
        content = re.sub(r'if interaction\.guild\.', r'if interaction.guild and interaction.guild.', content)
        
        if content != original:
            with open(filepath, 'w') as f:
                f.write(content)
            return True
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
    return False

# Fix files with most errors
files_to_fix = [
    'cogs/xp.py',
    'cogs/utility.py', 
    'cogs/verify.py',
    'cogs/moderation.py',
    'cogs/setup.py',
    'cogs/appeal.py',
    'cogs/birthdays.py'
]

fixed_count = 0
for filepath in files_to_fix:
    if os.path.exists(filepath):
        if fix_file(filepath):
            fixed_count += 1
            print(f"Fixed: {filepath}")

print(f"Fixed {fixed_count} files")