# Deployment Instructions - Supabase Migration

## 🚀 Quick Start

To deploy the Supabase-migrated version of MalaBoT, follow these steps:

### 1. Update Environment Variables

**Critical**: Update your `.env` file on both local and droplet environments:

```bash
# Add these new Supabase variables
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key-here
GUILD_ID=542004156513255445

# Remove or comment out the old SQLite line
# DATABASE_URL=sqlite:///data/bot.db
```

### 2. Update Dependencies

Install the new requirements on both environments:

```bash
# On local
pip install -r requirements.txt

# On droplet
pip install -r requirements.txt
```

### 3. Restart the Bot

```bash
# On local
python bot.py

# On droplet (depending on your setup)
pm2 restart mala-bot
# or
systemctl restart malabot
# or
python bot.py
```

## 📋 Detailed Steps

### Environment Setup

1. **Get Supabase Credentials**:
   - Go to your Supabase dashboard
   - Project Settings → API
   - Copy the Project URL and anon public key

2. **Update .env Files**:
   - Local: `/.env`
   - Droplet: `~/.env` (or wherever your bot's .env is located)

3. **Verify Environment**:
   ```bash
   # Check that variables are set
   echo $SUPABASE_URL
   echo $SUPABASE_KEY
   ```

### Dependency Management

1. **Remove Old Dependencies** (optional cleanup):
   ```bash
   pip uninstall aiosqlite
   ```

2. **Install New Dependencies**:
   ```bash
   pip install supabase
   ```

### Testing the Migration

1. **Start the Bot** and watch the logs:
   ```bash
   python bot.py
   ```

2. **Look for these successful messages**:
   - `✅ Supabase connection verified`
   - `Database initialized successfully`
   - `MalaBoT is now Locked in!`

3. **Test Core Commands**:
   - `/xp` - Test XP system
   - `/birthday` - Test birthday commands
   - Any bot command that uses the database

4. **Verify Data Persistence**:
   - Add some XP
   - Restart the bot
   - Check if XP is still there

### Troubleshooting

#### Common Issues

**Issue**: `SUPABASE_URL not found`
```bash
# Solution: Check .env file
cat .env | grep SUPABASE
```

**Issue**: `Invalid Supabase credentials`
```bash
# Solution: Verify URL and key format
# URL should be: https://project-id.supabase.co
# Key should start with: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Issue**: `ModuleNotFoundError: No module named 'supabase'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Issue**: Bot starts but commands don't work
```bash
# Solution: Check Supabase tables exist
# Go to Supabase dashboard → Table Editor
# Verify tables: users, birthdays, audit_log, etc.
```

#### Log Analysis

Check these log patterns:
- ✅ Success: `Database initialized successfully`
- ❌ Error: `Failed to initialize database`
- ❌ Error: `Supabase connection failed`

### Verification Checklist

- [ ] Environment variables set correctly
- [ ] Dependencies installed
- [ ] Bot starts without errors
- [ ] Database connection successful
- [ ] Commands working properly
- [ ] Data persists across restarts
- [ ] No SQLite-related errors in logs

## 🔄 Rollback Plan

If you encounter issues and need to rollback to SQLite:

1. **Restore .env file**:
   ```bash
   DATABASE_URL=sqlite:///data/bot.db
   # Remove SUPABASE variables
   ```

2. **Restore requirements.txt**:
   ```bash
   pip install aiosqlite
   pip uninstall supabase
   ```

3. **Restore archive files** (if needed):
   ```bash
   cp archive/sqlite_migrations/models.py database/
   ```

4. **Update imports** in bot.py and test files

## 📞 Support

If you encounter issues:

1. **Check the logs** first - most issues are clearly logged
2. **Verify Supabase tables** exist in your dashboard
3. **Check environment variables** are correctly set
4. **Review the migration documentation** in `MIGRATION_SUMMARY.md`

## 🎉 Success Indicators

You'll know the migration was successful when:
- Bot starts with `Database initialized successfully`
- Commands work and data persists
- No SQLite-related errors in logs
- Supabase dashboard shows new data being created
- Both local and droplet instances sync data

---

**🚀 Your bot is now running on Supabase! Enjoy the improved scalability and reliability!**