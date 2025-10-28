"""
System cleanup script for MalaBoT
Cleans up cache files, temporary files, and old logs
"""

import os
import shutil
import sys
from pathlib import Path

def cleanup_pycache():
    """Remove Python cache files"""
    print("Cleaning Python cache files...")
    count = 0
    for root, dirs, files in os.walk('.'):
        # Remove __pycache__ directories
        if '__pycache__' in dirs:
            cache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(cache_path)
                count += 1
                print(f"  Removed: {cache_path}")
            except Exception as e:
                print(f"  Error removing {cache_path}: {e}")
        
        # Remove .pyc files
        for file in files:
            if file.endswith('.pyc'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    count += 1
                except Exception as e:
                    print(f"  Error removing {file_path}: {e}")
    
    print(f"Cleaned {count} Python cache items")

def cleanup_pytest_cache():
    """Remove pytest cache"""
    print("Cleaning pytest cache...")
    pytest_cache = Path('.pytest_cache')
    if pytest_cache.exists():
        try:
            shutil.rmtree(pytest_cache)
            print("  Removed .pytest_cache")
        except Exception as e:
            print(f"  Error removing pytest cache: {e}")
    else:
        print("  No pytest cache found")

def cleanup_temp_files():
    """Remove temporary files"""
    print("Cleaning temporary files...")
    count = 0
    temp_extensions = ['.tmp', '.temp', '.log~', '.bak']
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if any(file.endswith(ext) for ext in temp_extensions):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    count += 1
                    print(f"  Removed: {file_path}")
                except Exception as e:
                    print(f"  Error removing {file_path}: {e}")
    
    print(f"Cleaned {count} temporary files")

def cleanup_old_logs():
    """Keep only the last 5 log files"""
    print("Cleaning old log files...")
    log_dir = Path('data/logs')
    
    if not log_dir.exists():
        print("  No log directory found")
        return
    
    log_files = sorted(log_dir.glob('*.log'), key=os.path.getmtime, reverse=True)
    
    if len(log_files) <= 5:
        print(f"  Only {len(log_files)} log files found, keeping all")
        return
    
    # Keep the 5 most recent, delete the rest
    files_to_delete = log_files[5:]
    for log_file in files_to_delete:
        try:
            os.remove(log_file)
            print(f"  Removed: {log_file}")
        except Exception as e:
            print(f"  Error removing {log_file}: {e}")
    
    print(f"Kept 5 most recent logs, removed {len(files_to_delete)} old logs")

def cleanup_discord_cache():
    """Remove Discord.py cache"""
    print("Cleaning Discord.py cache...")
    # Discord.py doesn't create persistent cache files by default
    print("  No Discord.py cache to clean")

def main():
    """Run all cleanup operations"""
    print("=" * 50)
    print("MalaBoT System Cleanup")
    print("=" * 50)
    print()
    
    try:
        cleanup_pycache()
        print()
        cleanup_pytest_cache()
        print()
        cleanup_temp_files()
        print()
        cleanup_old_logs()
        print()
        cleanup_discord_cache()
        print()
        print("=" * 50)
        print("Cleanup completed successfully!")
        print("=" * 50)
        return 0
    except Exception as e:
        print()
        print("=" * 50)
        print(f"Cleanup failed with error: {e}")
        print("=" * 50)
        return 1

if __name__ == "__main__":
    sys.exit(main())