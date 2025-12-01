"""
Tests for XP calculation logic.
"""

import pytest


class TestXPCalculations:
    """Test XP calculation functions."""

    def test_calculate_level_basic(self):
        """Test basic level calculation."""
        from cogs.xp import calculate_level

        # Test with actual XP values
        assert calculate_level(0) == 1
        assert calculate_level(50) == 1
        assert isinstance(calculate_level(100), int)
        assert calculate_level(100) >= 1

    def test_calculate_level_edge_cases(self):
        """Test edge cases for level calculation."""
        from cogs.xp import calculate_level

        # Test negative XP
        assert calculate_level(-100) == 1

        # Test zero XP
        assert calculate_level(0) == 1

        # Test very high XP returns valid level
        level = calculate_level(10000)
        assert isinstance(level, int)
        assert level >= 1

    def test_xp_helper_functions(self):
        """Test XP helper utility functions."""
        from utils.helpers import xp_helper

        # xp_helper returns a dict, not an object with methods
        result = xp_helper(100)
        assert isinstance(result, dict)

        result = xp_helper(1000)
        assert isinstance(result, dict)


@pytest.mark.asyncio
class TestXPDatabaseOperations:
    """Test XP database operations."""

    async def test_set_user_xp(self):
        """Test setting user XP and level calculation."""
        from database.models import DatabaseManager

        # Mock database connection
        db_manager = DatabaseManager(":memory:")
        await db_manager.initialize()

        # Test setting XP - returns (xp, level)
        new_xp, new_level = await db_manager.set_user_xp(12345, 500)
        assert new_xp == 500
        assert isinstance(new_level, int)
        assert new_level >= 1

        # Test getting XP back
        retrieved_xp = await db_manager.get_user_xp(12345)
        assert retrieved_xp == 500

    async def test_update_user_xp(self):
        """Test updating user XP."""
        from database.models import DatabaseManager

        db_manager = DatabaseManager(":memory:")
        await db_manager.initialize()

        # Update XP (adds to existing)
        new_xp, new_level = await db_manager.update_user_xp(12345, 100)
        assert new_xp == 100
        assert isinstance(new_level, int)

        # Add more XP
        new_xp, new_level = await db_manager.update_user_xp(12345, 50)
        assert new_xp == 150

    async def test_remove_user_xp(self):
        """Test removing user XP."""
        from database.models import DatabaseManager

        db_manager = DatabaseManager(":memory:")
        await db_manager.initialize()

        # Set initial XP
        await db_manager.set_user_xp(12345, 200)

        # Remove some XP
        new_xp, new_level = await db_manager.remove_user_xp(12345, 50)
        assert new_xp == 150
        assert isinstance(new_level, int)


if __name__ == "__main__":
    pytest.main([__file__])
