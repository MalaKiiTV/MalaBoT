"""
Comprehensive test suite for per-server data implementation validation.
This script tests all aspects of the per-server data architecture to ensure:
1. Data isolation between servers
2. Proper user leave cleanup
3. Correct database operations
4. Data consistency

To run this test:
1. Install dependencies: pip install -r requirements.txt
2. Run: python test_per_server_implementation.py
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.models import DatabaseManager
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("❌ Dependencies not available. Install with: pip install -r requirements.txt")


class PerServerDataValidator:
    """Comprehensive validator for per-server data implementation."""

    def __init__(self):
        self.test_db_path = "test_per_server_validation.db"
        self.db_manager = None
        self.test_results = []
        
    async def setup(self):
        """Set up test environment."""
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Required dependencies not installed")
            
        self.db_manager = DatabaseManager(self.test_db_path)
        await self.db_manager.initialize()
        
    async def cleanup(self):
        """Clean up test environment."""
        if self.db_manager:
            await self.db_manager.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def log_test_result(self, test_name: str, passed: bool, message: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")

    async def test_xp_isolation(self):
        """Test XP data isolation between servers."""
        try:
            user_id = 12345
            guild1_id = 1001
            guild2_id = 1002
            
            # Set different XP for same user in different guilds
            await self.db_manager.set_user_xp(user_id, 100, guild1_id)
            await self.db_manager.set_user_xp(user_id, 200, guild2_id)
            
            # Verify isolation
            xp_guild1 = await self.db_manager.get_user_xp(user_id, guild1_id)
            xp_guild2 = await self.db_manager.get_user_xp(user_id, guild2_id)
            
            passed = xp_guild1 == 100 and xp_guild2 == 200
            message = f"Guild1: {xp_guild1} XP, Guild2: {xp_guild2} XP"
            
            self.log_test_result("XP Data Isolation", passed, message)
            
        except Exception as e:
            self.log_test_result("XP Data Isolation", False, f"Error: {e}")

    async def test_birthday_isolation(self):
        """Test birthday data isolation between servers."""
        try:
            user_id = 12346
            guild1_id = 1001
            guild2_id = 1002
            
            # Set different birthdays
            await self.db_manager.set_user_birthday(user_id, "01-15", guild1_id)
            await self.db_manager.set_user_birthday(user_id, "06-20", guild2_id)
            
            # Verify isolation
            bday_guild1 = await self.db_manager.get_user_birthday(user_id, guild1_id)
            bday_guild2 = await self.db_manager.get_user_birthday(user_id, guild2_id)
            
            passed = (bday_guild1 is not None and bday_guild2 is not None and
                     bday_guild1[2] == "01-15" and bday_guild2[2] == "06-20")
            message = f"Guild1: {bday_guild1[2] if bday_guild1 else 'None'}, Guild2: {bday_guild2[2] if bday_guild2 else 'None'}"
            
            self.log_test_result("Birthday Data Isolation", passed, message)
            
        except Exception as e:
            self.log_test_result("Birthday Data Isolation", False, f"Error: {e}")

    async def test_user_leave_cleanup(self):
        """Test data cleanup when user leaves a server."""
        try:
            user_id = 12347
            guild1_id = 1001
            guild2_id = 1002
            
            # Set up data in both guilds
            await self.db_manager.set_user_xp(user_id, 150, guild1_id)
            await self.db_manager.set_user_xp(user_id, 250, guild2_id)
            await self.db_manager.set_user_birthday(user_id, "03-10", guild1_id)
            await self.db_manager.set_user_birthday(user_id, "08-25", guild2_id)
            
            # Clean up data for guild1 only
            await self.db_manager.cleanup_user_data(user_id, guild1_id)
            
            # Verify cleanup
            xp_guild1_after = await self.db_manager.get_user_xp(user_id, guild1_id)
            xp_guild2_after = await self.db_manager.get_user_xp(user_id, guild2_id)
            bday_guild1_after = await self.db_manager.get_user_birthday(user_id, guild1_id)
            bday_guild2_after = await self.db_manager.get_user_birthday(user_id, guild2_id)
            
            passed = (xp_guild1_after == 0 and xp_guild2_after == 250 and
                     bday_guild1_after is None and bday_guild2_after is not None)
            
            message = f"Guild1 cleaned up correctly, Guild2 data preserved"
            self.log_test_result("User Leave Data Cleanup", passed, message)
            
        except Exception as e:
            self.log_test_result("User Leave Data Cleanup", False, f"Error: {e}")

    async def test_rank_calculation(self):
        """Test per-server rank calculation."""
        try:
            guild_id = 1001
            users = [(11111, 500), (22222, 300), (33333, 100)]
            
            # Set XP for users
            for user_id, xp in users:
                await self.db_manager.set_user_xp(user_id, xp, guild_id)
            
            # Check ranks
            rank_11111 = await self.db_manager.get_user_rank(11111, guild_id)
            rank_22222 = await self.db_manager.get_user_rank(22222, guild_id)
            rank_33333 = await self.db_manager.get_user_rank(33333, guild_id)
            
            passed = rank_11111 == 1 and rank_22222 == 2 and rank_33333 == 3
            message = f"User ranks: {rank_11111}, {rank_22222}, {rank_33333}"
            
            self.log_test_result("Per-Server Rank Calculation", passed, message)
            
        except Exception as e:
            self.log_test_result("Per-Server Rank Calculation", False, f"Error: {e}")

    async def test_level_progression(self):
        """Test per-server level progression."""
        try:
            user_id = 12348
            guild1_id = 1001
            guild2_id = 1002
            
            # Set same XP in different guilds with different progression types
            await self.db_manager.set_setting("xp_progression_type", "basic", guild1_id)
            await self.db_manager.set_setting("xp_progression_type", "custom", guild2_id)
            
            await self.db_manager.set_user_xp(user_id, 150, guild1_id)
            await self.db_manager.set_user_xp(user_id, 150, guild2_id)
            
            level_guild1 = await self.db_manager.get_user_level(user_id, guild1_id)
            level_guild2 = await self.db_manager.get_user_level(user_id, guild2_id)
            
            passed = level_guild1 >= 1 and level_guild2 >= 1
            message = f"Level progression working in both guilds"
            
            self.log_test_result("Per-Server Level Progression", passed, message)
            
        except Exception as e:
            self.log_test_result("Per-Server Level Progression", False, f"Error: {e}")

    async def check_database_schema(self):
        """Check if database schema includes required guild_id columns."""
        try:
            conn = await self.db_manager.get_connection()
            
            # Check users table for guild_id
            cursor = await conn.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in await cursor.fetchall()]
            users_has_guild_id = 'guild_id' in columns
            
            # Check birthdays table for guild_id
            cursor = await conn.execute("PRAGMA table_info(birthdays)")
            columns = [row[1] for row in await cursor.fetchall()]
            birthdays_has_guild_id = 'guild_id' in columns
            
            # Check daily_checkins table for guild_id
            cursor = await conn.execute("PRAGMA table_info(daily_checkins)")
            columns = [row[1] for row in await cursor.fetchall()]
            checkins_has_guild_id = 'guild_id' in columns
            
            passed = users_has_guild_id and birthdays_has_guild_id and checkins_has_guild_id
            message = f"Users: {users_has_guild_id}, Birthdays: {birthdays_has_guild_id}, Checkins: {checkins_has_guild_id}"
            
            self.log_test_result("Database Schema Validation", passed, message)
            
        except Exception as e:
            self.log_test_result("Database Schema Validation", False, f"Error: {e}")

    async def check_required_methods(self):
        """Check if all required per-server methods exist."""
        try:
            required_methods = [
                'get_user_xp', 'set_user_xp', 'update_user_xp',
                'get_user_level', 'get_user_rank', 'cleanup_user_data',
                'set_user_birthday', 'get_user_birthday', 'remove_user_birthday',
                'get_all_birthdays', 'get_unannounced_birthdays', 'mark_birthday_announced',
                'get_user_checkin', 'update_user_checkin', 'remove_user_checkin'
            ]
            
            missing_methods = []
            for method in required_methods:
                if not hasattr(self.db_manager, method):
                    missing_methods.append(method)
            
            passed = len(missing_methods) == 0
            message = f"Missing methods: {missing_methods}" if missing_methods else "All required methods present"
            
            self.log_test_result("Required Methods Check", passed, message)
            
        except Exception as e:
            self.log_test_result("Required Methods Check", False, f"Error: {e}")

    async def run_comprehensive_validation(self):
        """Run all validation tests."""
        print("🔍 Per-Server Data Implementation Validator")
        print("=" * 50)
        
        if not DEPENDENCIES_AVAILABLE:
            print("❌ Cannot run validation - dependencies not installed")
            print("Please install with: pip install -r requirements.txt")
            return False
        
        try:
            await self.setup()
            
            print("Running comprehensive validation tests...\n")
            
            # Schema and method checks
            await self.check_database_schema()
            await self.check_required_methods()
            
            # Functional tests
            await self.test_xp_isolation()
            await self.test_birthday_isolation()
            await self.test_user_leave_cleanup()
            await self.test_rank_calculation()
            await self.test_level_progression()
            
            # Results summary
            print("\n" + "=" * 50)
            print("📊 VALIDATION RESULTS")
            print("=" * 50)
            
            passed_count = sum(1 for result in self.test_results if result['passed'])
            total_count = len(self.test_results)
            
            for result in self.test_results:
                status = "✅" if result['passed'] else "❌"
                print(f"{status} {result['test']}")
                if not result['passed'] and result['message']:
                    print(f"   {result['message']}")
            
            print(f"\nSummary: {passed_count}/{total_count} tests passed")
            
            if passed_count == total_count:
                print("\n🎉 ALL TESTS PASSED!")
                print("✅ Per-server data implementation is working correctly")
                print("✅ Data is properly isolated between servers")
                print("✅ User leave cleanup is working")
                print("✅ All database operations are server-aware")
                return True
            else:
                print(f"\n⚠️  {total_count - passed_count} test(s) failed")
                print("❌ Please review the implementation and fix the issues")
                return False
                
        except Exception as e:
            print(f"\n❌ Validation failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            await self.cleanup()


async def main():
    """Main validation runner."""
    validator = PerServerDataValidator()
    success = await validator.run_comprehensive_validation()
    
    if success:
        print("\n🚀 Ready for deployment!")
    else:
        print("\n🔧 Implementation needs fixes before deployment")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)