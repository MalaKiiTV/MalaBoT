"""Emergency fix for log_event method"""

with open('database/models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and fix the broken log_event method
old_text = '''        await conn.commit()
   
   
           """Log an event to the audit log."""
           conn = await self.get_connection()
           await conn.execute("""
               INSERT INTO audit_log (category, action, user_id, target_id, channel_id, details, guild_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)
           """, (category, action, user_id, target_id, channel_id, details, guild_id))
           await conn.commit()
       
       async def get_audit_logs'''

new_text = '''        await conn.commit()
    
    async def log_event(self, category: str, action: str, user_id: int = None,
                       target_id: int = None, channel_id: int = None,
                       details: str = None, guild_id: int = None):
        """Log an event to the audit log."""
        conn = await self.get_connection()
        await conn.execute("""
            INSERT INTO audit_log (category, action, user_id, target_id, channel_id, details, guild_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (category, action, user_id, target_id, channel_id, details, guild_id))
        await conn.commit()
    
    async def get_audit_logs'''

content = content.replace(old_text, new_text)

with open('database/models.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed log_event method!")