#!/bin/bash

# MalaBoT Update Script for Linux Droplet
# Fully clean, update, and restart MalaBoT with online notification

echo "========================================"
echo "MalaBoT Droplet Update Script"
echo "========================================"
echo

# Stop the bot if it's running
echo "Stopping MalaBoT..."
pkill -f "python.*bot.py" || true
sleep 3

# Pull latest changes from GitHub
echo "Pulling latest changes from GitHub..."
git pull origin main

# Clear cache files
echo "Clearing cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
rm -rf .pytest_cache 2>/dev/null || true

# Clear log files
echo "Clearing log files..."
rm -rf data/logs/* 2>/dev/null || true
mkdir -p data/logs

# Clear command cache
echo "Clearing command cache..."
rm -f data/command_cache* 2>/dev/null || true

# Install/update dependencies
echo "Installing/Updating dependencies..."
pip install -r requirements.txt --upgrade

# Start the bot
echo "Starting MalaBoT..."
nohup python bot.py > data/logs/bot.log 2>&1 &

echo
echo "Update complete!"
echo "Bot is now running in the background"
echo "Check data/logs/bot.log for startup status"