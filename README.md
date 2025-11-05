# 🤖 MalaBoT

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-black.svg)](https://github.com/psf/black)

A powerful, multifunctional Discord bot built with Python and discord.py. MalaBoT provides comprehensive server management features including XP systems, user verification, moderation tools, and more.

## ✨ Features

### 🎮 XP & Leveling System
- **Rank Command**: Check your or another user's rank and XP
- **Leaderboard**: Server-wide XP leaderboard
- **Daily Checkins**: Claim daily XP bonuses
- **Admin Tools**: Add, remove, set, and reset user XP

### 🔐 User Verification
- **Manual Verification**: Users can submit verification requests
- **Mod Review**: Moderators can approve/deny verification requests
- **Custom Roles**: Assign verified and cheater roles
- **Screenshot Support**: Upload verification screenshots

### 🛡️ Moderation
- **Appeal System**: Users can appeal moderation actions
- **Mod Actions**: Full suite of moderation commands
- **Logging**: Comprehensive audit logging
- **Role Management**: Dynamic role assignment

### 🎉 Community Features
- **Birthday System**: Automatic birthday celebrations
- **Welcome Messages**: Customizable new member greetings
- **Goodbye Messages**: Customizable member departure messages
- **Online Status**: Configurable online messages

### ⚙️ Server Configuration
- **Interactive Setup**: Easy-to-use setup commands
- **Guild-Specific Settings**: Per-server configuration
- **Role Management**: Configure mod, join, and special roles
- **Channel Management**: Set up dedicated channels for various features

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Discord Bot Token
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/MalaKiiTV/MalaBoT.git
   cd MalaBoT
   ```

2. **Install dependencies using Poetry**
   ```bash
   # Install Poetry (if not already installed)
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Install dependencies
   poetry install
   ```

3. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your configuration
   nano .env
   ```

4. **Run the bot**
   ```bash
   poetry run python bot.py
   ```

### Alternative Installation (pip)

If you prefer not to use Poetry:

```bash
# Clone repository
git clone https://github.com/MalaKiiTV/MalaBoT.git
cd MalaBoT

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run bot
python bot.py
```

## ⚙️ Configuration

Create a `.env` file based on `.env.example`:

```env
# -- Core Bot Settings --
DISCORD_TOKEN=your_discord_bot_token_here
BOT_PREFIX=!
OWNER_IDS=your_user_id_here,another_user_id_here
DEBUG_GUILDS=your_test_guild_id_here

# -- Database --
DATABASE_URL=sqlite:///data/malabot.db

# -- Optional Logging --
LOG_LEVEL=INFO
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DISCORD_TOKEN` | Your Discord bot token | ✅ |
| `BOT_PREFIX` | Command prefix for the bot | ❌ (defaults: !) |
| `OWNER_IDS` | Comma-separated list of owner Discord IDs | ✅ |
| `DEBUG_GUILDS` | Comma-separated list of test guild IDs | ❌ |
| `DATABASE_URL` | Database connection URL | ❌ (defaults: sqlite) |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | ❌ (defaults: INFO) |

## 📋 Commands

### XP Commands
- `/xp rank` - Check your or another user's rank
- `/xp leaderboard` - View server XP leaderboard
- `/xp checkin` - Claim daily XP bonus
- `/xp add` - Add XP to a user (Admin)
- `/xp remove` - Remove XP from a user (Admin)
- `/xp set` - Set user XP to specific amount (Admin)
- `/xp reset` - Reset user XP to 0 (Admin)

### Server Commands
- `/setup` - Configure bot settings (Server Owner)
- `/verify submit` - Submit verification request
- `/verify review` - Review verification requests (Mod)
- `/appeal` - Submit moderation appeal

### Utility Commands
- Various utility and moderation commands
- Birthday celebration commands
- Welcome/goodbye message configuration

## 🛠️ Development

### Setting Up Development Environment

1. **Clone and install dependencies**
   ```bash
   git clone https://github.com/MalaKiiTV/MalaBoT.git
   cd MalaBoT
   poetry install
   ```

2. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

3. **Run code formatting and linting**
   ```bash
   poetry run black .
   poetry run ruff check --fix .
   poetry run mypy .
   ```

### Running Tests

```bash
poetry run pytest
```

### Project Structure

```
MalaBoT/
├── bot.py                 # Main bot entry point
├── cogs/                  # Bot command modules
│   ├── xp.py             # XP and leveling system
│   ├── verify.py         # User verification
│   ├── moderation.py     # Moderation commands
│   ├── birthdays.py      # Birthday system
│   └── ...
├── database/             # Database models and management
├── utils/                # Helper functions and utilities
├── config/               # Configuration files
├── tests/                # Test files
├── pyproject.toml        # Poetry dependency management
├── .env.example          # Environment variables template
└── README.md             # This file
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Standards

- Use **Black** for code formatting
- Use **Ruff** for linting
- Use **MyPy** for type checking
- Write tests for new features
- Follow the existing code style
- Use meaningful commit messages

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

If you need help or have questions:

- Create an [Issue](https://github.com/MalaKiiTV/MalaBoT/issues)
- Join our [Discord Server](https://discord.gg/your-invite)
- Check the [Documentation](https://malabot.readthedocs.io)

## 🙏 Acknowledgments

- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [APScheduler](https://github.com/agronholm/apscheduler) - Task scheduling
- All contributors and users who make this bot better!

---

**MalaBoT** - Making Discord servers better, one feature at a time! 🚀