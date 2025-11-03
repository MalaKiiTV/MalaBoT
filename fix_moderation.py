import sqlite3

def add_log_moderation_method():
    """Directly add the log_moderation_action method to the DatabaseManager."""
    with open('database/models.py', 'r') as f:
        lines = f.readlines()
    
    # Find the line with "async def get_flag" and insert before it
    for i, line in enumerate(lines):
        if 'async def get_flag' in line:
            # Insert the new method before get_flag
            indent = '    '
            new_method = [
                indent + 'async def log_moderation_action(self, moderator_id: int, target_id: int, action: str, reason: str = None, guild_id: int = None):\n',
                indent + '    """Log moderation action (wrapper for log_event)."""\n',
                indent + '    await self.log_event(\n',
                indent + '        category="MODERATION",\n',
                indent + '        action=action,\n',
                indent + '        user_id=moderator_id,\n',
                indent + '        target_id=target_id,\n',
                indent + '        details=reason,\n',
                indent + '        guild_id=guild_id\n',
                indent + '    )\n',
                '\n'
            ]
            lines[i:i] = new_method
            break
    
    with open('database/models.py', 'w') as f:
        f.writelines(lines)
    
    print("Added log_moderation_action method")

if __name__ == "__main__":
    add_log_moderation_method()