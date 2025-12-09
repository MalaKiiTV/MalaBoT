# Archived Files - SQLite Migration

This directory contains files from the original SQLite implementation that have been replaced by Supabase.

## Contents

### `/sqlite_migrations/`
- `models.py` - Original SQLite database models
- `migrate_appeals_table.py` - SQLite migration script
- `migrate_to_per_guild_data.py` - SQLite migration script  
- `add_component_to_health_logs.py` - SQLite migration script
- `migrate_settings_table.py` - SQLite migration script

### Root Archive Files
- `migrate_to_supabase.py` - One-time migration script used to move from SQLite to Supabase
- `fix_birthdays.py` - Script to fix birthday data format during migration
- `bot.db.backup_*` - SQLite database backups

## Why These Were Archived

- **Supabase Migration**: The bot has been fully migrated to Supabase for better scalability and cloud sync
- **Code Cleanup**: Removing SQLite dependencies simplifies the codebase
- **Maintenance**: Only one database system to maintain (Supabase)

## When to Use These Files

- **Rollback**: If you need to revert to SQLite for any reason
- **Reference**: To understand the original database structure
- **Debugging**: To compare with Supabase implementation if issues arise

## Important Notes

- These files are no longer used by the active bot
- The current implementation uses `database/supabase_models.py`
- Environment variables should now use `SUPABASE_URL` and `SUPABASE_KEY`
- SQLite `DATABASE_URL` is deprecated but kept for fallback compatibility

## Migration Date

These files were archived on: **2024-12-08**

The migration to Supabase was completed as part of the bot's infrastructure upgrade.