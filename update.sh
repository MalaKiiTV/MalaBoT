#!/bin/bash

# MalaBoT Update Script
# Fully clean, update, and restart MalaBoT

set -e  # Exit on any error

# Configuration
BOT_DIR="/home/malabot/MalaBoT"
BACKUP_DIR="$BOT_DIR/backups"
LOG_DIR="$BOT_DIR/data/logs"
DB_FILE="$BOT_DIR/data/bot.db"
PYTHON_CMD="python3"
RESTART_REASON="${1:-manual}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Create timestamp for this update
TIMESTAMP=$(date '+%Y-%m-%d-%H%M')
UPDATE_LOG="$LOG_DIR/update_$TIMESTAMP.log"

# Start logging
exec > >(tee -a "$UPDATE_LOG")
exec 2>&1

log "Starting MalaBoT update process..."
log "Restart reason: $RESTART_REASON"
log "Update log: $UPDATE_LOG"

# Function to gracefully stop MalaBoT
stop_bot() {
    log "Stopping MalaBoT process..."
    
    # Find and kill MalaBoT processes (only our bot, not all Python processes)
    if pgrep -f "python.*bot.py" > /dev/null; then
        log "Found running MalaBoT process, stopping gracefully..."
        
        # Send SIGTERM for graceful shutdown
        pkill -TERM -f "python.*bot.py" || true
        
        # Wait up to 30 seconds for graceful shutdown
        for i in {1..30}; do
            if ! pgrep -f "python.*bot.py" > /dev/null; then
                log "MalaBoT stopped gracefully"
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if pgrep -f "python.*bot.py" > /dev/null; then
            warning "MalaBoT did not stop gracefully, force killing..."
            pkill -KILL -f "python.*bot.py" || true
        fi
    else
        log "No MalaBoT process found running"
    fi
}

# Function to create backups
create_backups() {
    log "Creating backups..."
    
    # Create backup directories
    mkdir -p "$BACKUP_DIR/logs/$TIMESTAMP"
    mkdir -p "$BACKUP_DIR/db/$TIMESTAMP"
    
    # Backup logs
    if [ -d "$LOG_DIR" ] && [ "$(ls -A $LOG_DIR 2>/dev/null)" ]; then
        log "Backing up logs to $BACKUP_DIR/logs/$TIMESTAMP"
        cp -r "$LOG_DIR"/* "$BACKUP_DIR/logs/$TIMESTAMP/" 2>/dev/null || true
    fi
    
    # Backup database
    if [ -f "$DB_FILE" ]; then
        log "Backing up database to $BACKUP_DIR/db/$TIMESTAMP"
        cp "$DB_FILE" "$BACKUP_DIR/db/$TIMESTAMP/bot.db"
        
        # Create database integrity backup
        sqlite3 "$DB_FILE" "PRAGMA integrity_check;" > "$BACKUP_DIR/db/$TIMESTAMP/integrity_check.txt" 2>/dev/null || true
    fi
    
    # Backup .env file if it exists
    if [ -f "$BOT_DIR/.env" ]; then
        cp "$BOT_DIR/.env" "$BACKUP_DIR/env_backup_$TIMESTAMP" 2>/dev/null || true
    fi
    
    log "Backups completed"
}

# Function to clean old backups
clean_old_backups() {
    log "Cleaning old backups..."
    
    # Keep only 10 most recent log backups
    find "$BACKUP_DIR/logs" -maxdepth 1 -type d -name "20*" | sort -r | tail -n +11 | xargs rm -rf 2>/dev/null || true
    
    # Keep only 10 most recent database backups
    find "$BACKUP_DIR/db" -maxdepth 1 -type d -name "20*" | sort -r | tail -n +11 | xargs rm -rf 2>/dev/null || true
    
    # Clean old env backups (keep 5)
    find "$BACKUP_DIR" -name "env_backup_*" | sort -r | tail -n +6 | xargs rm -f 2>/dev/null || true
    
    log "Old backups cleaned"
}

# Function to update code from Git
update_code() {
    log "Updating code from Git..."
    
    cd "$BOT_DIR"
    
    # Fetch all changes
    git fetch --all
    
    # Reset to latest main branch
    git reset --hard origin/main
    
    # Get latest commit info
    LATEST_COMMIT=$(git log -1 --oneline)
    log "Updated to: $LATEST_COMMIT"
    
    log "Code update completed"
}

# Function to install/update dependencies
update_dependencies() {
    log "Updating Python dependencies..."
    
    cd "$BOT_DIR"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        log "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install/update requirements
    pip install -r requirements.txt --upgrade
    
    log "Dependencies updated"
}

# Function to run database migrations
run_migrations() {
    log "Running database migrations..."
    
    cd "$BOT_DIR"
    
    # This would run any migration scripts if needed
    # For now, the database schema is auto-updated on startup
    
    log "Database migrations completed"
}

# Function to start the bot
start_bot() {
    log "Starting MalaBoT..."
    
    cd "$BOT_DIR"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Create data directories if they don't exist
    mkdir -p data/logs data/flags
    
    # Start bot in background with nohup
    nohup $PYTHON_CMD bot.py > data/logs/latest.log 2>&1 &
    
    BOT_PID=$!
    
    log "MalaBoT started with PID: $BOT_PID"
    log "Latest log file: data/logs/latest.log"
    
    # Wait a moment to check if startup was successful
    sleep 5
    
    if kill -0 $BOT_PID 2>/dev/null; then
        log "MalaBoT is running successfully"
    else
        error "MalaBoT failed to start or crashed immediately"
        error "Check data/logs/latest.log for details"
        exit 1
    fi
}

# Function to verify startup
verify_startup() {
    log "Verifying startup..."
    
    cd "$BOT_DIR"
    
    # Wait for bot to initialize
    sleep 10
    
    # Check if process is still running
    if pgrep -f "python.*bot.py" > /dev/null; then
        log "✅ MalaBoT is running successfully"
    else
        error "❌ MalaBoT is not running after startup"
        error "Check logs for errors"
        exit 1
    fi
    
    # Check latest log for startup message
    if [ -f "data/logs/latest.log" ]; then
        if grep -q "MalaBoT is now Locked in" data/logs/latest.log; then
            log "✅ Startup verification passed"
        else
            warning "⚠️ Startup verification inconclusive - check logs"
        fi
    fi
}

# Function to handle watchdog restarts
watchdog_restart() {
    log "Watchdog initiated restart - reason: $RESTART_REASON"
    
    # Create crash flag for recovery
    mkdir -p data/flags
    echo "$RESTART_REASON" > data/flags/crash_detected
    
    # Set restart reason in system flags if database is available
    if [ -f "$DB_FILE" ]; then
        sqlite3 "$DB_FILE" "INSERT OR REPLACE INTO system_flags (flag_name, flag_value, created_at) VALUES ('watchdog_restart', '$RESTART_REASON', datetime('now'));" 2>/dev/null || true
    fi
}

# Main update process
main() {
    log "=== MalaBoT Update Process Started ==="
    log "Working directory: $(pwd)"
    
    # Change to bot directory
    cd "$BOT_DIR" || {
        error "Cannot change to bot directory: $BOT_DIR"
        exit 1
    }
    
    # Handle watchdog restarts
    if [ "$RESTART_REASON" != "manual" ]; then
        watchdog_restart
    fi
    
    # Stop bot
    stop_bot
    
    # Create backups
    create_backups
    
    # Update code
    update_code
    
    # Clean caches
    log "Cleaning caches..."
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    rm -rf .pytest_cache 2>/dev/null || true
    
    # Update dependencies
    update_dependencies
    
    # Run migrations
    run_migrations
    
    # Clean old backups
    clean_old_backups
    
    # Start bot
    start_bot
    
    # Verify startup
    verify_startup
    
    log "=== MalaBoT Update Process Completed Successfully ==="
    log "Bot should be online and ready within 30 seconds"
    
    # Send completion notification (if configured)
    if [ -f ".env" ] && grep -q "OWNER_ALERTS_ENABLED=true" .env; then
        log "Owner alerts are enabled - owner will be notified of restart"
    fi
}

# Error handling
trap 'error "Update script failed at line $LINENO"' ERR

# Check if running as correct user
if [ "$EUID" -eq 0 ]; then
    error "Do not run this script as root"
    exit 1
fi

# Check if bot directory exists
if [ ! -d "$BOT_DIR" ]; then
    error "Bot directory not found: $BOT_DIR"
    exit 1
fi

# Check if Git repository
if [ ! -d "$BOT_DIR/.git" ]; then
    error "Not a Git repository: $BOT_DIR"
    exit 1
fi

# Run main process
main "$@"

exit 0