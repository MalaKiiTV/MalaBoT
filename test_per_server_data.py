"""
Test script to validate per-server data implementation in MalaBoT.
This script tests database operations to ensure proper data isolation between servers.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import DatabaseManager


class PerServerDataTester:
    """Test suite for per-server data functionality."""

    def __init__(self):
        # Use a test database
        self.test_db_path = "test_per_server.db"
        self.db_manager = DatabaseManager(self.test_db_path)
        
    async def setup(self):
        """Set up test database."""
        print("🔧 Setting up test database...")
        await self.db_manager.initialize()
        print("✅ Test database initialized")
        
    async def cleanup(self):
        """Clean up test database."""
        print("🧹 Cleaning up test database...")
        await self.db_manager.close()
        # Remove test database file
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        print("✅ Test database cleaned up")

    async def test_user_xp_isolation(self):
        """Test that XP data is properly isolated between servers."""
        print("\n🧪 Testing XP data isolation...")
        
        user_id = 12345
        guild1_id = 1001
        guild2_id = 1002
        
        # Set XP for same user in different guilds
        await self.db_manager.set_user_xp(user_id, 100, guild1_id)
        await self.db_manager.set_user_xp(user_id, 200, guild2_id)
        
        # Verify isolation
        xp_guild1 = await self.db_manager.get_user_xp(user_id, guild1_id)
        xp_guild2 = await self.db_manager.get_user_xp(user_id, guild2_id)
        
        assert xp_guild1 == 100, f"Expected 100 XP in guild1, got {xp_guild1}"
        assert xp_guild2 == 200, f"Expected 200 XP in guild2, got {xp_guild2}"
        
        print("✅ XP data isolation test passed")

    async def test_birthday_isolation(self):
        """Test that birthday data is properly isolated between servers."""
        print("\n🧪 Testing birthday data isolation...")
        
        user_id = 12346
        guild1_id = 1001
        guild2_id = 1002
        
        # Set different birthdays for same user in different guilds
        await self.db_manager.set_user_birthday(user_id, "01-15", guild1_id)
        await self.db_manager.set_user_birthday(user_id, "06-20", guild2_id)
        
        # Verify isolation
        birthday_guild1 = await self.db_manager.get_user_birthday(user_id, guild1_id)
        birthday_guild2 = await self.db_manager.get_user_birthday(user_id, guild2_id)
        
        assert birthday_guild1 is not None, "Birthday should exist in guild1"
        assert birthday_guild2 is not None, "Birthday should exist in guild2"
        assert birthday_guild1[2] == "01-15", f"Expected 01-15 in guild1, got {birthday_guild1[2]}"
        assert birthday_guild2[2] == "06-20", f"Expected 06-20 in guild2, got {birthday_guild2[2]}"
        
        print("✅ Birthday data isolation test passed")

    async def test_checkin_isolation(self):
        """Test that daily checkin data is properly isolated between servers."""
        print("\n🧪 Testing daily checkin data isolation...")
        
        user_id = 12347
        guild1_id = 1001
        guild2_id = 1002
        
        # Set different checkin data for same user in different guilds
        await self.db_manager.update_user_checkin(user_id, guild1_id, "2024-01-15", 5)
        await self.db_manager.update_user_checkin(user_id, guild2_id, "2024-01-16", 10)
        
        # Verify isolation
        checkin_guild1 = await self.db_manager.get_user_checkin(user_id, guild1_id)
        checkin_guild2 = await self.db_manager.get_user_checkin(user_id, guild2_id)
        
        assert checkin_guild1 is not None, "Checkin data should exist in guild1"
        assert checkin_guild2 is not None, "Checkin data should exist in guild2"
        assert checkin_guild1[2] == "2024-01-15", f"Expected 2024-01-15 in guild1, got {checkin_guild1[2]}"
        assert checkin_guild1[3] == 5, f"Expected streak 5 in guild1, got {checkin_guild1[3]}"
        assert checkin_guild2[2] == "2024-01-16", f"Expected 2024-01-16 in guild2, got {checkin_guild2[2]}"
        assert checkin_guild2[3] == 10, f"Expected streak 10 in guild2, got {checkin_guild2[3]}"
        
        print("✅ Daily checkin data isolation test passed")

    async def test_user_rank_calculation(self):
        """Test that user ranks are calculated per-server."""
        print("\n🧪 Testing user rank calculation per-server...")
        
        # Create test users with different XP in each guild
        test_users = [
            (11111, 500),  # Highest in guild1
            (22222, 300),  # Middle in guild1, highest in guild2
            (33333, 100),  # Lowest in guild1, middle in guild2
            (44444, 50),   # Not in guild1, lowest in guild2
        ]
        
        guild1_id = 1001
        guild2_id = 1002
        
        # Set XP for guild1 (users 1-3)
        for user_id, xp in test_users[:3]:
            await self.db_manager.set_user_xp(user_id, xp, guild1_id)
        
        # Set XP for guild2 (users 2-4)
        for user_id, xp in test_users[1:]:
            await self.db_manager.set_user_xp(user_id, xp, guild2_id)
        
        # Test ranks in guild1
        rank_11111_guild1 = await self.db_manager.get_user_rank(11111, guild1_id)
        rank_22222_guild1 = await self.db_manager.get_user_rank(22222, guild1_id)
        rank_33333_guild1 = await self.db_manager.get_user_rank(33333, guild1_id)
        
        assert rank_11111_guild1 == 1, f"User 11111 should be rank 1 in guild1, got {rank_11111_guild1}"
        assert rank_22222_guild1 == 2, f"User 22222 should be rank 2 in guild1, got {rank_22222_guild1}"
        assert rank_33333_guild1 == 3, f"User 33333 should be rank 3 in guild1, got {rank_33333_guild1}"
        
        # Test ranks in guild2
        rank_22222_guild2 = await self.db_manager.get_user_rank(22222, guild2_id)
        rank_33333_guild2 = await self.db_manager.get_user_rank(33333, guild2_id)
        rank_44444_guild2 = await self.db_manager.get_user_rank(44444, guild2_id)
        
        assert rank_22222_guild2 == 1, f"User 22222 should be rank 1 in guild2, got {rank_22222_guild2}"
        assert rank_33333_guild2 == 2, f"User 33333 should be rank 2 in guild2, got {rank_33333_guild2}"
        assert rank_44444_guild2 == 3, f"User 44444 should be rank 3 in guild2, got {rank_44444_guild2}"
        
        print("✅ User rank calculation test passed")

    async def test_data_cleanup_on_leave(self):
        """Test that user data is properly cleaned up when they leave a server."""
        print("\n🧪 Testing data cleanup on user leave...")
        
        user_id = 12348
        guild1_id = 1001
        guild2_id = 1002
        
        # Set up data in both guilds
        await self.db_manager.set_user_xp(user_id, 150, guild1_id)
        await self.db_manager.set_user_xp(user_id, 250, guild2_id)
        await self.db_manager.set_user_birthday(user_id, "03-10", guild1_id)
        await self.db_manager.set_user_birthday(user_id, "08-25", guild2_id)
        await self.db_manager.update_user_checkin(user_id, guild1_id, "2024-03-10", 3)
        await self.db_manager.update_user_checkin(user_id, guild2_id, "2024-03-11", 7)
        
        # Verify data exists in both guilds
        assert await self.db_manager.get_user_xp(user_id, guild1_id) == 150
        assert await self.db_manager.get_user_xp(user_id, guild2_id) == 250
        assert await self.db_manager.get_user_birthday(user_id, guild1_id) is not None
        assert await self.db_manager.get_user_birthday(user_id, guild2_id) is not None
        assert await self.db_manager.get_user_checkin(user_id, guild1_id) is not None
        assert await self.db_manager.get_user_checkin(user_id, guild2_id) is not None
        
        # Simulate user leaving guild1
        await self.db_manager.cleanup_user_data(user_id, guild1_id)
        
        # Verify data is removed from guild1 but not guild2
        assert await self.db_manager.get_user_xp(user_id, guild1_id) == 0, "XP should be 0 after cleanup in guild1"
        assert await self.db_manager.get_user_xp(user_id, guild2_id) == 250, "XP should still exist in guild2"
        assert await self.db_manager.get_user_birthday(user_id, guild1_id) is None, "Birthday should be removed from guild1"
        assert await self.db_manager.get_user_birthday(user_id, guild2_id) is not None, "Birthday should still exist in guild2"
        assert await self.db_manager.get_user_checkin(user_id, guild1_id) is None, "Checkin should be removed from guild1"
        assert await self.db_manager.get_user_checkin(user_id, guild2_id) is not None, "Checkin should still exist in guild2"
        
        print("✅ Data cleanup test passed")

    async def test_birthday_announcements_isolation(self):
        """Test that birthday announcements are handled per-server."""
        print("\n🧪 Testing birthday announcements isolation...")
        
        user_id = 12349
        guild1_id = 1001
        guild2_id = 1002
        current_year = 2024
        
        # Set birthday for today in both guilds
        today = datetime.now().strftime("%m-%d")
        await self.db_manager.set_user_birthday(user_id, today, guild1_id)
        await self.db_manager.set_user_birthday(user_id, today, guild2_id)
        
        # Check for unannounced birthdays in each guild
        unannounced_guild1 = await self.db_manager.get_unannounced_birthdays(guild1_id, current_year)
        unannounced_guild2 = await self.db_manager.get_unannounced_birthdays(guild2_id, current_year)
        
        assert len(unannounced_guild1) == 1, f"Should have 1 unannounced birthday in guild1, got {len(unannounced_guild1)}"
        assert len(unannounced_guild2) == 1, f"Should have 1 unannounced birthday in guild2, got {len(unannounced_guild2)}"
        assert unannounced_guild1[0][0] == user_id, f"User {user_id} should be in unannounced list for guild1"
        assert unannounced_guild2[0][0] == user_id, f"User {user_id} should be in unannounced list for guild2"
        
        # Mark as announced in guild1 only
        await self.db_manager.mark_birthday_announced(user_id, guild1_id, current_year)
        
        # Check again
        unannounced_guild1_after = await self.db_manager.get_unannounced_birthdays(guild1_id, current_year)
        unannounced_guild2_after = await self.db_manager.get_unannounced_birthdays(guild2_id, current_year)
        
        assert len(unannounced_guild1_after) == 0, f"Should have 0 unannounced birthdays in guild1 after announcement, got {len(unannounced_guild1_after)}"
        assert len(unannounced_guild2_after) == 1, f"Should still have 1 unannounced birthday in guild2, got {len(unannounced_guild2_after)}"
        
        print("✅ Birthday announcements isolation test passed")

    async def run_all_tests(self):
        """Run all per-server data tests."""
        print("🚀 Starting per-server data implementation tests...")
        print("=" * 50)
        
        try:
            await self.setup()
            
            # Run all tests
            await self.test_user_xp_isolation()
            await self.test_birthday_isolation()
            await self.test_checkin_isolation()
            await self.test_user_rank_calculation()
            await self.test_data_cleanup_on_leave()
            await self.test_birthday_announcements_isolation()
            
            print("\n" + "=" * 50)
            print("🎉 All tests passed! Per-server data implementation is working correctly.")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            await self.cleanup()


async def main():
    """Main test runner."""
    tester = PerServerDataTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())