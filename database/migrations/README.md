# Database Migrations

This folder contains database migration scripts for the MalaBoT Discord bot.

## Executed Migrations

### migrate_appeals_table.py
- **Executed:** October 30, 2024
- **Purpose:** Remove UNIQUE constraint from appeals table
- **Changes:**
  - Allows users to submit one appeal per jail session
  - Users can appeal again after leaving and rejoining
  - Pending appeals are automatically cancelled when user leaves
- **Status:** ✅ Successfully executed

## Running Migrations

Migrations in this folder have already been executed. They are kept for reference and documentation purposes.

If you need to run a migration on a new database:
1. Review the migration script
2. Ensure database backup exists
3. Run: `python3 migrate_appeals_table.py`
4. Verify the migration was successful

## Notes

- Always backup your database before running migrations
- Test migrations on a development database first
- Document any new migrations added to this folder