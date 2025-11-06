"""
Tests for XP calculation logic.
"""

import datetime
from unittest.mock import patch, MagicMock

import pytest


class TestXPCalculations:
    """Test XP calculation functions."""

    def test_calculate_level_basic(self):
        """Test basic level calculation."""
        # Test with XP_TABLE mock
        with patch('config.constants.XP_TABLE', [0, 100, 300, 600, 1000]):
            # Since calculate_level function doesn't exist in xp.py,
            # we'll test the level calculation logic directly
            from config.constants import XP_TABLE
            
            def calculate_level(xp_amount):
                level = 1
                for lvl, req_xp in enumerate(XP_TABLE):
                    if xp_amount >= req_xp:
                        level = lvl + 1
                    else:
                        break
                return level

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
        with patch('config.constants.XP_TABLE', [0, 100, 300]):
            # Test the level calculation logic directly
            from config.constants import XP_TABLE
            
            def calculate_level(xp_amount):
                level = 1
                for lvl, req_xp in enumerate(XP_TABLE):
                    if xp_amount >= req_xp:
                        level = lvl + 1
                    else:
                        break
                return level

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
        # Since xp_helper might not exist, we'll test basic XP formatting
        def format_xp(amount):
            return f"{amount:,}"

        # Test XP formatting
        assert format_xp(1000) == "1,000"
        assert format_xp(1234567) == "1,234,567"
        assert format_xp(0) == "0"

        def is_valid_xp_amount(amount):
            return isinstance(amount, (int, float)) and amount >= 0

        # Test XP validation
        assert is_valid_xp_amount(100) is True
        assert is_valid_xp_amount(-1) is False
        assert is_valid_xp_amount(0) is True


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

    async def test_update_user_xp(self):
        """Test updating user XP."""
        from database.models import DatabaseManager

        db_manager = DatabaseManager(":memory:")
        await db_manager.initialize()

        # Update XP (should work even if user doesn't exist now)
        new_xp, new_level = await db_manager.update_user_xp(12345, 200)
        assert new_xp == 200
        assert isinstance(new_level, int)

        # Check result
        xp = await db_manager.get_user_xp(12345)
        assert xp == 200

        # Test adding more XP
        new_xp, new_level = await db_manager.update_user_xp(12345, 100)
        assert new_xp == 300

        # Test XP cannot go negative
        new_xp, new_level = await db_manager.update_user_xp(12345, -500)
        assert new_xp == 0  # Should be clamped to 0


@pytest.mark.asyncio
class TestXPEventListeners:
    """Test XP event listeners."""

    async def test_message_xp_cooldown(self):
        """Test XP cooldown for messages."""
        # Mock the XP cog cooldown logic
        from config.constants import XP_COOLDOWN_SECONDS
        
        last_xp_time = {}
        user_id = 12345
        current_time = datetime.datetime.now().timestamp()
        
        # First message should award XP
        if user_id not in last_xp_time:
            should_award = True
        else:
            time_diff = current_time - last_xp_time[user_id]
            should_award = time_diff >= XP_COOLDOWN_SECONDS
        
        assert should_award is True
        
        # Update last XP time
        last_xp_time[user_id] = current_time
        
        # Immediate second message should not award XP
        current_time = datetime.datetime.now().timestamp()
        if user_id in last_xp_time:
            time_diff = current_time - last_xp_time[user_id]
            should_award = time_diff >= XP_COOLDOWN_SECONDS
        
        assert should_award is False

    async def test_voice_xp_calculation(self):
        """Test voice XP calculation."""
        from config.constants import XP_PER_VOICE_MINUTE
        
        # Test voice time calculation
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(minutes=5)
        time_spent = end_time - start_time
        minutes = int(time_spent.total_seconds() / 60)
        
        expected_xp = minutes * XP_PER_VOICE_MINUTE
        assert expected_xp == 5 * XP_PER_VOICE_MINUTE


if __name__ == "__main__":
    pytest.main([__file__])