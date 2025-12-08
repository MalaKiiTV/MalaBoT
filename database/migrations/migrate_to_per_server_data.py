"""
Database migration to implement per-server user data storage.
This migration adds guild_id to tables that currently store global user data.
"""

import aiosqlite
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import DatabaseManager
from config.settings import settings


async def migrate_to_per_server_data():
    """Migrate database to per-server data architecture."""
    
    # Get database path from settings
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    if settings.DATABASE_URL.startswith("sqlite://"):
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    else:
        db_path = settings.DATABASE_URL
    
    print(f"Connecting to database: {db_path}")
    
    async with aiosqlite.connect(db_path) as conn:
        print("Starting per-server data migration...")
        
        # Enable foreign keys
        await conn.execute("PRAGMA foreign_keys = ON")
        
        # 1. Add guild_id to users table
        print("1. Adding guild_id to users table...")
        try:
            # Check if column already exists
            cursor = await conn.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in await cursor.fetchall()]
            
            if 'guild_id' not in columns:
                # Add guild_id column
                await conn.execute("ALTER TABLE users ADD COLUMN guild_id INTEGER")
                
                # Since existing data is global, we need to assign it to all guilds
                # Get all current users
                cursor = await conn.execute("SELECT DISTINCT user_id FROM users")
                users = await cursor.fetchall()
                
                print(f"   Migrating {len(users)} users to per-server format...")
                
                # For each user, we need to create entries for each guild they're in
                # Since we don't have guild history, we'll create entries for all current guilds
                cursor = await conn.execute("SELECT DISTINCT guild_id FROM settings WHERE guild_id IS NOT NULL")
                guilds = await cursor.fetchall()
                
                if not guilds:
                    print("   Warning: No guild settings found. Creating default guild entry.")
                    # Create a default guild entry (guild_id 0 for global/unknown)
                    await conn.execute("UPDATE users SET guild_id = 0 WHERE guild_id IS NULL")
                else:
                    guild_ids = [guild[0] for guild in guilds]
                    print(f"   Found {len(guild_ids)} guilds in settings")
                    
                    # For each user, create copies for each guild
                    for (user_id,) in users:
                        cursor = await conn.execute("SELECT * FROM users WHERE user_id = ? AND guild_id IS NULL", (user_id,))
                        user_data = await cursor.fetchone()
                        
                        if user_data:
                            # Get column names
                            cursor = await conn.execute("PRAGMA table_info(users)")
                            columns = [row[1] for row in await cursor.fetchall()]
                            
                            # Prepare data for insertion (skip original user_id, set guild_id)
                            for guild_id in guild_ids:
                                # Build insert query excluding auto-increment id and original guild_id
                                cols_to_insert = [col for col in columns if col not in ['id', 'guild_id']]
                                placeholders = ', '.join(['?' for _ in cols_to_insert])
                                cols_str = ', '.join(cols_to_insert)
                                
                                # Get values for the columns
                                values = []
                                for i, col in enumerate(columns):
                                    if col not in ['id', 'guild_id']:
                                        values.append(user_data[i])
                                
                                # Insert with guild_id
                                await conn.execute(
                                    f"INSERT INTO users ({cols_str}, guild_id) VALUES ({placeholders}, ?)",
                                    values + [guild_id]
                                )
                    
                    # Remove the original global entries
                    await conn.execute("DELETE FROM users WHERE guild_id IS NULL")
                
                print("   ✓ Users table migrated")
            else:
                print("   ✓ guild_id column already exists in users table")
                
        except Exception as e:
            print(f"   ✗ Error migrating users table: {e}")
            raise
        
        # 2. Add guild_id to birthdays table
        print("2. Adding guild_id to birthdays table...")
        try:
            cursor = await conn.execute("PRAGMA table_info(birthdays)")
            columns = [row[1] for row in await cursor.fetchall()]
            
            if 'guild_id' not in columns:
                await conn.execute("ALTER TABLE birthdays ADD COLUMN guild_id INTEGER")
                
                # Migrate existing birthdays to all guilds
                cursor = await conn.execute("SELECT * FROM birthdays WHERE guild_id IS NULL")
                birthdays = await cursor.fetchall()
                
                cursor = await conn.execute("SELECT DISTINCT guild_id FROM settings WHERE guild_id IS NOT NULL")
                guilds = await cursor.fetchall()
                
                if guilds:
                    guild_ids = [guild[0] for guild in guilds]
                    
                    for birthday in birthdays:
                        for guild_id in guild_ids:
                            await conn.execute(
                                "INSERT INTO birthdays (user_id, birthday, timezone, announced_year, created_at, guild_id) VALUES (?, ?, ?, ?, ?, ?)",
                                (birthday[1], birthday[2], birthday[3], birthday[4], birthday[5], guild_id)
                            )
                    
                    # Remove original global entries
                    await conn.execute("DELETE FROM birthdays WHERE guild_id IS NULL")
                
                print("   ✓ Birthdays table migrated")
            else:
                print("   ✓ guild_id column already exists in birthdays table")
                
        except Exception as e:
            print(f"   ✗ Error migrating birthdays table: {e}")
            raise
        
        # 3. Add guild_id to daily_checkins table
        print("3. Adding guild_id to daily_checkins table...")
        try:
            cursor = await conn.execute("PRAGMA table_info(daily_checkins)")
            columns = [row[1] for row in await cursor.fetchall()]
            
            if 'guild_id' not in columns:
                await conn.execute("ALTER TABLE daily_checkins ADD COLUMN guild_id INTEGER")
                
                # Migrate existing checkins to all guilds
                cursor = await conn.execute("SELECT * FROM daily_checkins WHERE guild_id IS NULL")
                checkins = await cursor.fetchall()
                
                cursor = await conn.execute("SELECT DISTINCT guild_id FROM settings WHERE guild_id IS NOT NULL")
                guilds = await cursor.fetchall()
                
                if guilds:
                    guild_ids = [guild[0] for guild in guilds]
                    
                    for checkin in checkins:
                        for guild_id in guild_ids:
                            await conn.execute(
                                "INSERT INTO daily_checkins (user_id, last_checkin, checkin_streak, created_at, guild_id) VALUES (?, ?, ?, ?, ?)",
                                (checkin[1], checkin[2], checkin[3], checkin[4], guild_id)
                            )
                    
                    # Remove original global entries
                    await conn.execute("DELETE FROM daily_checkins WHERE guild_id IS NULL")
                
                print("   ✓ Daily checkins table migrated")
            else:
                print("   ✓ guild_id column already exists in daily_checkins table")
                
        except Exception as e:
            print(f"   ✗ Error migrating daily_checkins table: {e}")
            raise
        
        # 4. Create new composite primary keys and constraints
        print("4. Creating new constraints...")
        try:
            # Note: SQLite doesn't support ALTER TABLE to add primary keys to existing tables
            # We'll need to recreate tables, but for now we'll add unique constraints
            
            # Create unique constraints for per-server data
            await conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_user_guild ON users(user_id, guild_id)")
            await conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_birthdays_user_guild ON birthdays(user_id, guild_id)")
            await conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_checkins_user_guild ON daily_checkins(user_id, guild_id)")
            
            print("   ✓ Unique constraints created")
            
        except Exception as e:
            print(f"   ✗ Error creating constraints: {e}")
            raise
        
        # 5. Update existing database manager methods
        print("5. Migration completed successfully!")
        print("\nNext steps:")
        print("1. Update DatabaseManager methods to use guild_id")
        print("2. Update all cog methods to pass guild_id")
        print("3. Implement proper on_member_remove handlers")
        print("4. Test the new per-server functionality")
        
        await conn.commit()
        print("   ✓ Database changes committed")


if __name__ == "__main__":
    import asyncio
    
    async def main():
        try:
            await migrate_to_per_server_data()
            print("\n🎉 Migration completed successfully!")
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(main())