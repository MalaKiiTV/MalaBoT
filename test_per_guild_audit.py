"""
Comprehensive test suite for fully per-guild implementation.
Tests all database operations to ensure complete data isolation between guilds.
"""

import asyncio
import aiosqlite
import os
import tempfile
from typing import Optional
import sys

# Add the project root to path so we can import the database models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.models import DatabaseManager


class PerGuildTester:
    """Test suite for per-guild functionality."""
    
    def __init__(self):
        self.test_db_path = tempfile.mktemp(suffix='.db')
        self.db_manager = DatabaseManager(self.test_db_path)
        
    async def setup(self) -> None:
        """Set up test database."""
        await self.db_manager.initialize()
        print("✅ Test database initialized")
        
    async def cleanup(self) -> None:
        """Clean up test database."""
        if self.db_manager._connection:
            await self.db_manager.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        print("✅ Test database cleaned up")
        
    async def get_fresh_db_manager(self):
        """Get a fresh database manager for each test."""
        fresh_db_path = tempfile.mktemp(suffix='.db')
        fresh_manager = DatabaseManager(fresh_db_path)
        await fresh_manager.initialize()
        return fresh_manager, fresh_db_path
    
    async def test_xp_isolation(self) -> bool:
        """Test that XP is properly isolated between guilds."""
        print("\n🧪 Testing XP isolation between guilds...")
        
        try:
            user_id = 987654321  # Use different ID to avoid conflicts
            guild1_id = 111111111
            guild2_id = 222222222
            
            # Ensure database connection is available
            await self.db_manager.get_connection()
            
            # Set XP for user in guild 1
            await self.db_manager.set_user_xp(user_id, guild1_id, 1000)
            xp_guild1 = await self.db_manager.get_user_xp(user_id, guild1_id)
            
            # Check that user has no XP in guild 2
            xp_guild2_initial = await self.db_manager.get_user_xp(user_id, guild2_id)
            
            # Set different XP for user in guild 2
            await self.db_manager.set_user_xp(user_id, guild2_id, 500)
            xp_guild2_updated = await self.db_manager.get_user_xp(user_id, guild2_id)
            xp_guild1_unchanged = await self.db_manager.get_user_xp(user_id, guild1_id)
            
            # Verify isolation
            assert xp_guild1 == 1000, f"Expected 1000 XP in guild 1, got {xp_guild1}"
            assert xp_guild2_initial == 0, f"Expected 0 XP in guild 2 initially, got {xp_guild2_initial}"
            assert xp_guild2_updated == 500, f"Expected 500 XP in guild 2, got {xp_guild2_updated}"
            assert xp_guild1_unchanged == 1000, f"Expected 1000 XP unchanged in guild 1, got {xp_guild1_unchanged}"
            
            print("  ✅ XP isolation test passed")
            return True
            
        except Exception as e:
            print(f"  ❌ XP isolation test failed: {e}")
            return False
    
    async def test_birthday_isolation(self) -> bool:
        """Test that birthdays are properly isolated between guilds."""
        print("\n🧪 Testing birthday isolation between guilds...")
        
        try:
            user_id = 123456789
            guild1_id = 111111111
            guild2_id = 222222222
            
            birthday = "1990-01-01"
            timezone = "UTC"
            
            # Ensure user exists first
            conn = await self.db_manager.get_connection()
            await conn.execute(
                "INSERT OR IGNORE INTO users (user_id, username, discriminator) VALUES (?, 'TestUser', '1234')",
                (user_id,)
            )
            await conn.commit()
            
            # Set birthday for user in guild 1
            await self.db_manager.set_birthday(user_id, guild1_id, birthday, timezone)
            birthday_guild1 = await self.db_manager.get_user_birthday(user_id, guild1_id)
            
            # Check that user has no birthday in guild 2
            birthday_guild2 = await self.db_manager.get_user_birthday(user_id, guild2_id)
            
            # Set different birthday for user in guild 2
            birthday2 = "1995-05-05"
            await self.db_manager.set_birthday(user_id, guild2_id, birthday2, timezone)
            birthday_guild2_updated = await self.db_manager.get_user_birthday(user_id, guild2_id)
            birthday_guild1_unchanged = await self.db_manager.get_user_birthday(user_id, guild1_id)
            
            # Verify isolation
            assert birthday_guild1 is not None, "Expected birthday to be set in guild 1"
            assert birthday_guild2 is None, f"Expected no birthday in guild 2 initially, got {birthday_guild2}"
            assert birthday_guild2_updated is not None, "Expected birthday to be set in guild 2"
            assert birthday_guild1_unchanged is not None, "Expected birthday to remain unchanged in guild 1"
            
            print("  ✅ Birthday isolation test passed")
            return True
            
        except Exception as e:
            print(f"  ❌ Birthday isolation test failed: {e}")
            return False
    
    async def test_user_cleanup(self) -> bool:
        """Test that user data is properly cleaned up when they leave a guild."""
        print("\n🧪 Testing user data cleanup on guild leave...")
        
        try:
            user_id = 123456789
            guild1_id = 111111111
            guild2_id = 222222222
            
            # Set up user data in both guilds
            await self.db_manager.set_user_xp(user_id, guild1_id, 1000)
            await self.db_manager.set_user_xp(user_id, guild2_id, 500)
            await self.db_manager.set_birthday(user_id, guild1_id, "1990-01-01")
            await self.db_manager.set_birthday(user_id, guild2_id, "1995-05-05")
            
            # Verify data exists in both guilds
            xp_guild1_before = await self.db_manager.get_user_xp(user_id, guild1_id)
            xp_guild2_before = await self.db_manager.get_user_xp(user_id, guild2_id)
            birthday_guild1_before = await self.db_manager.get_user_birthday(user_id, guild1_id)
            birthday_guild2_before = await self.db_manager.get_user_birthday(user_id, guild2_id)
            
            # Cleanup user data from guild 1
            cleanup_success = await self.db_manager.delete_user_data_from_guild(user_id, guild1_id)
            
            # Verify cleanup
            xp_guild1_after = await self.db_manager.get_user_xp(user_id, guild1_id)
            xp_guild2_after = await self.db_manager.get_user_xp(user_id, guild2_id)
            birthday_guild1_after = await self.db_manager.get_user_birthday(user_id, guild1_id)
            birthday_guild2_after = await self.db_manager.get_user_birthday(user_id, guild2_id)
            
            # Verify cleanup results
            assert cleanup_success, "Expected cleanup to succeed"
            assert xp_guild1_before == 1000, f"Expected 1000 XP in guild 1 before, got {xp_guild1_before}"
            assert xp_guild2_before == 500, f"Expected 500 XP in guild 2 before, got {xp_guild2_before}"
            assert xp_guild1_after == 0, f"Expected 0 XP in guild 1 after cleanup, got {xp_guild1_after}"
            assert xp_guild2_after == 500, f"Expected 500 XP unchanged in guild 2, got {xp_guild2_after}"
            assert birthday_guild1_before is not None, "Expected birthday in guild 1 before"
            assert birthday_guild2_before is not None, "Expected birthday in guild 2 before"
            assert birthday_guild1_after is None, f"Expected no birthday in guild 1 after cleanup, got {birthday_guild1_after}"
            assert birthday_guild2_after is not None, "Expected birthday to remain in guild 2"
            
            print("  ✅ User cleanup test passed")
            return True
            
        except Exception as e:
            print(f"  ❌ User cleanup test failed: {e}")
            return False
    
    async def test_leaderboard_isolation(self) -> bool:
        """Test that leaderboards are properly isolated between guilds."""
        print("\n🧪 Testing leaderboard isolation between guilds...")
        
        try:
            user1_id = 444444444  # Use different IDs to avoid conflicts
            user2_id = 555555555
            user3_id = 666666666
            guild1_id = 777777777
            guild2_id = 888888888
            
            # Set up different XP for users in different guilds
            await self.db_manager.set_user_xp(user1_id, guild1_id, 1000)  # User 1: 1000 XP in guild 1
            await self.db_manager.set_user_xp(user2_id, guild1_id, 500)   # User 2: 500 XP in guild 1
            await self.db_manager.set_user_xp(user1_id, guild2_id, 200)   # User 1: 200 XP in guild 2
            await self.db_manager.set_user_xp(user3_id, guild2_id, 800)   # User 3: 800 XP in guild 2
            
            # Check ranks in guild 1 (User 1 should be #1, User 2 should be #2)
            rank_user1_guild1 = await self.db_manager.get_user_rank(user1_id, guild1_id)
            rank_user2_guild1 = await self.db_manager.get_user_rank(user2_id, guild1_id)
            
            # Check ranks in guild 2 (User 3 should be #1, User 1 should be #2)
            rank_user1_guild2 = await self.db_manager.get_user_rank(user1_id, guild2_id)
            rank_user3_guild2 = await self.db_manager.get_user_rank(user3_id, guild2_id)
            
            # Verify rankings
            assert rank_user1_guild1 == 1, f"Expected User 1 to be rank 1 in guild 1, got {rank_user1_guild1}"
            assert rank_user2_guild1 == 2, f"Expected User 2 to be rank 2 in guild 1, got {rank_user2_guild1}"
            assert rank_user1_guild2 == 2, f"Expected User 1 to be rank 2 in guild 2, got {rank_user1_guild2}"
            assert rank_user3_guild2 == 1, f"Expected User 3 to be rank 1 in guild 2, got {rank_user3_guild2}"
            
            print("  ✅ Leaderboard isolation test passed")
            return True
            
        except Exception as e:
            print(f"  ❌ Leaderboard isolation test failed: {e}")
            return False
    
    async def test_settings_isolation(self) -> bool:
        """Test that settings are properly isolated between guilds."""
        print("\n🧪 Testing settings isolation between guilds...")
        
        try:
            guild1_id = 111111111
            guild2_id = 222222222
            
            key = "xp_progression_type"
            value1 = "custom"
            value2 = "basic"
            
            # Set different settings for each guild
            await self.db_manager.set_setting(key, value1, guild1_id)
            await self.db_manager.set_setting(key, value2, guild2_id)
            
            # Verify settings are isolated
            setting_guild1 = await self.db_manager.get_setting(key, guild1_id)
            setting_guild2 = await self.db_manager.get_setting(key, guild2_id)
            
            assert setting_guild1 == value1, f"Expected {value1} in guild 1, got {setting_guild1}"
            assert setting_guild2 == value2, f"Expected {value2} in guild 2, got {setting_guild2}"
            
            print("  ✅ Settings isolation test passed")
            return True
            
        except Exception as e:
            print(f"  ❌ Settings isolation test failed: {e}")
            return False
    
    async def test_table_schema(self) -> bool:
        """Test that all tables have proper per-guild schema."""
        print("\n🧪 Testing database schema...")
        
        try:
            conn = await self.db_manager.get_connection()
            
            # Tables that should have guild_id
            tables_with_guild_id = [
                'user_xp', 'birthdays', 'verifications', 'appeals',
                'daily_checkins', 'roast_log', 'mod_logs', 'level_roles'
            ]
            
            for table in tables_with_guild_id:
                cursor = await conn.execute(f"PRAGMA table_info({table})")
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                assert 'guild_id' in column_names, f"Table {table} missing guild_id column"
                
                # Check unique constraints for per-guild tables
                if table in ['user_xp', 'birthdays', 'daily_checkins']:
                    # For these tables, we expect composite primary keys
                    if table == 'user_xp':
                        cursor = await conn.execute(f"PRAGMA table_info({table})")
                        columns = await cursor.fetchall()
                        # In SQLite, composite PK shows first column as PK=1, second as PK=2, etc.
                        pk_columns = [col[1] for col in columns if col[5] > 0]  # Any PK > 0
                        has_user_id = any(col[1] == 'user_id' and col[5] > 0 for col in columns)
                        has_guild_id = any(col[1] == 'guild_id' and col[5] > 0 for col in columns)
                        assert has_user_id and has_guild_id, f"Table {table} should have composite primary key with user_id and guild_id. Found PK columns: {pk_columns}"
            
            # Users table should NOT have global data columns
            cursor = await conn.execute("PRAGMA table_info(users)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            forbidden_columns = ['xp', 'level', 'birthday']
            for col in forbidden_columns:
                assert col not in column_names, f"Users table should not have global {col} column"
            
            await conn.close()
            print("  ✅ Database schema test passed")
            return True
            
        except Exception as e:
            print(f"  ❌ Database schema test failed: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all tests and return overall result."""
        print("🚀 Starting comprehensive per-guild audit tests...")
        
        tests = [
            self.test_table_schema(),
            self.test_xp_isolation(),
            self.test_birthday_isolation(),
            self.test_user_cleanup(),
            self.test_leaderboard_isolation(),
            self.test_settings_isolation(),
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        passed = 0
        failed = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Test {i+1} crashed: {result}")
                failed += 1
            elif result:
                passed += 1
            else:
                failed += 1
        
        print(f"\n📊 Test Results:")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        return failed == 0


async def main():
    """Run the comprehensive per-guild audit."""
    print("🔍 Comprehensive Per-Guild Implementation Audit")
    print("=" * 50)
    
    tester = PerGuildTester()
    
    try:
        await tester.setup()
        success = await tester.run_all_tests()
        
        if success:
            print("\n🎉 ALL TESTS PASSED! The per-guild implementation is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Please review the implementation.")
        
        return success
        
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)