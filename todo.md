# Restructure XP Commands - COMPLETED ✅

## Goal
Reorganize all XP commands under a single `/xp` parent command group with proper subcommands.

## Tasks

### 1. Create XP Command Group ✅
- [x] Convert XP cog to use command groups
- [x] Create parent `/xp` group

### 2. Move Existing Commands Under /xp ✅
- [x] `/rank` → `/xp rank [user]`
- [x] `/leaderboard` → `/xp leaderboard`
- [x] `/daily` → `/xp checkin` (removed /daily)
- [x] `/xpadd` → `/xp add <user> <amount>`
- [x] `/xpremove` → `/xp remove <user> <amount>`
- [x] `/xpset` → `/xp set <user> <amount>`
- [x] `/xpreset` → `/xp reset <user>` and `/xp reset-all <confirm>`

### 3. Add New Commands ✅
- [x] `/xp add-all <amount> <confirm>` - Add XP to ALL users in server

### 4. Remove Commands ✅
- [x] Remove `/xplevelrole` command (moved to /setup)
- [x] Remove `/daily` command (replaced by /xp checkin)

### 5. Update /setup ✅
- [x] Add level roles management to XP Setup menu
- [x] Add "Manage Level Roles" button
- [x] Create LevelRolesView with Add/Remove/Back buttons
- [x] Add Level Role - Assign role at specific level
- [x] Remove Level Role - Remove level role reward
- [x] Back button to return to XP setup

### 6. Testing & Deployment
- [x] Test all commands compile
- [ ] Commit changes
- [ ] Push to GitHub
- [ ] User deploys and tests

## Final Command Structure ✅

```
/xp (parent command group)
├── rank [user] - Check XP/level (Anyone) ✅
├── leaderboard - Show XP leaderboard (Anyone) ✅
├── checkin - Daily XP bonus (Anyone, replaces /daily) ✅
├── add <user> <amount> - Add XP to user (Server Owner) ✅
├── add-all <amount> <confirm> - Add XP to ALL users (Server Owner) ✅
├── remove <user> <amount> - Remove XP from user (Server Owner) ✅
├── set <user> <amount> - Set user's XP (Server Owner) ✅
├── reset <user> - Reset user's XP (Server Owner) ✅
└── reset-all <confirm> - Reset ALL users' XP (Server Owner) ✅
```

## Level Roles in /setup ✅

```
/setup → XP System → Manage Level Roles
├── Add Level Role - Input level and role
├── Remove Level Role - Input level to remove
└── Back to XP Setup
```

## Changes Summary

### cogs/xp.py
- Complete rewrite using command groups
- All commands now under `/xp` parent
- Removed `/xplevelrole` command
- Removed `/daily` command
- Added `/xp checkin` (replacement for /daily)
- Added `/xp add-all` for bulk XP addition
- Renamed all admin commands to subcommands
- Kept all XP gain listeners (message, reaction, voice)
- Kept level-up handling and level role assignment

### cogs/setup.py
- Added "Manage Level Roles" button to XPSetupView
- Created new LevelRolesView class
- Add Level Role functionality
- Remove Level Role functionality
- Back button navigation

## Ready for Deployment ✅
All code is complete and compiles successfully. Ready to commit and push.