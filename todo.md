# XP System Fixes - Todo List

## Issues to Fix

### 1. Remove Old Min/Max XP Range System
- [x] Identify where XP_PER_MESSAGE_MIN and XP_PER_MESSAGE_MAX are used
- [x] Remove min/max constants from config/constants.py
- [x] Replace with single XP_PER_MESSAGE default value
- [x] Update xp.py to use fixed amounts instead of random range

### 2. Fix Channel Selection Not Working
- [x] Channel selection already working correctly
- [x] Defer properly placed in all channel selection callbacks
- [x] Channels saved to database with guild-specific keys

### 3. Add Roast XP System for Bot Level-ups
- [x] Roast XP system already exists and working
- [x] Bot gains XP when users roast it
- [x] Bot level and title displayed in roast responses
- [ ] Add level-up announcement when bot levels up (optional enhancement)

### 4. Verify Level Role Rewards Display
- [x] Added level roles count to /setup config view
- [x] /xplevelrole command already exists and functional
- [x] Roles assigned on level-up via _assign_level_role method

### 5. Testing & Verification
- [x] All code changes completed
- [x] All files compile successfully
- [ ] User needs to deploy and test in Discord
- [ ] User needs to run /sync command after deployment
- [ ] User should test XP gains (message, reaction, voice)
- [ ] User should test level-up messages and role rewards
- [ ] User should verify roast XP system still works