"""
COMPLETE MalaBoT Diagnostic Script
Run this ONCE and send me the full output
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {str(e)}"

def check_file_exists(filepath):
    """Check if file exists and get size"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        return f"✅ EXISTS ({size} bytes)"
    return "❌ NOT FOUND"

def read_file_lines(filepath, num_lines=20):
    """Read first N lines of a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [f.readline().strip() for _ in range(num_lines)]
            return '\n'.join(lines)
    except Exception as e:
        return f"Error reading: {str(e)}"

def check_cog_commands(filepath):
    """Extract commands from a cog file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        commands = re.findall(r'@app_commands\.command\(name=["\'](\w+)["\']', content)
        
        results = []
        for cmd in commands:
            has_default_perms = f'default_permissions' in content
            has_owner_check = 'is_owner' in content
            results.append({
                'name': cmd,
                'has_default_perms': has_default_perms,
                'has_owner_check': has_owner_check
            })
        return results
    except Exception as e:
        return [{'error': str(e)}]

print("="*80)
print("MALABOT COMPLETE DIAGNOSTIC REPORT")
print("="*80)
print()

# 1. ENVIRONMENT CHECK
print("1. ENVIRONMENT CHECK")
print("-"*80)
print(f"Python Version: {sys.version}")
print(f"Current Directory: {os.getcwd()}")
print(f"Python Executable: {sys.executable}")
print()

# 2. FILE STRUCTURE CHECK
print("2. FILE STRUCTURE CHECK")
print("-"*80)
files_to_check = [
    'bot.py',
    '.env',
    '.env.example',
    'requirements.txt',
    'update.bat',
    'cogs/owner.py',
    'cogs/moderation.py',
    'cogs/utility.py',
    'cogs/fun.py',
    'cogs/birthdays.py',
    'cogs/welcome.py',
    'cogs/xp.py',
]

for filepath in files_to_check:
    print(f"{filepath:30} {check_file_exists(filepath)}")
print()

# 3. .ENV CONFIGURATION CHECK
print("3. .ENV CONFIGURATION CHECK")
print("-"*80)
if os.path.exists('.env'):
    print("Reading .env file (first 15 lines, tokens hidden):")
    with open('.env', 'r') as f:
        for i, line in enumerate(f):
            if i >= 15:
                break
            if 'TOKEN' in line and '=' in line:
                key, val = line.split('=', 1)
                if val.strip() and val.strip() != 'your_bot_token_here':
                    print(f"{key}=***HIDDEN*** (SET)")
                else:
                    print(f"{key}=NOT SET")
            else:
                print(line.strip())
else:
    print("❌ .env file not found!")
print()

# 4. GIT STATUS
print("4. GIT STATUS")
print("-"*80)
print(run_command("git status"))
print("\nGit Remote:")
print(run_command("git remote -v"))
print()

# 5. INSTALLED PACKAGES
print("5. INSTALLED PACKAGES")
print("-"*80)
print(run_command("pip list | findstr discord"))
print()

# 6. COG FILES ANALYSIS
print("6. COG FILES COMMAND ANALYSIS")
print("-"*80)

cog_files = [
    'cogs/owner.py',
    'cogs/moderation.py',
    'cogs/utility.py',
    'cogs/fun.py',
    'cogs/birthdays.py',
    'cogs/welcome.py',
    'cogs/xp.py',
]

for cog_file in cog_files:
    if os.path.exists(cog_file):
        print(f"\n{cog_file}:")
        commands = check_cog_commands(cog_file)
        for cmd in commands:
            if 'error' in cmd:
                print(f"  Error: {cmd['error']}")
            else:
                perms = "✅" if cmd['has_default_perms'] else "❌"
                owner = "✅" if cmd['has_owner_check'] else "❌"
                print(f"  /{cmd['name']:20} default_perms:{perms}  owner_check:{owner}")
print()

# 7. CHECK OWNER.PY SPECIFICALLY
print("7. OWNER.PY DETAILED CHECK")
print("-"*80)
if os.path.exists('cogs/owner.py'):
    print("First 50 lines of owner.py:")
    print(read_file_lines('cogs/owner.py', 50))
else:
    print("❌ owner.py not found!")
print()

# 8. CHECK MODERATION.PY SPECIFICALLY  
print("8. MODERATION.PY DETAILED CHECK")
print("-"*80)
if os.path.exists('cogs/moderation.py'):
    print("First 50 lines of moderation.py:")
    print(read_file_lines('cogs/moderation.py', 50))
else:
    print("❌ moderation.py not found!")
print()

# 9. RECENT LOGS
print("9. RECENT BOT LOGS")
print("-"*80)
log_file = 'data/logs/latest.log'
if os.path.exists(log_file):
    print(f"Last 30 lines of {log_file}:")
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[-30:]:
                print(line.strip())
    except Exception as e:
        print(f"Error reading log: {e}")
else:
    print(f"❌ {log_file} not found!")
print()

# 10. DISCORD COMMAND SYNC STATUS
print("10. CHECKING FOR DUPLICATE COMMANDS")
print("-"*80)
print("To check for duplicate commands in Discord, we need to connect to the bot.")
print("This diagnostic script cannot do that without running the full bot.")
print("However, duplicate commands usually happen when:")
print("  1. Commands are synced multiple times")
print("  2. Bot is in multiple servers with different command configs")
print("  3. Global commands conflict with guild-specific commands")
print()

# 11. SUMMARY
print("="*80)
print("DIAGNOSTIC COMPLETE")
print("="*80)
print()
print("COPY ALL OUTPUT ABOVE AND SEND IT TO ME")
print()
print("="*80)