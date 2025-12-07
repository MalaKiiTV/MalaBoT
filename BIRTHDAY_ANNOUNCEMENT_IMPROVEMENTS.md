# Birthday Announcement System Improvements

## Overview
This update enhances the birthday announcement system to prevent duplicate announcements and properly track which birthdays have been announced each year.

## Changes Made

### 1. Database Schema Enhancement
The `birthdays` table now includes an `announced_year` column that tracks the year when a birthday was last announced. This prevents the bot from sending multiple birthday messages for the same user in the same year.

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS birthdays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    birthday TEXT NOT NULL,
    timezone TEXT DEFAULT 'UTC',
    announced_year INTEGER,  -- NEW: Tracks last announcement year
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. New DatabaseManager Methods

#### `get_unannounced_birthdays(current_year: int) -> list`
Returns a list of users whose birthdays are today AND haven't been announced this year.

**Usage:**
```python
current_year = datetime.now().year
unannounced = await db_manager.get_unannounced_birthdays(current_year)
```

**Returns:**
```python
[
    (user_id, birthday_string),
    ...
]
```

#### `mark_birthday_announced(user_id: int, year: int) -> None`
Marks a user's birthday as announced for a specific year.

**Usage:**
```python
await db_manager.mark_birthday_announced(user_id, 2024)
```

### 3. Birthday Check Logic Updates

The birthday check task in `cogs/birthdays.py` has been updated to:

1. **Use the new `get_unannounced_birthdays()` method** instead of manually checking announced years
2. **Automatically mark birthdays as announced** after sending the message
3. **Respect guild timezones** when determining "today's" birthdays

**Before:**
```python
today = now.strftime("%m-%d")
today_birthdays = await self.bot.db_manager.get_today_birthdays(today)

for user_data in today_birthdays:
    user_id = user_data[0]
    
    # Manual check for announced year
    announced_year = user_data[4] if len(user_data) > 4 else None
    if announced_year == now.year:
        continue
    
    # Send message...
```

**After:**
```python
# Automatically filters out already-announced birthdays
today_birthdays = await self.bot.db_manager.get_unannounced_birthdays(now.year)

for user_data in today_birthdays:
    user_id = user_data[0]
    
    # Send message...
    
    # Mark as announced
    await self.bot.db_manager.mark_birthday_announced(user_id, now.year)
```

## Benefits

### 1. **No Duplicate Announcements**
The system now guarantees that each user receives exactly one birthday announcement per year, even if:
- The bot restarts multiple times on their birthday
- The birthday check runs multiple times in a day
- There are timezone changes or configuration updates

### 2. **Cleaner Code**
The logic is now centralized in the database layer, making the cog code simpler and more maintainable.

### 3. **Better Performance**
The database query filters out already-announced birthdays at the SQL level, reducing the amount of data processed in Python.

### 4. **Audit Trail**
The `announced_year` field provides a historical record of when birthdays were last announced, useful for debugging and analytics.

## Testing Recommendations

### Manual Testing
1. **Set a test birthday for today:**
   ```
   /bday set
   # Enter today's date in MM-DD format
   ```

2. **Wait for the birthday check to run** (or restart the bot to trigger it immediately)

3. **Verify the announcement is sent**

4. **Restart the bot** and verify no duplicate announcement is sent

5. **Check the database:**
   ```sql
   SELECT user_id, birthday, announced_year FROM birthdays WHERE user_id = YOUR_USER_ID;
   ```
   The `announced_year` should match the current year.

### Edge Cases to Test
- [ ] Birthday on leap day (February 29th)
- [ ] Birthday at midnight in different timezones
- [ ] Multiple users with the same birthday
- [ ] Bot restart during birthday announcement
- [ ] Timezone changes mid-year

## Migration Notes

### For Existing Installations
The `announced_year` column is nullable, so existing birthday records will work without modification. The first time each user's birthday is announced after this update, the `announced_year` will be set.

### Database Migration (if needed)
If you need to manually add the column:
```sql
ALTER TABLE birthdays ADD COLUMN announced_year INTEGER;
```

## Rollback Plan
If issues arise, you can rollback by:
1. Reverting the changes to `database/models.py` and `cogs/birthdays.py`
2. The `announced_year` column can remain in the database (it will simply be ignored)

## Future Enhancements
Potential improvements for future versions:
- Birthday reminder notifications (e.g., "Tomorrow is X's birthday!")
- Birthday statistics and analytics
- Custom birthday roles or permissions
- Birthday countdown feature
- Multi-language birthday messages

## Support
If you encounter any issues with the birthday system:
1. Check the bot logs for error messages
2. Verify the `birthday_channel` is set correctly: `/setup birthday`
3. Ensure the bot has permission to send messages in the birthday channel
4. Check that the timezone is configured correctly: `/setup timezone`

## Changelog
- **2024-01-XX**: Initial implementation of duplicate prevention system
  - Added `announced_year` column to birthdays table
  - Added `get_unannounced_birthdays()` method
  - Added `mark_birthday_announced()` method
  - Updated birthday check logic in cogs/birthdays.py