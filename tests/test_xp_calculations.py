"""
Tests for XP calculation logic.
"""

from unittest.mock import patch

import pytest


class TestXPCalculations:
    """Test XP calculation functions."""

    def test_calculate_level_basic(self):
        """Test basic level calculation."""
        # Test with XP_TABLE mock
        with patch("config.constants.XP_TABLE", [0, 100, 300, 600, 1000]):
            from cogs.xp import calculate_level

            assert calculate_level(0) == 1
            assert calculate_level(50) == 1
            assert calculate_level(100) == 2
            assert calculate_level(200) == 2
            assert calculate_level(300) == 3
            assert calculate_level(500) == 3
            assert calculate_level(1000) == 4
            assert calculate_level(1500) == 4

    def test_calculate_level_edge_cases(self):
        """Test edge cases for level calculation."""
        with patch("config.constants.XP_TABLE", [0, 100, 300]):
            from cogs.xp import calculate_level

            # Test negative XP
            assert calculate_level(-100) == 1

            # Test exact thresholds
            assert calculate_level(0) == 1
            assert calculate_level(100) == 2
            assert calculate_level(300) == 3

            # Test very high XP
            assert calculate_level(10000) == 3

    def test_xp_helper_functions(self):
        """Test XP helper utility functions."""
        from utils.helpers import xp_helper

        # Test XP validation
        assert xp_helper.is_valid_xp_amount(100) is True
        assert xp_helper.is_valid_xp_amount(-1) is False
        assert xp_helper.is_valid_xp_amount(0) is True

        # Test XP formatting
        assert xp_helper.format_xp(1000) == "1,000"
        assert xp_helper.format_xp(1234567) == "1,234,567"
        assert xp_helper.format_xp(0) == "0"


@pytest.mark.asyncio
class TestXPDatabaseOperations:
    """Test XP database operations."""

    async def test_set_user_xp(self):
        """Test setting user XP and level calculation."""
        from database.models import DatabaseManager

        # Mock database connection
        db_manager = DatabaseManager(":memory:")
        await db_manager.initialize()

        # Test setting XP
        new_xp, new_level = await db_manager.set_user_xp(12345, 500)
        assert new_xp == 500
        assert isinstance(new_level, int)
        assert new_level >= 1

        # Test getting XP back
        retrieved_xp = await db_manager.get_user_xp(12345)
        assert retrieved_xp == 500

    async def test_add_user_xp(self):
        """Test adding XP to user."""
        from database.models import DatabaseManager

        db_manager = DatabaseManager(":memory:")
        await db_manager.initialize()

        # Add XP to new user
        new_total = await db_manager.add_user_xp(12345, 100)
        assert new_total == 100

        # Add more XP
        new_total = await db_manager.add_user_xp(12345, 50)
        assert new_total == 150

    async def test_update_user_xp(self):
        """Test updating user XP."""
        from database.models import DatabaseManager

        db_manager = DatabaseManager(":memory:")
        await db_manager.initialize()

        # Update XP (should work even if user doesn't exist)
        await db_manager.update_user_xp(12345, 200)

        # Check result
        xp = await db_manager.get_user_xp(12345)
        assert xp == 200


if __name__ == "__main__":
    pytest.main([__file__])
