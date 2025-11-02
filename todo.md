# MalaBoT Repair Plan

## Issues Identified
- Startup errors in logs
- Old/broken files cluttering repository
- Discord slash commands not registering/showing up
- Multiple conflicting bot files (bot.py, bot_broken.py, bot_fixed.py)
- Patch files that should be applied and cleaned up

## Cleanup Tasks
- [ ] Remove broken/unused files:
  - bot_broken.py
  - bot_fixed.py
  - All .patch files
  - Test files (test_*.py)
  - fix_*.py files
  - Database backup files (models.py.backup, models_broken.py)
  - Old XP cogs (xp_old.py, xp_old_working.py)
- [ ] Clean up temporary files
  - temp.sql
- [ ] Update FIXES_APPLIED.md with current status

## Bot Code Analysis
- [ ] Analyze current bot.py for command registration issues
- [ ] Check slash command implementation in cogs
- [ ] Verify database models are correct
- [ ] Test database initialization

## Command Registration Fix
- [ ] Fix command tree sync issues
- [ ] Ensure all slash commands are properly registered
- [ ] Verify command groups work correctly
- [ ] Test command registration in debug vs production mode

## Testing & Validation
- [ ] Create test script to validate bot startup
- [ ] Test slash command registration
- [ ] Verify database connectivity
- [ ] Test cog loading

## Final Steps
- [ ] Commit all fixes to GitHub
- [ ] Provide clear instructions for testing