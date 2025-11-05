"""
Tests for XP calculation logic.
"""
import pytest
from config.constants import XP_TABLE


class TestXPCalculations:
    """Test XP calculation functions."""
    
    def test_xp_table_structure(self):
        """Test that XP_TABLE is properly structured."""
        assert isinstance(XP_TABLE, dict)
        assert 1 in XP_TABLE
        assert XP_TABLE[1] == 0
        assert 2 in XP_TABLE
        assert XP_TABLE[2] == 100


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
        
        # Update XP (should work even if user doesn't exist)
        new_xp, new_level = await db_manager.update_user_xp(12345, 200)
        assert new_xp == 200
        assert new_level >= 1
        
        # Check result
        xp = await db_manager.get_user_xp(12345)
        assert xp == 200
        
        # Add more XP
        new_xp, new_level = await db_manager.update_user_xp(12345, 50)
        assert new_xp == 250
        
    async def test_remove_user_xp(self):
        """Test removing XP from user."""
        from database.models import DatabaseManager
        
        db_manager = DatabaseManager(":memory:")
        await db_manager.initialize()
        
        # Set initial XP
        await db_manager.set_user_xp(12345, 500)
        
        # Remove XP
        new_xp, new_level = await db_manager.remove_user_xp(12345, 100)
        assert new_xp == 400
        
    async def test_get_user_rank(self):
        """Test getting user rank."""
        from database.models import DatabaseManager
        
        db_manager = DatabaseManager(":memory:")
        await db_manager.initialize()
        
        # Create multiple users with different XP
        await db_manager.set_user_xp(1, 500)
        await db_manager.set_user_xp(2, 300)
        await db_manager.set_user_xp(3, 700)
        
        # Check ranks
        rank1 = await db_manager.get_user_rank(1, 0)
        rank2 = await db_manager.get_user_rank(2, 0)
        rank3 = await db_manager.get_user_rank(3, 0)
        
        assert rank3 == 1  # Highest XP
        assert rank1 == 2  # Second highest
        assert rank2 == 3  # Third highest


if __name__ == "__main__":
    pytest.main([__file__])