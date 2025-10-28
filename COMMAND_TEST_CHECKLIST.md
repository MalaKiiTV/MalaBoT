# Complete Command Test Checklist

## ✅ XP Commands (All Users)

### /rank
- [ ] `/rank` - Show your own rank
- [ ] `/rank @user` - Show another user's rank
- **Expected**: Shows XP, level, progress bar, daily status

### /leaderboard
- [ ] `/leaderboard` - Show top 10 users
- [ ] `/leaderboard 20` - Show top 20 users
- **Expected**: Shows ranked list of users with XP and levels

### /daily
- [ ] `/daily` - Claim daily bonus (first time)
- [ ] `/daily` - Try to claim again (should reject)
- **Expected**: First time gives XP, second time says "already claimed today"

---

## ✅ XP Admin Commands (Administrators Only)

### /xpadmin add
- [ ] `/xpadmin add @user 100` - Add 100 XP
- [ ] `/xpadmin add @user 0` - Try with 0 (should reject)
- [ ] `/xpadmin add @user -50` - Try with negative (should reject)
- **Expected**: Adds XP, shows success message with amount

### /xpadmin remove
- [ ] `/xpadmin remove @user 50` - Remove 50 XP
- [ ] `/xpadmin remove @user 0` - Try with 0 (should reject)
- **Expected**: Removes XP, shows new total

### /xpadmin set
- [ ] `/xpadmin set @user 500` - Set to 500 XP
- [ ] `/xpadmin set @user 0` - Set to 0 XP
- **Expected**: Sets XP to exact amount, shows success

### /xpadmin reset
- [ ] `/xpadmin reset @user` - Reset user XP
- **Expected**: Resets XP and level to 0

---

## ✅ XP Configuration (Administrators Only)

### /xpconfig
- [ ] `/xpconfig` - View all settings
- [ ] `/xpconfig xp_min` - View min XP setting
- [ ] `/xpconfig xp_max` - View max XP setting
- [ ] `/xpconfig cooldown` - View cooldown setting
- [ ] `/xpconfig daily_xp` - View daily bonus setting
- [ ] `/xpconfig streak_bonus` - View streak bonus setting
- [ ] `/xpconfig xp_min 10` - Show how to change min XP to 10
- **Expected**: Shows current values and instructions for editing config/constants.py

---

## ✅ Fun Commands (All Users)

### /joke
- [ ] `/joke` - Get a random joke
- [ ] `/joke` - Try again immediately (should show cooldown)
- **Expected**: Shows joke, then cooldown message

### /fact
- [ ] `/fact` - Get a random fact
- [ ] `/fact` - Try again immediately (should show cooldown)
- **Expected**: Shows fact, then cooldown message

### /roast
- [ ] `/roast @user` - Roast a user
- [ ] `/roast @user` - Try again immediately (should show cooldown)
- **Expected**: Shows roast, then cooldown message

### /8ball
- [ ] `/8ball Will it work?` - Ask a question
- **Expected**: Shows magic 8-ball response

### /roll
- [ ] `/roll` - Roll default dice
- [ ] `/roll 20` - Roll d20
- **Expected**: Shows dice roll result

### /coinflip
- [ ] `/coinflip` - Flip a coin
- **Expected**: Shows heads or tails

---

## ✅ Moderation Commands (Administrators Only)

### /delete
- [ ] `/delete 5` - Delete 5 messages
- **Expected**: Deletes messages, shows confirmation

### /kick
- [ ] `/kick @user reason` - Kick user
- **Expected**: Kicks user, logs action

### /ban
- [ ] `/ban @user reason` - Ban user
- **Expected**: Bans user, logs action

### /mute
- [ ] `/mute @user 10m reason` - Mute for 10 minutes
- **Expected**: Mutes user, auto-unmutes after time

### /unmute
- [ ] `/unmute @user` - Unmute user
- **Expected**: Unmutes user immediately

---

## ✅ Utility Commands (All Users)

### /help
- [ ] `/help` - Show all commands
- **Expected**: Shows organized command list

### /ping
- [ ] `/ping` - Check bot latency
- **Expected**: Shows latency and uptime

### /userinfo
- [ ] `/userinfo` - Show your info
- [ ] `/userinfo @user` - Show another user's info
- **Expected**: Shows user details with avatar

### /serverinfo
- [ ] `/serverinfo` - Show server info
- **Expected**: Shows server details with icon

### /serverstats
- [ ] `/serverstats` - Show server statistics
- **Expected**: Shows member counts, channel counts, etc.

### /about
- [ ] `/about` - Show bot information
- **Expected**: Shows bot version, features, etc.

---

## ✅ Verify Commands (All Users)

### /verify submit
- [ ] `/verify submit` - Submit verification
- **Expected**: Prompts for screenshot upload

### /verify review (Staff Only)
- [ ] `/verify review @user accept` - Accept verification
- [ ] `/verify review @user deny` - Deny verification
- **Expected**: Processes verification request

### /verify setup (Admin Only)
- [ ] `/verify setup #channel` - Set review channel
- **Expected**: Sets channel for verification reviews

---

## 🔍 Known Issues to Check

1. **Verify Commands Structure**
   - Should show as ONE `/verify` command with 3 subcommands
   - NOT as 3 separate commands

2. **XP Admin Amount Parameter**
   - Should accept positive numbers
   - Should reject 0 and negative numbers
   - Should show clear error messages

3. **Daily Check-in Status**
   - `/rank` should show correct daily status
   - Should prevent multiple claims per day

4. **XP Configuration**
   - `/xpconfig` should show current values
   - Should provide clear instructions for changing settings

---

## 📝 Testing Notes

- Test as **Server Administrator** for admin commands
- Test as **Regular User** for user commands
- Check bot logs for any errors
- Verify all embeds display correctly
- Check that cooldowns work properly

---

**Last Updated**: January 27, 2025
**Status**: Ready for testing