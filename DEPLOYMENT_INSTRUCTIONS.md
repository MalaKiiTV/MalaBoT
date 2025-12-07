# Deployment Instructions for Birthday Announcement Improvements

## What Was Changed
This update prevents duplicate birthday announcements by tracking which birthdays have been announced each year.

## Pull Request
**PR #23**: https://github.com/MalaKiiTV/MalaBoT/pull/23

## How to Deploy

### Step 1: Review and Merge the Pull Request
1. Go to https://github.com/MalaKiiTV/MalaBoT/pull/23
2. Review the changes
3. Click "Merge pull request"
4. Confirm the merge

### Step 2: Update Your Local Repository
On your local machine, run:
```bash
cd C:\Users\malak\Desktop\Mala
git checkout main
git pull origin main
```

### Step 3: Database Migration (Automatic)
The `announced_year` column will be automatically created when the bot starts. No manual database migration is needed.

However, if you want to manually verify or add the column:
```sql
-- Connect to your database and run:
ALTER TABLE birthdays ADD COLUMN announced_year INTEGER;
```

### Step 4: Restart the Bot
Simply restart your bot. The new code will:
- Automatically use the new duplicate prevention system
- Mark birthdays as announced after sending messages
- Prevent duplicate announcements even with multiple restarts

### Step 5: Verify the Changes
1. **Check the logs** for any errors during startup
2. **Test with a birthday today** (if possible):
   - Use `/bday set` to set a test birthday for today
   - Wait for the birthday check to run
   - Restart the bot
   - Verify no duplicate announcement is sent
3. **Check the database**:
   ```sql
   SELECT user_id, birthday, announced_year FROM birthdays;
   ```
   After a birthday is announced, the `announced_year` should be set to the current year.

## What to Expect

### Before This Update
- Birthday announcements could be sent multiple times if the bot restarted on someone's birthday
- No tracking of which birthdays had been announced

### After This Update
- Each user receives exactly ONE birthday announcement per year
- The system tracks announcement years in the database
- Bot restarts won't cause duplicate announcements
- Cleaner, more maintainable code

## Rollback Plan (If Needed)
If you encounter issues:
1. Go to your local repository
2. Run:
   ```bash
   git checkout main
   git reset --hard 71b6c5b  # The commit before this update
   git push origin main --force
   ```
3. Restart the bot

## Support
If you encounter any issues:
1. Check the bot logs for error messages
2. Verify the database schema includes the `announced_year` column
3. Ensure the bot has proper permissions in the birthday channel
4. Check that timezone settings are correct

## Files Changed
- `database/models.py`: Added new methods for birthday tracking
- `cogs/birthdays.py`: Updated birthday check logic
- `BIRTHDAY_ANNOUNCEMENT_IMPROVEMENTS.md`: Comprehensive documentation

## Questions?
Feel free to ask if you need any clarification or run into issues during deployment!