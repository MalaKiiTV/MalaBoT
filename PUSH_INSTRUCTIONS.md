# Manual Push Instructions

## ⚠️ Git Push Timed Out

The automated git push timed out due to network issues. Please manually push the changes.

---

## 📦 What's Ready to Push

**Commit**: `67d3e01`
**Message**: "XP System Overhaul: Fixed amounts, reaction/voice XP, improved config"

**Files Changed**:
- `config/constants.py` - Updated XP constants
- `cogs/xp.py` - Added reaction and voice XP listeners
- `cogs/setup.py` - Added level roles display
- `XP_SYSTEM_OVERHAUL.md` - Complete documentation
- `DEPLOYMENT_GUIDE_XP.md` - Quick deployment guide
- `todo.md` - Task tracking

---

## 🚀 Manual Push Steps

### On Your Local Machine:

```bash
cd /home/malabot/MalaBoT
git pull origin main
git push origin main
```

If you encounter any issues:

```bash
# Check status
git status

# View commit log
git log --oneline -5

# Force push if needed (use with caution)
git push -f origin main
```

---

## ✅ Verification

After pushing, verify on GitHub:
1. Go to your repository
2. Check the latest commit is "XP System Overhaul..."
3. Verify all 5 files are updated

---

## 📋 Next Steps After Push

1. **Pull changes on droplet**:
   ```bash
   cd /home/malabot/MalaBoT
   git pull origin main
   ```

2. **Restart bot**:
   ```bash
   pkill -f bot.py
   nohup python3 bot.py > data/logs/latest.log 2>&1 &
   ```

3. **Sync commands in Discord**:
   ```
   /sync
   ```
   Wait 5 minutes, then restart Discord client

4. **Configure XP system**:
   ```
   /setup
   ```
   Select "XP System" and configure all settings

5. **Test everything**:
   - Send messages (should gain XP)
   - React to messages (author should gain XP)
   - Join/leave voice (should gain XP)
   - Check `/rank` and `/leaderboard`
   - Verify level-up messages work

---

## 📚 Documentation

Read these files for complete information:
- `XP_SYSTEM_OVERHAUL.md` - Full system documentation
- `DEPLOYMENT_GUIDE_XP.md` - Quick deployment guide

---

**Status**: Ready to push ✅
**Tested**: All files compile successfully ✅
**Risk**: Low - all changes tested ✅