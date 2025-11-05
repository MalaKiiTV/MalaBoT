#!/usr/bin/env python3
"""
Apply final audit fixes systematically
"""
import re

def apply_final_fixes():
    with open('bot.py', 'r') as f:
        content = f.read()
    
    # Fix 1: Replace signal_handler frame parameter
    content = re.sub(r'def signal_handler\(signum, frame\):', 'def signal_handler(signum, _frame):', content)
    
    # Fix 2: Replace birthday role blocking sleep with scheduler
    old_birthday_code = '''               # Schedule role removal after 24 hours
               await asyncio.sleep(86400)  # 24 hours (TODO: Replace with persistent scheduler)
               if birthday_role in user.roles:
                   await user.remove_roles(birthday_role, reason="Birthday period ended")'''
    
    new_birthday_code = '''               # Schedule role removal after 24 hours using persistent scheduler
               removal_time = datetime.now() + timedelta(hours=24)
               self.scheduler.add_job(
                   self._remove_birthday_role,
                   'date',
                   run_date=removal_time,
                   args=[user.id, birthday_role.id, guild.id],
                   id=f"birthday_role_{user.id}_{int(datetime.now().timestamp())}",
                   replace_existing=True
               )'''
    
    content = content.replace(old_birthday_code, new_birthday_code)
    
    # Fix 3: Add the _remove_birthday_role method
    remove_birthday_method = '''    async def _remove_birthday_role(self, user_id: int, role_id: int, guild_id: int):
        """Remove birthday role from user after 24 hours."""
        try:
            # Get guild and user
            guild = self.get_guild(guild_id)
            if not guild:
                self.logger.warning(f"Guild {guild_id} not found for birthday role removal")
                return
                
            user = guild.get_member(user_id)
            if not user:
                self.logger.info(f"User {user_id} not found for birthday role removal")
                return
                
            # Get birthday role
            role = guild.get_role(role_id)
            if not role:
                self.logger.info(f"Birthday role {role_id} not found for removal")
                return
                
            # Remove role if user still has it
            if role in user.roles:
                await user.remove_roles(role, reason="Birthday period ended")
                self.logger.info(f"Removed birthday role from user {user_id}")
                
                # Log role removal
                await self.db_manager.log_event(
                    category='BDAY',
                    action='ROLE_REMOVED',
                    user_id=user_id,
                    details=f"Birthday role removed after 24 hours"
                )
                
        except Exception as e:
            self.logger.error(f"Error removing birthday role: {e}")

'''
    
    content = content.replace('    async def _send_daily_digest(self):', remove_birthday_method + '    async def _send_daily_digest(self):')
    
    # Fix 4: Update digest_data to use optimized stats
    old_digest_data = '''                'commands': len(recent_logs),'''
    new_digest_data = '''                'total_logs': stats['total_logs'],
                'critical_events': stats['critical_events'],
                'warnings': stats['warnings'],
                'moderation_actions': stats['moderation_actions'],
                'user_events': stats['user_events'],
                'commands': stats['total_logs'],'''
    
    content = content.replace(old_digest_data, new_digest_data)
    
    # Write the fixed content
    with open('bot.py', 'w') as f:
        f.write(content)
    
    print("All final audit fixes applied successfully!")

if __name__ == "__main__":
    apply_final_fixes()