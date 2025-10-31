# Integration Guide - Production-Ready System

## Overview

This guide shows you how to integrate the new production-ready systems into your bot.

## What We've Built

1. **BackupManager** - Automatic database backups
2. **SafeDatabase** - Verified database operations
3. **HealthChecker** - System health monitoring
4. **EnhancedLogger** - Comprehensive logging
5. **StartupManager** - Safe bot initialization

## Integration Steps

### Step 1: Update bot.py

Add this to the top of `bot.py`:

```python
from utils.startup_manager import initialize_bot
from utils.backup_manager import BackupManager
from utils.enhanced_logger import setup_logging, get_logger
from discord.ext import tasks

# Setup logging first
setup_logging()
logger = get_logger('bot')
```

Replace the `on_ready` event with:

```python
@bot.event
async def on_ready():
    """Bot ready event with startup verification"""
    
    # Run startup sequence
    success = await initialize_bot(bot)
    
    if not success:
        logger.error("❌ Startup verification failed - check logs")
        # Don't exit, but log the issue
    
    # Start background tasks
    if not hasattr(bot, 'backup_task_started'):
        daily_backup.start()
        bot.backup_task_started = True
    
    logger.info(f"✅ {bot.user} is ready!")
    logger.info(f"Connected to {len(bot.guilds)} guilds")
    
    # Print startup report
    if hasattr(bot, 'startup_manager'):
        print(bot.startup_manager.get_startup_report())

@tasks.loop(hours=24)
async def daily_backup():
    """Create daily backup"""
    logger.info("Creating daily backup...")
    backup_manager = BackupManager()
    backup_manager.auto_backup_if_needed()

@daily_backup.before_loop
async def before_daily_backup():
    await bot.wait_until_ready()
```

### Step 2: Update role_connections.py

Replace the database calls with SafeDatabase:

```python
from utils.safe_database import RoleConnectionSafeDB
from utils.enhanced_logger import get_logger

logger = get_logger('role_connections')

class RoleConnectionManager:
    def __init__(self, bot, db_manager):
        self.bot = bot
        self.db = db_manager
        self.safe_db = RoleConnectionSafeDB(db_manager)  # NEW
        self.connections_cache = {}
        self.protected_roles_cache = {}
    
    async def save_connections(self, guild_id: int):
        """Save connections with verification"""
        connections = self.connections_cache.get(guild_id, [])
        success = await self.safe_db.save_connections(guild_id, connections)
        
        if not success:
            logger.error(f"Failed to save connections for guild {guild_id}")
        
        return success
    
    async def load_connections(self, guild_id: int):
        """Load connections with error recovery"""
        data = await self.safe_db.load_connections(guild_id)
        
        self.connections_cache[guild_id] = [
            RoleConnection(
                connection_id=conn["id"],
                guild_id=guild_id,
                target_role_id=conn["target_role_id"],
                action=conn["action"],
                conditions=conn["conditions"],
                logic=conn.get("logic", "AND"),
                enabled=conn.get("enabled", True)
            )
            for conn in data
        ]
```

### Step 3: Add Backup Commands

Add to `cogs/owner.py` or create new `cogs/admin.py`:

```python
from discord.ext import commands
from discord import app_commands
from utils.backup_manager import BackupManager, list_backups
from utils.enhanced_logger import get_logger

logger = get_logger('admin')

class Admin(commands.Cog):
    """Admin commands for bot management"""
    
    def __init__(self, bot):
        self.bot = bot
        self.backup_manager = BackupManager()
    
    @app_commands.command(name="backup", description="Create manual database backup")
    @app_commands.checks.has_permissions(administrator=True)
    async def backup(self, interaction: discord.Interaction):
        """Create manual backup"""
        await interaction.response.defer(ephemeral=True)
        
        backup_path = self.backup_manager.create_backup("manual")
        
        if backup_path:
            await interaction.followup.send(
                f"✅ Backup created: `{backup_path}`",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                "❌ Backup failed - check logs",
                ephemeral=True
            )
    
    @app_commands.command(name="listbackups", description="List all backups")
    @app_commands.checks.has_permissions(administrator=True)
    async def list_backups_cmd(self, interaction: discord.Interaction):
        """List all backups"""
        await interaction.response.defer(ephemeral=True)
        
        backups = list_backups()
        
        if not backups:
            await interaction.followup.send("No backups found", ephemeral=True)
            return
        
        lines = ["📦 Available Backups:\n"]
        for backup in backups[:10]:  # Show last 10
            size_mb = backup['size'] / 1024 / 1024
            lines.append(
                f"• {backup['filename']}\n"
                f"  Type: {backup['type']} | "
                f"Size: {size_mb:.1f}MB | "
                f"Created: {backup['created'].strftime('%Y-%m-%d %H:%M')}"
            )
        
        await interaction.followup.send("\n".join(lines), ephemeral=True)
    
    @app_commands.command(name="healthcheck", description="Run health check")
    @app_commands.checks.has_permissions(administrator=True)
    async def health_check(self, interaction: discord.Interaction):
        """Run health check"""
        await interaction.response.defer(ephemeral=True)
        
        from utils.health_checker import HealthChecker
        
        checker = HealthChecker(self.bot)
        results = await checker.run_full_check()
        
        report = checker.get_health_report()
        await interaction.followup.send(f"```\n{report}\n```", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
```

### Step 4: Update Logging Throughout

Replace all `log_system()` calls with the new logger:

**Before:**
```python
log_system(f"[ROLE_CONNECTION] Added role", level="info")
```

**After:**
```python
from utils.enhanced_logger import get_logger
logger = get_logger('role_connections')
logger.info("Added role to user")
```

### Step 5: Test the Integration

1. **Start the bot:**
   ```bash
   python bot.py
   ```

2. **Check startup logs:**
   - Should see "STARTUP COMPLETE"
   - Check `data/logs/bot.log` for details

3. **Test backup system:**
   ```
   /backup
   /listbackups
   ```

4. **Test health check:**
   ```
   /healthcheck
   ```

5. **Verify logging:**
   - Check `data/logs/` directory
   - Should have separate log files for each system

## File Structure After Integration

```
MalaBoT/
├── bot.py                    # Updated with startup manager
├── cogs/
│   ├── admin.py             # NEW - Admin commands
│   ├── role_connections.py  # Updated with SafeDatabase
│   ├── verify.py            # Updated with enhanced logging
│   └── ...
├── utils/
│   ├── backup_manager.py    # NEW
│   ├── safe_database.py     # NEW
│   ├── health_checker.py    # NEW
│   ├── enhanced_logger.py   # NEW
│   └── startup_manager.py   # NEW
├── data/
│   ├── bot.db
│   ├── backups/             # NEW - Automatic backups
│   │   ├── bot_backup_auto_20241030_120000.db
│   │   └── ...
│   └── logs/                # NEW - Separate log files
│       ├── bot.log
│       ├── database.log
│       ├── role_connections.log
│       ├── errors.log
│       └── ...
└── ...
```

## Benefits After Integration

### 1. Data Safety
- ✅ Daily automatic backups
- ✅ Manual backup command
- ✅ Backup before migrations
- ✅ Easy restore from backup

### 2. Visibility
- ✅ Separate log files per system
- ✅ Easy to find specific issues
- ✅ Comprehensive error tracking
- ✅ Audit trail of all operations

### 3. Reliability
- ✅ Startup verification
- ✅ Health monitoring
- ✅ Data integrity checks
- ✅ Automatic error recovery

### 4. Development
- ✅ Safe to add new features
- ✅ Easy to debug issues
- ✅ Clear separation of concerns
- ✅ Professional workflow

## Troubleshooting

### Issue: Startup fails
**Solution:** Check `data/logs/bot.log` for specific error

### Issue: Backups not created
**Solution:** Check `data/logs/backup.log` and verify `data/backups/` directory exists

### Issue: Health check fails
**Solution:** Run `/healthcheck` to see specific failures, check corresponding log files

### Issue: Role connections still lost
**Solution:** 
1. Check `data/logs/role_connections.log`
2. Verify data with `/healthcheck`
3. Check if backup exists in `data/backups/`
4. Restore from backup if needed

## Next Steps

1. ✅ Integrate all systems (follow steps above)
2. ✅ Test thoroughly on local bot
3. ✅ Deploy to production
4. ✅ Monitor logs for first 24 hours
5. ✅ Verify backups are being created
6. ✅ Test restore procedure

## Maintenance

### Daily
- Check `data/logs/errors.log` for issues
- Verify backup was created

### Weekly
- Review all log files
- Check disk space for logs/backups
- Test restore procedure

### Monthly
- Clean up old logs (keep last 30 days)
- Clean up old backups (keep last 7 days)
- Review and update documentation

## Support

If you encounter issues:
1. Check the specific log file in `data/logs/`
2. Run `/healthcheck` to diagnose
3. Check if backup exists
4. Review this guide for troubleshooting steps