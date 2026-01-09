"""
Supabase database models for MalaBoT.
Drop-in replacement for SQLite models.
"""

from supabase import create_client, Client
from typing import Optional, Any
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class DatabaseManager:
    """Manages all database operations for MalaBoT using Supabase."""

    def __init__(self, db_path: str = None):
        # db_path is ignored but kept for compatibility
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        # Note: guild_id removed to ensure per-guild operations only

    async def get_connection(self):
        """Compatibility method - returns self since Supabase doesn't need connections."""
        return self

    async def initialize(self) -> None:
        """Initialize database - tables already exist in Supabase."""
        await self._initialize_roast_xp()

    async def _initialize_roast_xp(self) -> None:
        """Initialize roast XP table with default values."""
        try:
            result = self.supabase.table('roast_xp').select('*').execute()
            if len(result.data) == 0:
                self.supabase.table('roast_xp').insert([
                    {'action': 'roast_success', 'base_xp': 15},
                    {'action': 'roast_fail', 'base_xp': 5},
                    {'action': 'defend_success', 'base_xp': 10},
                    {'action': 'defend_fail', 'base_xp': 3},
                    {'action': 'compliment', 'base_xp': 8}
                ]).execute()
        except Exception:
            pass  # Already exists

    # === XP METHODS ===

    async def get_user_xp(self, user_id: int, guild_id: int) -> int:
        """Get user's current XP."""
        result = self.supabase.table('users').select('xp').eq('user_id', user_id).eq('guild_id', guild_id).execute()
        
        if not result.data:
            # Create user if doesn't exist
            self.supabase.table('users').insert({
                'user_id': user_id,
                'guild_id': str(guild_id) if guild_id else None,
                'username': 'Unknown',
                'discriminator': '0',
                'xp': 0,
                'level': 0
            }).execute()
            return 0
        
        return result.data[0]['xp']

    async def set_user_xp(self, user_id: int, amount: int, guild_id: int) -> tuple[int, int]:
        """Set user's XP to a specific amount and calculate level."""
        from src.config.constants import XP_TABLE

        # Calculate level
        level = 1
        for lvl, req_xp in enumerate(XP_TABLE):
            if amount >= req_xp:
                level = lvl + 1
            else:
                break

        # Upsert user
        self.supabase.table('users').upsert({
            'user_id': user_id,
            'guild_id': str(guild_id) if guild_id else None,
            'username': 'Unknown',
            'discriminator': '0',
            'xp': amount,
            'level': level
        }).execute()

        return amount, level

    async def update_user_xp(self, user_id: int, xp_change: int, guild_id: int = None) -> tuple[int, int, bool]:
        """Update user's XP and recalculate level. Returns (new_xp, new_level, leveled_up)."""
        # guild_id required parameter
        
        # Get current XP and level
        result = self.supabase.table('users').select('xp, level').eq('user_id', user_id).eq('guild_id', guild_id).execute()
        
        if not result.data:
            # Create user
            self.supabase.table('users').insert({
                'user_id': user_id,
                'guild_id': str(guild_id) if guild_id else None,
                'username': 'Unknown',
                'discriminator': '0',
                'xp': 0,
                'level': 0
            }).execute()
            current_xp = 0
            old_level = 0
        else:
            current_xp = result.data[0]['xp']
            old_level = result.data[0]['level']

        # Calculate new XP
        new_xp = max(0, current_xp + xp_change)

        # Get progression type
        progression_type = await self.get_setting("xp_progression_type", guild_id) or "custom"
        new_level = await self._calculate_level_from_xp(new_xp, progression_type)

        leveled_up = new_level > old_level

        # Update
        self.supabase.table('users').update({
            'xp': new_xp,
            'level': new_level
        }).eq('user_id', user_id).eq('guild_id', guild_id).execute()

        return new_xp, new_level, leveled_up

    async def _calculate_level_from_xp(self, xp: int, progression_type: str) -> int:
        """Calculate level from XP based on progression type."""
        if progression_type == "basic":
            if xp < 50:
                return 0
            return ((xp - 50) // 100) + 1

        elif progression_type == "gradual":
            if xp < 50:
                return 0

            level = 1
            total_xp_needed = 50

            while level < 1000:
                xp_for_next_level = (level + 1) * 100
                total_xp_needed += xp_for_next_level

                if xp < total_xp_needed:
                    return level
                level += 1

            return 1000

        elif progression_type == "custom":
            from src.config.constants import XP_TABLE

            if xp < 50:
                return 0

            level = 0
            for lvl in sorted(XP_TABLE.keys()):
                if xp >= XP_TABLE[lvl]:
                    level = lvl
                else:
                    break
            return level

        else:
            return await self._calculate_level_from_xp(xp, "custom")

    async def remove_user_xp(self, user_id: int, amount: int, guild_id: int) -> tuple[int, int]:
        """Remove XP from user."""
        return await self.update_user_xp(user_id, -amount, guild_id)

    async def get_user_level(self, user_id: int, guild_id: int) -> int:
        """Get user's current level."""
        result = self.supabase.table('users').select('level').eq('user_id', user_id).eq('guild_id', guild_id).execute()
        return result.data[0]['level'] if result.data else 1

    async def get_user_rank(self, user_id: int, guild_id: int) -> int:
        """Get user's rank in the guild."""
        result = self.supabase.table('users').select('user_id').eq('guild_id', guild_id).gt('xp', 0).order('xp', desc=True).execute()
        
        for rank, user in enumerate(result.data, 1):
            if user['user_id'] == user_id:
                return rank
        
        return len(result.data) + 1

    # === LEADERBOARD METHODS ===

    async def get_leaderboard(self, guild_id: int, limit: int = 10) -> list:
        """Get XP leaderboard for a guild."""
        result = self.supabase.table('users').select('user_id, xp, level').eq('guild_id', guild_id).gt('xp', 0).order('xp', desc=True).limit(limit).execute()
        return [(r['user_id'], r['xp'], r['level']) for r in result.data]

    # === DAILY CHECKIN METHODS ===

    async def get_daily_checkin(self, user_id: int, guild_id: int) -> Optional[tuple]:
        """Get user daily checkin data."""
        result = self.supabase.table('daily_checkins').select('*').eq('user_id', user_id).eq('guild_id', guild_id).execute()
        if result.data:
            r = result.data[0]
            return (r.get('last_checkin'), r.get('checkin_streak', 0))
        return None

    async def update_daily_checkin(self, user_id: int, last_checkin: str, streak: int, guild_id: int) -> None:
        """Update user daily checkin."""
        self.supabase.table('daily_checkins').upsert({
            'user_id': user_id,
            'guild_id': str(guild_id) if guild_id else None,
            'last_checkin': last_checkin,
            'checkin_streak': streak
        }, on_conflict='user_id,guild_id').execute()


    async def reset_all_xp(self, guild_id: int) -> None:
        """Reset all XP for a guild."""
        self.supabase.table('users').update({'xp': 0, 'level': 0}).eq('guild_id', guild_id).execute()

    async def get_user_count(self, guild_id: int) -> int:
        """Get count of users with XP."""
        result = self.supabase.table('users').select('user_id', count='exact').eq('guild_id', guild_id).gt('xp', 0).execute()
        return result.count if hasattr(result, 'count') else len(result.data)

    async def get_checkin_count(self, guild_id: int) -> int:
        """Get count of daily checkins."""
        result = self.supabase.table('daily_checkins').select('user_id', count='exact').eq('guild_id', guild_id).execute()
        return result.count if hasattr(result, 'count') else len(result.data)

    async def reset_all_checkins(self, guild_id: int) -> None:
        """Reset all daily checkins."""
        self.supabase.table('daily_checkins').delete().eq('guild_id', guild_id).execute()

    async def get_level_roles(self, guild_id: int) -> list:
        """Get level roles for a guild."""
        result = self.supabase.table('level_roles').select('*').eq('guild_id', guild_id).order('level').execute()
        return [(r['level'], r['role_id']) for r in result.data]

    # === USER METHODS ===

    async def get_user(self, user_id: int, guild_id: int) -> Optional[dict]:
        """Get user data."""
        result = self.supabase.table('users').select('*').eq('user_id', user_id).eq('guild_id', guild_id).execute()
        return result.data[0] if result.data else None

    # === BIRTHDAY METHODS ===

    async def set_birthday(self, user_id: int, birthday: str, guild_id: int, timezone: str = "UTC") -> None:
        """Set user birthday."""
        # Convert MM-DD to full date (2000-MM-DD)
        if len(birthday.split('-')) == 2:
            month, day = birthday.split("-")
            birthday = f"2000-{month.zfill(2)}-{day.zfill(2)}"

        # Check if birthday exists
        result = self.supabase.table('birthdays').select('id').eq('user_id', user_id).eq('guild_id', guild_id).execute()
    
        if result.data:
            # Update existing
            self.supabase.table("birthdays").update({
                "birthday": birthday,
                "timezone": timezone
            }).eq("user_id", user_id).eq("guild_id", guild_id).execute()
        else:
            # Insert new
            self.supabase.table("birthdays").insert({
                "user_id": user_id,
                "guild_id": guild_id,
                "birthday": birthday,
                "timezone": timezone
            }).execute()


    async def set_user_birthday(self, user_id: int, birthday: str, guild_id: int) -> bool:
        """Set user birthday (returns success status)."""
        try:
            await self.set_birthday(user_id, birthday, guild_id)
            return True
        except Exception as e:
            print(f"ERROR setting birthday: {e}")
            import traceback
            traceback.print_exc()
            return False



    async def get_birthday(self, user_id: int, guild_id: int) -> Optional[tuple]:
        """Get user birthday."""
        result = self.supabase.table('birthdays').select('*').eq('user_id', user_id).eq('guild_id', guild_id).execute()
        if result.data:
            row = result.data[0]
            # Return as tuple for compatibility (id, user_id, birthday, timezone, announced_year, created_at)
            return (row['id'], row['user_id'], row['birthday'], row.get('timezone', 'UTC'), row.get('announced_year'), row.get('created_at'))
        return None

    async def get_user_birthday(self, user_id: int, guild_id: int) -> Optional[tuple]:
        """Get user birthday (alias)."""
        return await self.get_birthday(user_id, guild_id)

    async def get_all_birthdays(self, guild_id: int) -> list:
        """Get all birthdays."""
        result = self.supabase.table('birthdays').select('*').eq('guild_id', guild_id).order('birthday').execute()
        return [(r['id'], r['user_id'], r['birthday'], r.get('timezone', 'UTC'), r.get('announced_year'), r.get('created_at')) for r in result.data]

    async def get_today_birthdays(self, guild_id: int, today: Optional[str] = None) -> list:
        """Get today's birthdays in MM-DD format."""
        # Supabase stores as 2000-MM-DD, we need to match MM-DD
        if today:
            # today is in MM-DD format
            result = self.supabase.table('birthdays').select('user_id').eq('guild_id', guild_id).like('birthday', f'%{today}').execute()
        else:
            # Get current MM-DD
            current_mmdd = (current_date or datetime.now()).strftime('%m-%d')
            result = self.supabase.table('birthdays').select('user_id').eq('guild_id', guild_id).like('birthday', f'%{current_mmdd}').execute()
        
        return [(r['user_id'],) for r in result.data]

    async def get_unannounced_birthdays(self, guild_id: int, current_date: datetime) -> list:
        """Get birthdays that haven't been announced today."""
        current_mmdd = current_date.strftime('%m-%d')
        today_str = current_date.strftime('%Y-%m-%d')
        result = self.supabase.table('birthdays').select('user_id, birthday, announced_date').eq('guild_id', guild_id).like('birthday', f'%{current_mmdd}').execute()

        # Filter for unannounced today
        unannounced = []
        for r in result.data:
            if r.get('announced_date') != today_str:
                unannounced.append((r['user_id'], r['birthday']))
                unannounced.append((r['user_id'], r['birthday']))

        return unannounced

    async def mark_birthday_announced(self, user_id: int, guild_id: int, announced_date: str) -> None:
        """Mark that a birthday has been announced for a specific date."""
        self.supabase.table('birthdays').update({
            'announced_date': announced_date
        }).eq('user_id', user_id).eq('guild_id', guild_id).execute()

    # === LOGGING METHODS ===

    async def remove_user_birthday(self, user_id: int, guild_id: int) -> bool:
        """Remove user birthday."""
        try:
            self.supabase.table('birthdays').delete().eq('user_id', user_id).eq('guild_id', guild_id).execute()
            return True
        except Exception as e:
            print(f"Error removing birthday: {e}")
            return False

    async def log_event(
        self,
        category: str,
        action: str,
        user_id: Optional[int] = None,
        target_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        details: Optional[str] = None,
        guild_id: Optional[int] = None,
    ) -> None:
        """Log an event to the audit log."""
        self.supabase.table('audit_log').insert({
            'category': category,
            'action': action,
            'user_id': str(user_id) if user_id is not None else None,
            'target_id': str(target_id) if target_id is not None else None,
            'channel_id': str(channel_id) if channel_id is not None else None,
            'details': details,
            'guild_id': str(guild_id) if guild_id is not None else None
        }).execute()

    async def log_moderation_action(
        self,
        moderator_id: int,
        action: str,
        target_id: Optional[int] = None,
        reason: Optional[str] = None,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        message_count: Optional[int] = None,
    ) -> None:
        """Log moderation action."""
        self.supabase.table('mod_logs').insert({
            'moderator_id': moderator_id,
            'user_id': target_id,
            'action': action,
            'reason': reason,
            'guild_id': str(guild_id) if guild_id else None,
            'channel_id': channel_id,
            'message_count': message_count
        }).execute()

    async def get_recent_moderation_logs(self, guild_id: int, limit: int = 10) -> list[dict]:
        """Get recent moderation logs."""
        result = self.supabase.table('mod_logs').select('*').eq('guild_id', guild_id).order('created_at', desc=True).limit(limit).execute()
        return result.data

    async def log_health_check(
        self,
        component: str,
        status: str,
        value: Optional[float] = None,
        details: Optional[str] = None,
    ) -> None:
        """Log health check results."""
        self.supabase.table('health_logs').insert({
            'component': component,
            'status': status,
            'value': value,
            'details': details
        }).execute()

    async def log_roast_user(self, user_id: int) -> None:
        """Log that user roasted the bot."""
        await self.log_event(
            category="ROAST",
            action="USER_ROAST",
            user_id=user_id,
            details="User roasted the bot",
        )

    # === SETTINGS METHODS ===

    async def get_setting(self, key: str, guild_id: Optional[int] = None) -> Optional[str]:
        """Get setting value."""
        # guild_id required parameter
        result = self.supabase.table('settings').select('value').eq('setting_key', key).eq('guild_id', str(guild_id) if guild_id else None).execute()
        return result.data[0]['value'] if result.data else None

    async def set_setting(self, key: str, value: str, guild_id: Optional[int] = None) -> None:
        """Set setting value."""
        # guild_id required parameter
        self.supabase.table('settings').upsert({
            'guild_id': str(guild_id) if guild_id else None,
            'setting_key': key,
            'value': value,
            'updated_at': datetime.now().isoformat()
        }, on_conflict='guild_id,setting_key').execute()

    # === SYSTEM FLAGS ===

    async def get_flag(self, flag_name: str) -> Any:
        """Get system flag value."""
        result = self.supabase.table('system_flags').select('flag_value').eq('flag_name', flag_name).execute()
        return result.data[0]['flag_value'] if result.data else None

    async def set_flag(self, flag_name: str, flag_value: Any, description: Optional[str] = None) -> None:
        """Set system flag."""
        self.supabase.table('system_flags').upsert({
            'flag_name': flag_name,
            'flag_value': str(flag_value),
            'description': description
        }).execute()

    async def clear_flag(self, flag_name: str) -> None:
        """Clear system flag."""
        self.supabase.table('system_flags').delete().eq('flag_name', flag_name).execute()

    # === AUDIT METHODS ===

    async def get_audit_logs(self, guild_id: int, limit: int = 100) -> list[dict]:
        """Get recent audit logs."""
        result = self.supabase.table('audit_log').select('*').eq('guild_id', guild_id).order('timestamp', desc=True).limit(limit).execute()
        return result.data

    async def get_daily_digest_stats(self, guild_id: int) -> dict:
        """Get optimized daily digest statistics."""
        # Get logs from last 24 hours
        yesterday = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        result = self.supabase.table('audit_log').select('category, action').eq('guild_id', guild_id).gte('timestamp', yesterday).execute()
        
        logs = result.data
        return {
            "total_logs": len(logs),
            "critical_events": len([l for l in logs if l.get('category') == 'CRITICAL']),
            "warnings": len([l for l in logs if l.get('category') == 'WARNING']),
            "moderation_actions": len([l for l in logs if any(x in l.get('action', '') for x in ['BAN', 'KICK', 'MUTE'])]),
            "user_events": len([l for l in logs if any(x in l.get('action', '') for x in ['JOIN', 'LEAVE'])]),
        }

    # === ROAST METHODS ===

    async def add_roast_xp(self, xp_amount: int) -> dict:
        """Add roast XP."""
        return {"xp_gained": xp_amount, "bot_level": 1}

    # === CLEANUP ===

    async def close(self) -> None:
        """Close database connection (no-op for Supabase)."""
        pass

    async def add_xp(self, user_id: int, guild_id: int, xp_amount: int) -> tuple[int, int]:
        """Add XP to a user and return their new XP and level."""
        # Get current XP
        result = self.supabase.table('users').select('xp').eq('user_id', user_id).eq('guild_id', guild_id).execute()
        
        if not result.data:
            # Create user
            self.supabase.table('users').insert({
                'user_id': user_id,
                'guild_id': str(guild_id) if guild_id else None,
                'username': 'Unknown',
                'discriminator': '0',
                'xp': xp_amount,
                'level': 0
            }).execute()
            new_xp = xp_amount
        else:
            current_xp = result.data[0]['xp']
            new_xp = current_xp + xp_amount
            
            self.supabase.table('users').update({
                'xp': new_xp
            }).eq('user_id', user_id).eq('guild_id', guild_id).execute()
        
        # Calculate level
        new_level = int((new_xp / 100) ** 0.5)
        
        # Update level
        self.supabase.table('users').update({
            'level': new_level
        }).eq('user_id', user_id).eq('guild_id', guild_id).execute()
        
        return new_xp, new_level



