# XP System Overhaul - Complete Documentation

## Overview
This update completely overhauls the XP system to use **fixed XP amounts** instead of random ranges, adds **reaction and voice XP tracking**, and improves the configuration display.

---

## 🎯 Major Changes

### 1. **Fixed XP Amounts (No More Ranges)**

#### Before:
- XP was randomly awarded between 5-15 per message
- Unpredictable and inconsistent progression
- Users couldn't plan their leveling

#### After:
- **Message XP**: Fixed amount (default: 10 XP)
- **Reaction XP**: Fixed amount (default: 2 XP per reaction received)
- **Voice XP**: Fixed amount (default: 5 XP per minute in voice)
- All amounts are configurable per server via `/setup`

### 2. **New XP Sources**

#### Reaction XP
- Users gain XP when their messages receive reactions
- Configurable amount (set to 0 to disable)
- Encourages quality content creation
- Example: User posts a helpful message → Gets 5 reactions → Gains 10 XP (2 per reaction)

#### Voice XP
- Users gain XP for participating in voice channels
- Currently awards XP when leaving voice (simplified implementation)
- Configurable amount (set to 0 to disable)
- Future enhancement: Track time spent and award periodically

### 3. **Improved Configuration Display**

The `/setup` → "View Current Config" now shows:
- Level-up Channel
- Message XP amount
- Reaction XP amount
- Voice XP amount
- XP Cooldown
- **Level Roles count** (NEW!)

---

## 📋 Configuration Guide

### Setting Up XP System

1. **Run `/setup` in Discord**
2. **Select "XP System"**
3. **Configure each setting:**

#### Set Level-up Channel
- Click "Set Level-up Channel"
- Select the channel where level-up announcements will be posted
- Default: Server's system channel

#### Message XP
- Click "Message XP"
- Enter a fixed amount (e.g., 10)
- This is how much XP users gain per message
- Minimum: 1 XP

#### Reaction XP
- Click "Reaction XP"
- Enter a fixed amount (e.g., 2)
- This is how much XP users gain per reaction received
- Set to 0 to disable

#### Voice XP
- Click "Voice XP"
- Enter a fixed amount (e.g., 5)
- This is how much XP users gain per minute in voice
- Set to 0 to disable

#### XP Cooldown
- Click "XP Cooldown"
- Enter seconds between XP gains (e.g., 60)
- Prevents spam and ensures fair progression
- Minimum: 0 seconds (no cooldown)

#### Set Level-up Message
- Click "Set Level-up Message"
- Customize the message shown when users level up
- Available variables:
  - `{member}` - Mentions the user
  - `{level}` - Shows the new level
- Example: "🎉 {member} reached level {level}!"

---

## 🏆 Level Role Rewards

### Managing Level Roles

Use the `/xplevelrole` command to manage role rewards:

#### Add a Level Role
```
/xplevelrole action:Add level:10 role:@Level 10
```
- Users will automatically receive this role when reaching level 10

#### Remove a Level Role
```
/xplevelrole action:Remove level:10
```
- Removes the role reward for level 10

#### List All Level Roles
```
/xplevelrole action:List
```
- Shows all configured level roles

### How Level Roles Work
1. User gains enough XP to level up
2. Bot checks if there's a role configured for that level
3. If yes, bot automatically assigns the role
4. Role is permanent (doesn't get removed if user loses XP)

---

## 🔥 Roast XP System

The bot has its own leveling system based on roasts!

### How It Works
1. Users roast the bot using `/roast` (without target)
2. Bot gains 5-15 Roast XP per roast
3. Bot levels up and gains new titles
4. Bot's responses get sassier as it levels up

### Roast Titles
- Level 1: Newbie Roaster
- Level 2: Sassy Bot
- Level 3: Sharp Tongue
- Level 4: Burn Master
- Level 5: Fire Brand
- Level 6: Inferno Speaker
- Level 7: Dragon's Breath
- Level 8: Hellfire Roaster
- Level 9: Legendary Burn
- Level 10: Roast God

### Viewing Bot's Roast Level
- The bot's current level and title are shown in roast responses
- Example: "+12 Roast XP • Fire Brand"

---

## 🎮 User Commands

### Check Your Rank
```
/rank [@user]
```
- Shows your (or another user's) XP, level, and progress
- Displays server rank
- Shows XP needed for next level
- Indicates if daily bonus is available

### View Leaderboard
```
/leaderboard [limit]
```
- Shows top users by XP
- Default: Top 10 users
- Maximum: Top 25 users
- Shows medals for top 3 (🥇🥈🥉)

### Claim Daily Bonus
```
/daily
```
- Claim 50 XP once per day
- Builds a streak for bonus XP
- Streak bonus: +10% per day
- Example: Day 5 streak = 50 + 25 bonus = 75 XP

---

## 🔧 Admin Commands

### Add XP to User
```
/xpadd user:@User amount:100
```
- Adds XP to a user
- Server Owner only

### Remove XP from User
```
/xpremove user:@User amount:50
```
- Removes XP from a user
- Server Owner only

### Set User XP
```
/xpset user:@User amount:500
```
- Sets user's XP to exact amount
- Server Owner only

### Reset User XP
```
/xpreset user:@User
```
- Resets user's XP and level to 0
- Server Owner only

---

## 📊 Technical Details

### Database Settings Format
All XP settings are stored per-guild:
- `xp_per_message_{guild_id}` - Message XP amount
- `xp_per_reaction_{guild_id}` - Reaction XP amount
- `xp_per_voice_minute_{guild_id}` - Voice XP amount
- `xp_cooldown_{guild_id}` - Cooldown in seconds
- `xp_channel_{guild_id}` - Level-up channel ID
- `xp_levelup_message_{guild_id}` - Custom level-up message
- `xp_level_roles_{guild_id}` - Level role rewards (format: "level:role_id,level:role_id")

### Default Values
If not configured, the system uses these defaults:
- Message XP: 10
- Reaction XP: 2
- Voice XP: 5
- Cooldown: 60 seconds

### XP Calculation
- **Messages**: Fixed amount per message (respects cooldown)
- **Reactions**: Fixed amount per reaction received (no cooldown)
- **Voice**: Fixed amount when leaving voice channel (simplified)

### Level Calculation
Levels are calculated using the XP_TABLE in `config/constants.py`:
- Level 1: 0 XP
- Level 2: 100 XP
- Level 3: 250 XP
- Level 5: 700 XP
- Level 10: 3,200 XP
- Level 20: 20,000 XP
- Level 50: 160,000 XP

---

## 🚀 Deployment Instructions

### 1. Pull Latest Changes
```bash
cd /home/malabot/MalaBoT
git pull origin main
```

### 2. Restart Bot
```bash
pkill -f bot.py
nohup python3 bot.py > data/logs/latest.log 2>&1 &
```

### 3. Sync Commands (IMPORTANT!)
```
/sync
```
- Run this command in Discord
- Wait 5 minutes
- Restart Discord client
- This ensures all command changes take effect

### 4. Configure XP System
```
/setup
```
- Select "XP System"
- Configure all settings
- Test with `/rank` and sending messages

---

## ✅ Testing Checklist

After deployment, test these features:

- [ ] `/setup` → "XP System" opens correctly
- [ ] Can set level-up channel
- [ ] Can configure Message XP
- [ ] Can configure Reaction XP
- [ ] Can configure Voice XP
- [ ] Can configure XP Cooldown
- [ ] Can set custom level-up message
- [ ] `/setup` → "View Current Config" shows all XP settings
- [ ] Sending messages awards XP
- [ ] Receiving reactions awards XP
- [ ] Joining/leaving voice awards XP
- [ ] Level-up messages appear in configured channel
- [ ] `/xplevelrole` commands work
- [ ] Level roles are assigned on level-up
- [ ] `/rank` shows correct information
- [ ] `/leaderboard` displays correctly
- [ ] `/daily` bonus works
- [ ] Roast system still works

---

## 🐛 Troubleshooting

### XP Not Being Awarded
1. Check if XP amounts are set (not 0)
2. Verify cooldown isn't too high
3. Check bot has permission to read messages
4. Ensure user isn't a bot

### Level-up Messages Not Appearing
1. Verify level-up channel is set
2. Check bot has permission to send messages in that channel
3. Ensure user actually leveled up (check with `/rank`)

### Channel Selection Not Working
1. Run `/sync` command
2. Wait 5 minutes
3. Restart Discord client
4. Try again

### Level Roles Not Being Assigned
1. Check bot has "Manage Roles" permission
2. Ensure bot's role is higher than the role being assigned
3. Verify role exists and isn't deleted
4. Check `/xplevelrole list` to see configured roles

---

## 📝 Notes

- **Reaction XP**: Awarded to message author, not the reactor
- **Voice XP**: Currently simplified (awards on leave), can be enhanced later
- **Cooldown**: Only applies to message XP, not reactions or voice
- **Level Roles**: Permanent once assigned, not removed if XP is lost
- **Roast XP**: Separate system for bot's own progression

---

## 🎉 Benefits

1. **Predictable Progression**: Users know exactly how much XP they'll gain
2. **Multiple XP Sources**: Rewards different types of engagement
3. **Highly Configurable**: Each server can customize to their needs
4. **Fair System**: Cooldowns prevent spam, fixed amounts ensure fairness
5. **Engaging**: Level roles and roast system add fun elements
6. **Transparent**: Users can see all settings via `/setup`

---

## 🔮 Future Enhancements

Potential improvements for later:

1. **Voice XP Tracking**: Track actual time spent in voice, award periodically
2. **XP Multipliers**: Boost events, premium roles, etc.
3. **XP Leaderboard Roles**: Auto-assign roles to top 3 users
4. **Weekly/Monthly Resets**: Seasonal leaderboards
5. **XP Transfer**: Allow users to gift XP to others
6. **Achievement System**: Special XP bonuses for milestones
7. **Bot Level-up Announcements**: Celebrate when bot levels up in roast system

---

## 📞 Support

If you encounter any issues:
1. Check this documentation
2. Review the troubleshooting section
3. Check bot logs: `data/logs/latest.log`
4. Verify all commands are synced with `/sync`

---

**Last Updated**: January 2025
**Version**: 2.0
**Status**: Production Ready ✅