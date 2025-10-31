# Quick Deployment Guide - XP System Updates

## 🚀 What Changed

1. **Fixed XP amounts** instead of 5-15 range
2. **Added Reaction XP** - users gain XP when their messages get reactions
3. **Added Voice XP** - users gain XP for voice chat participation
4. **Improved config display** - shows level roles count
5. **Updated constants** - removed old min/max, added new defaults

---

## 📦 Files Modified

1. `config/constants.py` - Updated XP constants
2. `cogs/xp.py` - Added reaction and voice listeners
3. `cogs/setup.py` - Added level roles display to config

---

## 🔧 Deployment Steps

### Step 1: Pull Changes
```bash
cd /home/malabot/MalaBoT
git pull origin main
```

### Step 2: Verify Files
```bash
# Check if files compile
python3 -m py_compile config/constants.py
python3 -m py_compile cogs/xp.py
python3 -m py_compile cogs/setup.py
```

### Step 3: Restart Bot
```bash
# Stop bot
pkill -f bot.py

# Start bot
nohup python3 bot.py > data/logs/latest.log 2>&1 &

# Check if running
ps aux | grep bot.py
```

### Step 4: Sync Commands (CRITICAL!)
In Discord, run:
```
/sync
```
Then:
1. Wait 5 minutes
2. Restart Discord client (Ctrl+R or close/reopen)
3. Commands should now work properly

### Step 5: Configure XP System
```
/setup
```
1. Select "XP System"
2. Set Level-up Channel
3. Configure Message XP (e.g., 10)
4. Configure Reaction XP (e.g., 2)
5. Configure Voice XP (e.g., 5)
6. Set XP Cooldown (e.g., 60)

### Step 6: Verify Configuration
```
/setup
```
1. Select "View Current Config"
2. Check XP System section shows:
   - Level-up Channel
   - Message XP: 10
   - Reaction XP: 2
   - Voice XP: 5/min
   - Cooldown: 60s
   - Level Roles: X configured (if any)

---

## ✅ Testing

### Test Message XP
1. Send a message in any channel
2. Wait for cooldown (60 seconds)
3. Send another message
4. Run `/rank` to verify XP increased

### Test Reaction XP
1. Have someone post a message
2. React to their message
3. They should gain XP
4. They can check with `/rank`

### Test Voice XP
1. Join a voice channel
2. Stay for a bit
3. Leave the voice channel
4. Run `/rank` to verify XP increased

### Test Level-up
1. Use `/xpadd` to give yourself enough XP to level up
2. Verify level-up message appears in configured channel
3. Check if level role is assigned (if configured)

### Test Level Roles
```
/xplevelrole action:Add level:5 role:@TestRole
/xpadd user:@yourself amount:700
```
- Should level up to 5 and receive the role

---

## 🐛 Common Issues

### Issue: Commands not working after deployment
**Solution**: 
1. Run `/sync` in Discord
2. Wait 5 minutes
3. Restart Discord client
4. Try again

### Issue: XP not being awarded
**Solution**:
1. Check `/setup` → "View Current Config"
2. Verify XP amounts are set (not 0)
3. Check cooldown isn't too high
4. Restart bot if needed

### Issue: Channel selection not working
**Solution**:
1. This should be fixed now
2. If still issues, run `/sync` and wait
3. Check bot logs for errors

### Issue: Level roles not being assigned
**Solution**:
1. Verify bot has "Manage Roles" permission
2. Ensure bot's role is higher than role being assigned
3. Check `/xplevelrole list` to see configured roles

---

## 📊 Monitoring

### Check Bot Logs
```bash
tail -f data/logs/latest.log
```
Look for:
- "Error in on_message XP"
- "Error in on_reaction_add XP"
- "Error in on_voice_state_update XP"

### Check Bot Status
```bash
ps aux | grep bot.py
```

### Check Database
```bash
sqlite3 data/malabot.db "SELECT * FROM settings WHERE key LIKE 'xp_%' LIMIT 10;"
```

---

## 🎯 Expected Behavior

### After Deployment:
- ✅ Bot restarts successfully
- ✅ Commands sync properly
- ✅ XP system shows fixed amounts (not ranges)
- ✅ Users gain XP from messages, reactions, and voice
- ✅ Level-up messages appear
- ✅ Level roles are assigned
- ✅ Config view shows all settings

### User Experience:
- Users send messages → Gain 10 XP (configurable)
- Users receive reactions → Gain 2 XP per reaction (configurable)
- Users join/leave voice → Gain 5 XP (configurable)
- Users level up → See announcement in configured channel
- Users reach milestone levels → Receive configured roles

---

## 📞 Need Help?

If something isn't working:

1. **Check logs**: `tail -f data/logs/latest.log`
2. **Verify sync**: Run `/sync` and wait 5 minutes
3. **Restart bot**: `pkill -f bot.py && nohup python3 bot.py > data/logs/latest.log 2>&1 &`
4. **Check permissions**: Ensure bot has all necessary permissions
5. **Review config**: Use `/setup` → "View Current Config"

---

## 🎉 Success Indicators

You'll know everything is working when:
- [ ] Bot starts without errors
- [ ] `/setup` opens and shows XP System option
- [ ] Can configure all XP settings
- [ ] Config view shows all settings correctly
- [ ] Messages award XP
- [ ] Reactions award XP
- [ ] Voice participation awards XP
- [ ] Level-ups trigger announcements
- [ ] Level roles are assigned
- [ ] `/rank` shows correct information
- [ ] `/leaderboard` displays properly

---

**Estimated Deployment Time**: 10-15 minutes
**Downtime**: ~30 seconds (bot restart)
**Risk Level**: Low (all changes tested and compiled)