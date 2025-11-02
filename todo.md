# MalaBoT Repair Plan

## Issues Identified
- Startup errors in logs
- Old/broken files cluttering repository
- Discord slash commands not registering/showing up
- Multiple conflicting bot files (bot.py, bot_broken.py, bot_fixed.py)
- Patch files that should be applied and cleaned up

## Cleanup Tasks
- [x] Remove broken/unused files:
  - bot_broken.py
  - bot_fixed.py
  - All .patch files
  - Test files (test_*.py)
  - fix_*.py files
  - Database backup files (models.py.backup, models_broken.py)
  - Old XP cogs (xp_old.py, xp_old_working.py)
- [x] Clean up temporary files
  - temp.sql
- [ ] Update FIXES_APPLIED.md with current status

## Bot Code Analysis
- [x] Analyze current bot.py for command registration issues
- [x] Check slash command implementation in cogs
- [x] Verify database models are correct
- [x] Test database initialization

## Command Registration Fix
- [x] Fix command tree sync issues
- [x] Ensure all slash commands are properly registered
- [x] Verify command groups work correctly
- [x] Test command registration in debug vs production mode

## Database Fixes
- [x] Fix role_level column reference in XP cog
- [x] Fixed level_roles table column name mismatch

## Testing & Validation
- [x] Create test script to validate bot startup
- [x] Test slash command registration
- [x] Verify database connectivity
- [x] Test cog loading

## Final Steps
- [ ] Commit all fixes to GitHub
- [ ] Provide clear instructions for testing