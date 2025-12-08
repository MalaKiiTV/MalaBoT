"""
Database migration script to convert from mixed global/per-guild system to fully per-guild system.

This script will:
1. Add guild_id column to tables that are missing it
2. Migrate data from global tables to per-guild tables
3. Remove unused global columns
4. Update database schema to be fully per-guild
"""

import aiosqlite
import sys
from typing import Optional

async def migrate_database(db_path: str) -> None:
    """Migrate database to fully per-guild system."""
    
    print("🔄 Starting migration to fully per-guild system...")
    
    try:
        # Connect to database
        conn = await aiosqlite.connect(db_path)
        
        # Enable foreign keys
        await conn.execute("PRAGMA foreign_keys = ON")
        
        # Start transaction
        await conn.execute("BEGIN TRANSACTION")
        
        print("✅ Connected to database")
        
        # Step 1: Add guild_id to tables that are missing it
        print("📝 Adding guild_id columns to tables...")
        
        # Add guild_id to roast_log if missing
        try:
            await conn.execute("ALTER TABLE roast_log ADD COLUMN guild_id INTEGER")
            print("  ✅ Added guild_id to roast_log")
        except aiosqlite.OperationalError as e:
            if "duplicate column name" not in str(e):
                print(f"  ⚠️  Error adding guild_id to roast_log: {e}")
        
        # Add guild_id to verifications if missing
        try:
            await conn.execute("ALTER TABLE verifications ADD COLUMN guild_id INTEGER")
            print("  ✅ Added guild_id to verifications")
        except aiosqlite.OperationalError as e:
            if "duplicate column name" not in str(e):
                print(f"  ⚠️  Error adding guild_id to verifications: {e}")
        
        # Step 2: Migrate birthdays from global to per-guild
        print("📦 Migrating birthdays to per-guild system...")
        
        # Check if we need to migrate birthdays
        cursor = await conn.execute("SELECT COUNT(*) FROM birthdays WHERE guild_id IS NULL")
        global_birthdays_count = (await cursor.fetchone())[0]
        
        if global_birthdays_count > 0:
            print(f"  Found {global_birthdays_count} global birthdays to migrate")
            
            # For each guild, migrate global birthdays
            cursor = await conn.execute("SELECT DISTINCT guild_id FROM settings WHERE guild_id IS NOT NULL")
            guilds = await cursor.fetchall()
            
            for (guild_id,) in guilds:
                # Migrate global birthdays to this guild
                await conn.execute(
                    """
                    INSERT OR IGNORE INTO birthdays (user_id, guild_id, birthday, timezone, created_at)
                    SELECT user_id, ?, birthday, timezone, created_at
                    FROM birthdays 
                    WHERE guild_id IS NULL AND user_id NOT IN (
                        SELECT user_id FROM birthdays WHERE guild_id = ?
                    )
                """,
                    (guild_id, guild_id)
                )
            
            # Delete remaining global birthdays
            await conn.execute("DELETE FROM birthdays WHERE guild_id IS NULL")
            print("  ✅ Migrated all global birthdays to per-guild")
        else:
            print("  ✅ No global birthdays found, birthdays already per-guild")
        
        # Step 3: Migrate XP from global users table to per-guild user_xp table
        print("📦 Migrating XP from global to per-guild system...")
        
        # Check if we need to migrate XP
        cursor = await conn.execute("SELECT COUNT(*) FROM users WHERE xp > 0")
        global_xp_count = (await cursor.fetchone())[0]
        
        if global_xp_count > 0:
            print(f"  Found {global_xp_count} users with global XP to migrate")
            
            # Get all guilds to migrate XP to
            cursor = await conn.execute("SELECT DISTINCT guild_id FROM settings WHERE guild_id IS NOT NULL")
            guilds = await cursor.fetchall()
            
            for (guild_id,) in guilds:
                # Migrate global XP to this guild
                await conn.execute(
                    """
                    INSERT OR REPLACE INTO user_xp (user_id, guild_id, xp, level, last_message_time)
                    SELECT user_id, ?, xp, level, datetime('now')
                    FROM users 
                    WHERE xp > 0
                """,
                    (guild_id,)
                )
            
            print("  ✅ Migrated all global XP to per-guild")
        else:
            print("  ✅ No global XP found, XP already per-guild")
        
        # Step 4: Update unique constraints for per-guild tables
        print("🔧 Updating table constraints...")
        
        # Update daily_checkins unique constraint
        try:
            # Drop old unique constraint if exists
            await conn.execute("DROP INDEX IF EXISTS idx_daily_checkins_user_id")
            await conn.execute("DROP INDEX IF EXISTS sqlite_autoindex_daily_checkins_1")
        except:
            pass
        
        # Create new composite unique constraint
        try:
            await conn.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_checkins_user_guild 
                ON daily_checkins (user_id, guild_id)
            """
            )
            print("  ✅ Updated daily_checkins unique constraint")
        except aiosqlite.OperationalError as e:
            print(f"  ⚠️  Error updating daily_checkins constraint: {e}")
        
        # Step 5: Clean up unused global columns (optional - keep for backup)
        print("🧹 Cleaning up unused global columns...")
        
        # Remove global XP and level columns from users table
        try:
            await conn.execute("ALTER TABLE users DROP COLUMN xp")
            await conn.execute("ALTER TABLE users DROP COLUMN level")
            print("  ✅ Removed global xp and level columns from users table")
        except aiosqlite.OperationalError as e:
            print(f"  ⚠️  Error removing global columns: {e}")
        
        # Remove global birthday column from users table
        try:
            await conn.execute("ALTER TABLE users DROP COLUMN birthday")
            print("  ✅ Removed global birthday column from users table")
        except aiosqlite.OperationalError as e:
            print(f"  ⚠️  Error removing birthday column: {e}")
        
        # Commit transaction
        await conn.commit()
        print("✅ Migration completed successfully!")
        
        # Print summary
        print("\n📊 Migration Summary:")
        cursor = await conn.execute("SELECT COUNT(*) FROM user_xp")
        xp_records = (await cursor.fetchone())[0]
        
        cursor = await conn.execute("SELECT COUNT(*) FROM birthdays WHERE guild_id IS NOT NULL")
        birthday_records = (await cursor.fetchone())[0]
        
        print(f"  • Total per-guild XP records: {xp_records}")
        print(f"  • Total per-guild birthday records: {birthday_records}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        await conn.rollback()
        await conn.close()
        sys.exit(1)

async def verify_migration(db_path: str) -> None:
    """Verify that the migration was successful."""
    
    print("\n🔍 Verifying migration...")
    
    try:
        conn = await aiosqlite.connect(db_path)
        
        # Check that all tables have proper guild_id columns
        tables_to_check = [
            'user_xp', 'birthdays', 'verifications', 'appeals', 
            'daily_checkins', 'roast_log', 'mod_logs', 'level_roles'
        ]
        
        for table in tables_to_check:
            cursor = await conn.execute(f"PRAGMA table_info({table})")
            columns = await cursor.fetchall()
            has_guild_id = any(col[1] == 'guild_id' for col in columns)
            
            if has_guild_id:
                print(f"  ✅ {table} has guild_id column")
            else:
                print(f"  ❌ {table} missing guild_id column")
        
        # Check that users table doesn't have global data columns
        cursor = await conn.execute("PRAGMA table_info(users)")
        columns = await cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        global_columns = ['xp', 'level', 'birthday']
        for col in global_columns:
            if col in column_names:
                print(f"  ⚠️  users table still has global {col} column")
            else:
                print(f"  ✅ users table doesn't have global {col} column")
        
        # Check data consistency
        cursor = await conn.execute("SELECT COUNT(*) FROM user_xp")
        xp_count = (await cursor.fetchone())[0]
        
        cursor = await conn.execute("SELECT COUNT(*) FROM birthdays WHERE guild_id IS NOT NULL")
        birthday_count = (await cursor.fetchone())[0]
        
        print(f"  📊 Found {xp_count} XP records and {birthday_count} birthday records")
        
        if xp_count > 0 and birthday_count > 0:
            print("  ✅ Data appears to be properly migrated")
        else:
            print("  ⚠️  Some data may be missing - please verify")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    import asyncio
    
    if len(sys.argv) != 2:
        print("Usage: python migrate_to_full_per_guild.py <database_path>")
        print("Example: python migrate_to_full_per_guild.py data/bot.db")
        sys.exit(1)
    
    db_path = sys.argv[1]
    
    async def main():
        await migrate_database(db_path)
        await verify_migration(db_path)
    
    asyncio.run(main())