#!/usr/bin/env python3
"""
Deployment script to apply fixes to MalaBoT
"""

import os
import shutil
import sys

def deploy_fixes():
    """Deploy the fixed files to the bot directory."""
    print("🔧 Deploying MalaBoT fixes...")
    
    # Files to copy
    files_to_copy = [
        ("fixes/cogs/welcome.py", "cogs/welcome.py"),
        ("fixes/cogs/moderation.py", "cogs/moderation.py"),
        ("fixes/cogs/xp.py", "cogs/xp.py"),
        ("fixes/cogs/utility.py", "cogs/utility.py")
    ]
    
    # Copy files
    for src, dst in files_to_copy:
        if os.path.exists(src):
            try:
                shutil.copy2(src, dst)
                print(f"✅ Updated {dst}")
            except Exception as e:
                print(f"❌ Failed to update {dst}: {e}")
                return False
        else:
            print(f"❌ Source file {src} not found")
            return False
    
    print("✅ All fixes deployed successfully!")
    print("\n📝 Next steps:")
    print("1. Update your .env file with your Discord bot token and owner ID")
    print("2. Run the update script (update.bat on Windows or ./update_droplet.sh on Linux)")
    print("3. Restart your bot")
    
    return True

if __name__ == "__main__":
    success = deploy_fixes()
    sys.exit(0 if success else 1)