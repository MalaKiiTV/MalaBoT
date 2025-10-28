"""
Remove duplicate methods from helpers.py and database/models.py
"""

def remove_duplicate_check_cooldown():
    """Remove duplicate check_cooldown method"""
    with open('utils/helpers.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find all occurrences of check_cooldown
    indices = []
    for i, line in enumerate(lines):
        if 'def check_cooldown(self, user_id: int, command: str, cooldown_seconds: int)' in line:
            indices.append(i)
    
    if len(indices) > 1:
        # Remove the second occurrence (lines from second def to before next class/method)
        start = indices[1]
        end = start + 1
        
        # Find the end of the duplicate method
        indent_level = len(lines[start]) - len(lines[start].lstrip())
        for i in range(start + 1, len(lines)):
            current_indent = len(lines[i]) - len(lines[i].lstrip())
            if lines[i].strip() and current_indent <= indent_level and 'def ' in lines[i]:
                end = i
                break
            elif lines[i].strip() and current_indent < indent_level and 'class ' in lines[i]:
                end = i
                break
        
        # Remove lines from start to end
        del lines[start:end]
        
        with open('utils/helpers.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ Removed duplicate check_cooldown method (lines {start+1} to {end})")
        return True
    else:
        print("✅ No duplicate check_cooldown found")
        return True

def remove_duplicate_database_methods():
    """Remove duplicate get_leaderboard and set_daily_claimed methods"""
    with open('database/models.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find all occurrences
    leaderboard_indices = []
    daily_indices = []
    
    for i, line in enumerate(lines):
        if 'async def get_leaderboard(self, guild_id: int, limit: int = 10)' in line:
            leaderboard_indices.append(i)
        elif 'async def set_daily_claimed(self, user_id: int, guild_id: int)' in line:
            daily_indices.append(i)
    
    removed = False
    
    # Remove duplicates (keep first, remove rest)
    if len(leaderboard_indices) > 1:
        # Remove from last to first to maintain line numbers
        for idx in reversed(leaderboard_indices[1:]):
            start = idx
            end = start + 1
            
            # Find end of method
            indent_level = len(lines[start]) - len(lines[start].lstrip())
            for i in range(start + 1, len(lines)):
                current_indent = len(lines[i]) - len(lines[i].lstrip())
                if lines[i].strip() and current_indent <= indent_level and 'async def ' in lines[i]:
                    end = i
                    break
            
            del lines[start:end]
            removed = True
        
        print(f"✅ Removed {len(leaderboard_indices)-1} duplicate get_leaderboard method(s)")
    
    if len(daily_indices) > 1:
        # Reload lines after previous deletion
        with open('database/models.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find indices again
        daily_indices = []
        for i, line in enumerate(lines):
            if 'async def set_daily_claimed(self, user_id: int, guild_id: int)' in line:
                daily_indices.append(i)
        
        # Remove from last to first
        for idx in reversed(daily_indices[1:]):
            start = idx
            end = start + 1
            
            # Find end of method
            indent_level = len(lines[start]) - len(lines[start].lstrip())
            for i in range(start + 1, len(lines)):
                current_indent = len(lines[i]) - len(lines[i].lstrip())
                if lines[i].strip() and current_indent <= indent_level and 'async def ' in lines[i]:
                    end = i
                    break
            
            del lines[start:end]
            removed = True
        
        print(f"✅ Removed {len(daily_indices)-1} duplicate set_daily_claimed method(s)")
    
    if removed:
        with open('database/models.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
    else:
        print("✅ No duplicate database methods found")
    
    return True

if __name__ == "__main__":
    print("🧹 Removing duplicate methods...\n")
    remove_duplicate_check_cooldown()
    remove_duplicate_database_methods()
    print("\n✅ Cleanup complete!")