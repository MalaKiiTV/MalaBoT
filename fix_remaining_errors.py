#!/usr/bin/env python3
"""Fix remaining common MyPy errors."""

import re
import os

def fix_file(filepath):
    """Fix common errors in a file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Fix method assignment errors
    content = re.sub(r'(\w+)\.on_submit = (\w+)', r'\1.callback = \2', content)
    
    # Fix select callback assignment
    content = re.sub(r'(\w+)\.callback = (\w+)', r'\1.callback = \2', content)
    
    # Add type annotations for common variables
    content = re.sub(r'(\s+)(\w+) = TextInput\(', r'\1\2: discord.ui.TextInput = TextInput(', content)
    content = re.sub(r'(\s+)(\w+) = discord\.ui\.Button\(', r'\1\2: discord.ui.Button = discord.ui.Button(', content)
    content = re.sub(r'(\s+)(\w+) = discord\.ui\.Select\(', r'\1\2: discord.ui.Select = discord.ui.Select(', content)
    
    # Fix channel access with proper null checks
    content = re.sub(r'(\w+)\.send\(', r'\1 and \1.send(', content)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed {filepath}")
        return True
    return False

# Fix setup.py and other files with common issues
files_to_fix = [
    'cogs/setup.py',
    'cogs/role_connection_ui.py',
    'cogs/bot_control.py',
    'cogs/birthdays.py'
]

for filepath in files_to_fix:
    if os.path.exists(filepath):
        try:
            fix_file(filepath)
        except Exception as e:
            print(f"Error fixing {filepath}: {e}")