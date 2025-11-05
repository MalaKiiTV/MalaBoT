"""
Pytest configuration and fixtures.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_bot():
    """Create a mock Discord bot."""
    bot = Mock()
    bot.user = Mock()
    bot.user.id = 123456789
    bot.db_manager = AsyncMock()
    return bot


@pytest.fixture
def mock_guild():
    """Create a mock Discord guild."""
    guild = Mock()
    guild.id = 987654321
    guild.name = "Test Guild"
    guild.owner_id = 123456789
    return guild


@pytest.fixture
def mock_member():
    """Create a mock Discord member."""
    member = Mock()
    member.id = 555555555
    member.name = "TestUser"
    member.mention = f"<@{member.id}>"
    return member


@pytest.fixture
def mock_interaction(mock_bot, mock_guild, mock_member):
    """Create a mock Discord interaction."""
    interaction = Mock()
    interaction.client = mock_bot
    interaction.guild = mock_guild
    interaction.user = mock_member
    interaction.response = AsyncMock()
    interaction.followup = AsyncMock()
    return interaction