# Config Display Not Showing Correct Information

## Problem

The `/setup` → "View Current Config" is showing:
- ❌ "XP per Message: 5-15" (old format)
- ❌ "Welcome: Not configured" (when it IS configured)
- ❌ "Birthday: Not configured" (when it IS configured)
- ❌ "Role Connections: 0" (when connections exist)

## Root Cause

The database still has **old format settings** from before we made everything guild-specific. The config view is looking for the NEW keys, but the database has the OLD keys.

### Old vs New Format

**Old Format (Before):**
```
welcome_channel_id = 123456789
welcome_message = "Welcome!"
min_xp_542004156513255445 = 5
max_xp_542004156513255445 = 15
```

**New Format (After):**
```
welcome_channel_542004156513255445 = 123456789
welcome_message_542004156513255445 = "Welcome!"
xp_per_message_542004156513255445 = 10
```

## Solution

You need to migrate your database settings from old format to new format.

### Option 1: Use the Fix Script (Recommended)

1. **Find your guild ID:**
   - Enable Developer Mode in Discord (Settings → Advanced)
   - Right-click your server name
   - Click "Copy ID"

2. **Run the fix script:**
   ```bash
   cd /path/to/MalaBoT
   python fix_database_settings.py YOUR_GUILD_ID
   ```

3. **Restart your bot**

4. **Check config:**
   - Run `/setup` → "View Current Config"
   - Everything should now show correctly

### Option 2: Check Database First

If you want to see what's in your database before fixing:

```bash
python check_database_settings.py
```

This will show:
- All settings in your database
- Which format they're in (old vs new)
- What needs to be migrated

### Option 3: Reconfigure Manually

If the scripts don't work, you can reconfigure everything:

1. **Welcome System:**
   - `/setup` → Welcome
   - Set Channel, Message, Title, Image

2. **Goodbye System:**
   - `/setup` → Welcome → Goodbye System
   - Set Channel, Message, Title, Image

3. **Birthday System:**
   - `/setup` → Birthday
   - Set Channel, Time, Message

4. **XP System:**
   - `/setup` → XP
   - Set Message XP, Reaction XP, Voice XP, Cooldown

5. **Role Connections:**
   - `/setup` → Role Connections
   - Recreate your connections

## Why This Happened

We recently updated the bot to use guild-specific database keys for better multi-server support. Your database still has settings in the old format, so the config view can't find them.

## Prevention

This won't happen again because:
1. All new settings use guild-specific keys
2. The fix script migrates old settings
3. Future updates will include migration scripts

## Verification

After running the fix script, verify everything works:

### 1. Check Config Display
```
/setup → View Current Config
```

Should show:
- ✅ Welcome: Channel, Message, Title
- ✅ Goodbye: Channel, Message, Title
- ✅ Birthday: Channel, Time, Message
- ✅ XP: Message XP, Reaction XP, Voice XP
- ✅ Role Connections: Active count

### 2. Test Features

**Welcome/Goodbye:**
- Have someone join/leave
- Check if messages appear

**Birthday:**
- Check if birthdays are announced

**XP:**
- Send messages
- Check if XP is gained
- Check if level-up messages appear

**Role Connections:**
- Add/remove roles
- Check if connections trigger

## Troubleshooting

### Script Says "No fixes needed" but config still wrong

**Solution:** The settings might be completely missing. Reconfigure manually via `/setup`.

### Script Fails with Error

**Solution:** 
1. Check if `data/bot.db` exists
2. Make sure bot is not running (stop it first)
3. Check file permissions
4. Share the error message for help

### Config Still Shows "Not configured"

**Possible causes:**
1. Settings are for a different guild ID
2. Database keys are still in old format
3. Settings were never saved

**Solution:**
1. Run `check_database_settings.py` to see what's actually stored
2. Verify you're using the correct guild ID
3. Reconfigure via `/setup` if needed

### Role Connections Show 0 but I have connections

**Possible causes:**
1. Connections are stored but not enabled
2. Connections are for a different guild
3. Role connections cog not loaded

**Solution:**
1. Check `data/logs/role_connections.log`
2. Run `/setup` → Role Connections → Manage Connections
3. Verify connections exist and are enabled
4. Check if RoleConnections cog is loaded

## Files Created

1. `check_database_settings.py` - View what's in your database
2. `fix_database_settings.py` - Migrate old settings to new format
3. `CONFIG_DISPLAY_FIX.md` - This documentation

## Quick Fix Commands

```bash
# 1. Check what's in database
python check_database_settings.py

# 2. Fix settings (replace with your guild ID)
python fix_database_settings.py 542004156513255445

# 3. Restart bot
pkill -f bot.py
nohup python3 bot.py > data/logs/latest.log 2>&1 &

# 4. Verify in Discord
# Run: /setup → View Current Config
```

## Need Help?

If the scripts don't work:
1. Run `check_database_settings.py` and share the output
2. Check `data/logs/bot.log` for errors
3. Try reconfiguring manually via `/setup`
4. Check if bot has proper permissions