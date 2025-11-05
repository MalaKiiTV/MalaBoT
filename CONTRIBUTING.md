# Contributing to MalaBoT

Thank you for your interest in contributing to MalaBoT! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Poetry (recommended) or pip
- Git
- Discord Developer Account (for testing)

### Setting Up

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/MalaBoT.git
   cd MalaBoT
   ```

2. **Set up your development environment**
   ```bash
   # Using Poetry (recommended)
   poetry install
   poetry shell
   
   # Or using pip
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your development configuration
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## 📋 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Follow the existing code style
- Write tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Code Quality

Before submitting, ensure your code meets our quality standards:

```bash
# Format code
poetry run black .

# Lint code
poetry run ruff check --fix .

# Type check
poetry run mypy .

# Run tests
poetry run pytest
```

### 4. Commit Changes

Use clear, conventional commit messages:

```bash
git commit -m "feat: add new command for feature"
git commit -m "fix: resolve issue with database connection"
git commit -m "docs: update README with new information"
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:

- Clear title and description
- Reference any related issues
- Explain your changes
- Include screenshots for UI changes

## 📝 Code Standards

### Style Guidelines

- **Black**: Use for code formatting (configured to 88 characters)
- **Ruff**: Use for linting and import sorting
- **MyPy**: Use for type checking (strict mode enabled)
- **Docstrings**: Use Google-style docstrings

### Type Hints

All functions should have proper type hints:

```python
from typing import Optional, List
import discord

async def process_user_xp(
    user: discord.Member, 
    amount: int
) -> tuple[int, int]:
    """Process user XP and return new total and level."""
    # Implementation
    return new_xp, new_level
```

### Documentation

- Write clear docstrings for all public functions
- Include type hints
- Add examples for complex functions
- Update README for new features

## 🧪 Testing

### Writing Tests

- Use `pytest` for testing
- Place tests in the `tests/` directory
- Test both success and failure cases
- Mock external dependencies (Discord API)

### Test Structure

```python
# tests/test_xp.py
import pytest
from unittest.mock import Mock, AsyncMock
from cogs.xp import XPHelper

def test_calculate_level():
    """Test level calculation logic."""
    assert XPHelper.calculate_level(100) == 2
    assert XPHelper.calculate_level(0) == 1

@pytest.mark.asyncio
async def test_add_user_xp():
    """Test adding XP to a user."""
    # Mock database and test logic
    pass
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=cogs

# Run specific test file
poetry run pytest tests/test_xp.py
```

## 🏗️ Architecture

### Cog Structure

Each cog should follow this pattern:

```python
"""
Cog description and purpose.
Parent slash command: /command
Subcommands: sub1, sub2
"""

import discord
from discord.ext import commands
from typing import Optional

class CogName(commands.Cog):
    """Cog description."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger('cog_name')
    
    @commands.command()
    async def command_name(self, ctx: commands.Context):
        """Command description."""
        pass
```

### Database Patterns

- Use async database operations
- Handle connection errors gracefully
- Use transactions for multiple operations
- Validate input data

### Error Handling

```python
try:
    # Operation that might fail
    result = await some_operation()
except SpecificException as e:
    self.logger.error(f"Operation failed: {e}")
    await ctx.send("An error occurred while processing your request.")
except Exception as e:
    self.logger.error(f"Unexpected error: {e}")
    await ctx.send("An unexpected error occurred.")
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment**: Python version, discord.py version
2. **Steps to Reproduce**: Clear steps to reproduce the issue
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Error Logs**: Full error traceback
6. **Additional Context**: Any other relevant information

## 💡 Feature Requests

We welcome feature requests! Please:

1. **Check existing issues** to avoid duplicates
2. **Provide clear description** of the feature
3. **Explain the use case** and why it's valuable
4. **Consider implementation** if you have ideas
5. **Be realistic** about scope and complexity

## 🔧 Development Tools

### Recommended VS Code Extensions

- Python
- Pylance
- Black Formatter
- Error Lens
- GitLens

### Useful Commands

```bash
# Format code
poetry run black .

# Check imports
poetry run ruff check .

# Type check
poetry run mypy .

# Run tests
poetry run pytest

# Generate requirements
poetry export -f requirements.txt --output requirements.txt
```

## 📚 Resources

- [discord.py Documentation](https://discordpy.readthedocs.io/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Black Code Style](https://black.readthedocs.io/)
- [Ruff Linter](https://beta.ruff.rs/)
- [Pytest Testing](https://docs.pytest.org/)

## 🤝 Community

- Join our Discord server for discussions
- Participate in code reviews
- Help other contributors
- Share your knowledge and experience

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to MalaBoT! 🎉