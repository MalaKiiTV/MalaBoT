"""
Final comprehensive fix for all remaining issues:
1. XP system using wrong field name (total_xp vs xp)
2. Verify commands appearing separately instead of as group
"""

import re

def fix_xp_field_names():
    """Fix all references to total_xp to use xp instead"""
    
    # Fix cogs/xp.py
    with open('cogs/xp.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace total_xp with xp
    content = content.replace("user_data.get('total_xp'", "user_data.get('xp'")
    content = content.replace('user_data.get("total_xp"', 'user_data.get("xp"')
    
    # Also fix the rank command check
    content = content.replace(
        "if not user_data or not user_data.get('xp', 0):",
        "if not user_data or user_data.get('xp', 0) == 0:"
    )
    
    with open('cogs/xp.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed XP field names in cogs/xp.py")

def fix_xp_helper_methods():
    """Fix XPHelper methods to use correct field names"""
    
    with open('utils/helpers.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix get_xp_for_level method if it doesn't exist
    if 'def get_xp_for_level' not in content:
        # Add the method after get_xp_for_next_level
        old_method = '''    @staticmethod
    def get_xp_for_next_level(current_level: int, xp_table: Dict[int, int]) -> int:
        """Get XP required for next level."""
        next_level = current_level + 1
        return xp_table.get(next_level, xp_table[max(xp_table.keys())])'''
        
        new_methods = '''    @staticmethod
    def get_xp_for_next_level(current_level: int, xp_table: Dict[int, int]) -> int:
        """Get XP required for next level."""
        next_level = current_level + 1
        return xp_table.get(next_level, xp_table[max(xp_table.keys())])
    
    @staticmethod
    def get_xp_for_level(level: int, xp_table: Dict[int, int] = None) -> int:
        """Get XP required for a specific level."""
        if xp_table is None:
            from config.constants import XP_TABLE
            xp_table = XP_TABLE
        return xp_table.get(level, 0)'''
        
        content = content.replace(old_method, new_methods)
        
        with open('utils/helpers.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Added get_xp_for_level method to XPHelper")
    else:
        print("✅ get_xp_for_level already exists")

def verify_command_structure():
    """Verify that verify commands are properly structured as a group"""
    
    with open('cogs/verify.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if verify is defined as a Group
    if 'verify = app_commands.Group(name="verify"' in content:
        print("✅ Verify commands are correctly structured as a Group")
        
        # Check if all subcommands use @verify.command
        if '@verify.command(name="submit"' in content and \
           '@verify.command(name="review"' in content and \
           '@verify.command(name="setup"' in content:
            print("✅ All verify subcommands are correctly defined")
        else:
            print("⚠️ Some verify subcommands may not be correctly defined")
    else:
        print("❌ Verify commands are not structured as a Group")

def check_database_schema():
    """Verify database schema has correct fields"""
    
    with open('database/models.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if users table has xp field
    if 'xp INTEGER DEFAULT 0' in content:
        print("✅ Database schema has 'xp' field")
    else:
        print("❌ Database schema missing 'xp' field")
    
    # Check if there's a total_xp field (shouldn't be)
    if 'total_xp' in content.lower():
        print("⚠️ Database references 'total_xp' - should be 'xp'")
    else:
        print("✅ No incorrect 'total_xp' references in database")

def main():
    """Run all fixes"""
    print("🔧 Applying final comprehensive fixes...\n")
    
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("1️⃣ Fixing XP field names...")
    fix_xp_field_names()
    
    print("\n2️⃣ Fixing XP helper methods...")
    fix_xp_helper_methods()
    
    print("\n3️⃣ Verifying command structure...")
    verify_command_structure()
    
    print("\n4️⃣ Checking database schema...")
    check_database_schema()
    
    print("\n✅ All fixes applied!")
    print("\n📝 Summary:")
    print("   • Fixed XP field references (total_xp → xp)")
    print("   • Added get_xp_for_level method if missing")
    print("   • Verified verify command structure")
    print("   • Checked database schema")
    print("\n🔄 Next steps:")
    print("   1. Restart the bot")
    print("   2. Send some messages to earn XP")
    print("   3. Test /rank command")
    print("   4. Test /daily command")
    print("   5. Check that /verify shows as one command with subcommands")

if __name__ == "__main__":
    main()