# XP System Configuration Guide

## 📊 Current XP Settings

All XP settings are in `config/constants.py`

### Message XP Rewards
```python
XP_PER_MESSAGE_MIN = 5      # Minimum XP per message
XP_PER_MESSAGE_MAX = 15     # Maximum XP per message
XP_COOLDOWN_SECONDS = 60    # Cooldown between XP gains (60 seconds)
```

**How it works:**
- Users earn 5-15 XP (random) for each message
- Can only earn XP once per 60 seconds
- Prevents spam for XP farming

### Daily Bonus
```python
DAILY_CHECKIN_XP = 50       # Base daily bonus
STREAK_BONUS_PERCENT = 10   # 10% bonus per streak day
```

**How it works:**
- Users get 50 XP for `/daily` command
- Streak bonus: Day 1 = 50 XP, Day 2 = 55 XP, Day 3 = 60 XP, etc.
- Streak resets if user misses a day

### Level Requirements
```python
XP_TABLE = {
    1: 0,           # Level 1 starts at 0 XP
    2: 100,         # Level 2 requires 100 XP
    3: 250,         # Level 3 requires 250 XP
    4: 450,         # Level 4 requires 450 XP
    5: 700,         # Level 5 requires 700 XP
    6: 1000,        # Level 6 requires 1,000 XP
    7: 1400,
    8: 1900,
    9: 2500,
    10: 3200,
    11: 4000,
    12: 5000,
    13: 6200,
    14: 7600,
    15: 9200,
    16: 11000,
    17: 13000,
    18: 15000,
    19: 17000,
    20: 20000,
    25: 30000,
    30: 45000,
    35: 65000,
    40: 90000,
    45: 120000,
    50: 160000,
}
```

---

## 🎯 How to Configure XP

### 1. Change XP Per Message
Edit `config/constants.py`:
```python
XP_PER_MESSAGE_MIN = 10     # Change from 5 to 10
XP_PER_MESSAGE_MAX = 25     # Change from 15 to 25
```

### 2. Change XP Cooldown
```python
XP_COOLDOWN_SECONDS = 30    # Change from 60 to 30 seconds
```
⚠️ Lower cooldown = more XP farming potential

### 3. Change Daily Bonus
```python
DAILY_CHECKIN_XP = 100      # Change from 50 to 100
STREAK_BONUS_PERCENT = 20   # Change from 10% to 20%
```

### 4. Adjust Level Requirements
Make leveling easier:
```python
XP_TABLE = {
    1: 0,
    2: 50,      # Easier (was 100)
    3: 150,     # Easier (was 250)
    4: 300,     # Easier (was 450)
    5: 500,     # Easier (was 700)
    # ... etc
}
```

Or make it harder:
```python
XP_TABLE = {
    1: 0,
    2: 200,     # Harder (was 100)
    3: 500,     # Harder (was 250)
    4: 900,     # Harder (was 450)
    5: 1400,    # Harder (was 700)
    # ... etc
}
```

---

## 🎭 Level-Based Roles (NOT CURRENTLY IMPLEMENTED)

To add role rewards for levels, you need to:

### 1. Create the roles in Discord
Example roles:
- Level 5: "Active Member"
- Level 10: "Veteran"
- Level 20: "Elite"
- Level 30: "Legend"

### 2. Add role configuration to `config/constants.py`
```python
# Level role rewards
LEVEL_ROLES = {
    5: "Active Member",
    10: "Veteran",
    20: "Elite",
    30: "Legend",
    50: "God Tier"
}
```

### 3. Modify `cogs/xp.py` to award roles
In the `_handle_level_up` method, add:
```python
async def _handle_level_up(self, member: discord.Member, guild: discord.Guild, new_level: int, old_level: int):
    """Handle user level up."""
    try:
        # ... existing code ...
        
        # Check if this level has a role reward
        from config.constants import LEVEL_ROLES
        if new_level in LEVEL_ROLES:
            role_name = LEVEL_ROLES[new_level]
            role = discord.utils.get(guild.roles, name=role_name)
            
            if role:
                await member.add_roles(role)
                # Add to level up message
                embed.add_field(
                    name="🎭 Role Unlocked!",
                    value=f"You earned the **{role_name}** role!",
                    inline=False
                )
```

---

## 🔒 Level-Based Channel Access (NOT CURRENTLY IMPLEMENTED)

To restrict channels by level:

### 1. Create private channels
Example:
- #level-10-lounge (requires level 10)
- #elite-chat (requires level 20)

### 2. Add channel configuration
```python
# Level-based channel access
LEVEL_CHANNELS = {
    10: ["level-10-lounge"],
    20: ["elite-chat", "elite-voice"],
    30: ["legends-only"]
}
```

### 3. Implement access check
Create a new command or modify existing:
```python
@app_commands.command(name="check-access")
async def check_access(self, interaction: discord.Interaction):
    """Check which channels you can access based on level."""
    user_data = await self.bot.db_manager.get_user(interaction.user.id)
    level = user_data.get('level', 1)
    
    accessible_channels = []
    for req_level, channels in LEVEL_CHANNELS.items():
        if level >= req_level:
            accessible_channels.extend(channels)
    
    # Show user their accessible channels
```

---

## 📈 XP Calculation Examples

### Example 1: Active User
- Sends 20 messages/day (avg 10 XP each) = 200 XP
- Claims daily bonus = 50 XP
- **Total per day: 250 XP**
- **Reaches Level 3 in 1 day**
- **Reaches Level 5 in 3 days**

### Example 2: Casual User
- Sends 5 messages/day (avg 10 XP each) = 50 XP
- Claims daily bonus = 50 XP
- **Total per day: 100 XP**
- **Reaches Level 2 in 1 day**
- **Reaches Level 5 in 7 days**

### Example 3: With Streak Bonus
- Day 1: 250 XP (200 messages + 50 daily)
- Day 2: 255 XP (200 messages + 55 daily with 10% streak)
- Day 3: 260 XP (200 messages + 60 daily with 20% streak)
- **3-day total: 765 XP (Level 5+)**

---

## 🛠️ Quick Configuration Templates

### Template 1: Fast Progression (Casual Server)
```python
XP_PER_MESSAGE_MIN = 15
XP_PER_MESSAGE_MAX = 30
XP_COOLDOWN_SECONDS = 30
DAILY_CHECKIN_XP = 100
STREAK_BONUS_PERCENT = 20

XP_TABLE = {
    1: 0, 2: 50, 3: 150, 4: 300, 5: 500,
    10: 1500, 15: 3500, 20: 7000
}
```

### Template 2: Slow Progression (Competitive Server)
```python
XP_PER_MESSAGE_MIN = 3
XP_PER_MESSAGE_MAX = 8
XP_COOLDOWN_SECONDS = 120
DAILY_CHECKIN_XP = 25
STREAK_BONUS_PERCENT = 5

XP_TABLE = {
    1: 0, 2: 200, 3: 500, 4: 1000, 5: 1800,
    10: 5000, 15: 12000, 20: 25000
}
```

### Template 3: Balanced (Current Settings)
```python
XP_PER_MESSAGE_MIN = 5
XP_PER_MESSAGE_MAX = 15
XP_COOLDOWN_SECONDS = 60
DAILY_CHECKIN_XP = 50
STREAK_BONUS_PERCENT = 10

# Use default XP_TABLE
```

---

## 🔄 Applying Changes

After editing `config/constants.py`:

1. Save the file
2. Restart the bot (`dev.bat → Option 2` then `Option 1`)
3. Changes take effect immediately
4. Existing user XP is preserved

---

## 📊 Monitoring XP System

### Check User Stats
```
/rank @user
```

### Check Leaderboard
```
/leaderboard
```

### Check Your Progress
```
/rank
```

---

**Last Updated**: January 27, 2025
**Current Version**: v1.0