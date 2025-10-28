# Troubleshooting /setup Command Issues

## ✅ Code Verification

I've verified that the code in the `fix-all-setup-and-cheater-jail` branch contains:
- ✅ TIMEZONE_OPTIONS with 25 timezone choices
- ✅ TimezoneSelect class (dropdown)
- ✅ StaffRoleSelect class (dropdown)
- ✅ Both properly added to their respective views

## 🔧 If You're Not Seeing the Dropdowns

### Step 1: Verify You're on the Correct Branch

```bash
git branch
# Should show: * fix-all-setup-and-cheater-jail
```

If not on the correct branch:
```bash
git checkout fix-all-setup-and-cheater-jail
git pull origin fix-all-setup-and-cheater-jail
```

### Step 2: Completely Restart the Bot

**Using dev.bat:**
1. Option 2 - Stop bot
2. Option 20 - Clear all commands (IMPORTANT!)
3. Option 1 - Start bot
4. Wait 30-60 seconds for commands to sync

**Or manually:**
```bash
# Stop the bot (Ctrl+C if running)
# Then:
python clear_and_sync.py
python bot.py
```

### Step 3: Clear Discord Cache

**CRITICAL:** Discord caches slash commands on the client side!

1. **Restart Discord completely:**
   - Press `Ctrl+R` (or `Cmd+R` on Mac)
   - Or close Discord completely and reopen

2. **If that doesn't work:**
   - Close Discord
   - Clear Discord cache:
     - Windows: `%AppData%\Discord\Cache`
     - Mac: `~/Library/Application Support/Discord/Cache`
   - Reopen Discord

### Step 4: Verify Command Sync

Check the bot console output for:
```
Synced 29 commands to guild XXXXX
```

If you see errors, the commands didn't sync properly.

### Step 5: Test the Commands

1. Type `/setup` in Discord
2. Select "Verification System" from dropdown
3. You should see 5 dropdowns:
   - Review Channel
   - Verified Role
   - Staff Role ← THIS ONE
   - Cheater Role
   - Cheater Jail Channel

4. Select "General Settings" from dropdown
5. You should see 2 dropdowns:
   - Timezone ← THIS ONE (25 options)
   - Online Message Channel

## 🐛 Common Issues

### Issue: "I don't see the Staff Role dropdown"

**Cause:** Discord limits views to 5 select menus + buttons

**Solution:** The Verification System has exactly 5 dropdowns (the maximum). Make sure you're scrolling down in the message to see all of them.

### Issue: "Timezone is still a text input"

**Possible causes:**
1. Bot not restarted with new code
2. Discord cache not cleared
3. Commands not synced

**Solution:** Follow Steps 2-3 above

### Issue: "Commands not syncing"

**Check:**
1. Bot has proper permissions in the server
2. Bot is in the correct guild
3. No errors in console

**Fix:**
```bash
# Use dev.bat option 20 to clear commands
# Then restart bot
```

## 🔍 Verify the Code Locally

Run this to verify your local code has the changes:

```bash
cd /path/to/MalaBoT
grep -c "TIMEZONE_OPTIONS" cogs/setup.py
# Should output: 1

grep -c "class StaffRoleSelect" cogs/setup.py  
# Should output: 1

grep -c "class TimezoneSelect" cogs/setup.py
# Should output: 1
```

## 📊 What Each /setup Section Should Show

### Verification System:
- 5 dropdowns (Review Channel, Verified Role, Staff Role, Cheater Role, Cheater Jail)
- 1 button (View Current Config)

### Birthday System:
- 3 dropdowns (Birthday Channel, Birthday Role, Birthday Time)
- 1 button (View Current Config)

### XP System:
- 1 button (Configure XP Amounts) - Opens modal
- 1 button (View Current Config)

### General Settings:
- 2 dropdowns (Timezone, Online Message Channel)
- 1 button (Set Online Message Text) - Opens modal
- 1 button (View Current Config)

## 🆘 Still Not Working?

If you've followed all steps and it's still not working:

1. **Check bot console for errors**
2. **Verify you're testing in the correct Discord server**
3. **Make sure bot has proper permissions**
4. **Try in a different Discord server to rule out server-specific issues**

## ✅ Verification Checklist

Before reporting an issue, verify:
- [ ] On correct branch (`fix-all-setup-and-cheater-jail`)
- [ ] Pulled latest code (`git pull`)
- [ ] Bot completely restarted
- [ ] Commands cleared and synced
- [ ] Discord restarted (Ctrl+R)
- [ ] Waited 30+ seconds after bot start
- [ ] Testing in correct server
- [ ] Bot has admin permissions

## 📝 Expected Behavior

**When you run `/setup` and select "General Settings":**
- You should see a dropdown labeled "Select your timezone..."
- Clicking it shows 25 timezone options (UTC-12 through UTC+12)
- You should see a dropdown labeled "Select channel for online message..."
- You should see a button "Set Online Message Text"

**When you run `/setup` and select "Verification System":**
- You should see 5 dropdowns including "Select staff role..."
- All dropdowns should be functional
- Selecting options should save to database

If you're not seeing this, the issue is with deployment, not the code.