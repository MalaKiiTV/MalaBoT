"""
MalaBoT Complete System Cleanup Script
Clears all caches, temporary files, and prepares for fresh start.

Usage:
    python cleanup.py
    python cleanup.py --auto  (skip confirmation)
"""

import os
import sys
import shutil
from pathlib import Path

def clear_python_cache():
    """Clear Python cache files."""
    print("🧹 Clearing Python cache...")
    count = 0
    
    # Remove .pyc files
    for pyc_file in Path('.').rglob('*.pyc'):
        try:
            pyc_file.unlink()
            count += 1
        except Exception as e:
            print(f"  ⚠️  Failed to delete {pyc_file}: {e}")
    
    # Remove __pycache__ directories
    for pycache_dir in Path('.').rglob('__pycache__'):
        try:
            shutil.rmtree(pycache_dir)
            count += 1
        except Exception as e:
            print(f"  ⚠️  Failed to delete {pycache_dir}: {e}")
    
    print(f"  ✅ Cleared {count} Python cache items")
    return count

def clear_pytest_cache():
    """Clear pytest cache."""
    print("🧹 Clearing pytest cache...")
    pytest_cache = Path('.pytest_cache')
    if pytest_cache.exists():
        try:
            shutil.rmtree(pytest_cache)
            print("  ✅ Pytest cache cleared")
            return 1
        except Exception as e:
            print(f"  ⚠️  Failed to clear pytest cache: {e}")
            return 0
    else:
        print("  ℹ️  No pytest cache found")
        return 0

def clear_temp_files():
    """Clear temporary files."""
    print("🧹 Clearing temporary files...")
    count = 0
    
    temp_patterns = ['*.tmp', '*.log', '*.bak', '*~']
    for pattern in temp_patterns:
        for temp_file in Path('.').glob(pattern):
            try:
                temp_file.unlink()
                count += 1
            except Exception as e:
                print(f"  ⚠️  Failed to delete {temp_file}: {e}")
    
    # Clear temp directory if exists
    temp_dir = Path('temp')
    if temp_dir.exists():
        try:
            shutil.rmtree(temp_dir)
            count += 1
        except Exception as e:
            print(f"  ⚠️  Failed to clear temp directory: {e}")
    
    print(f"  ✅ Cleared {count} temporary items")
    return count

def clear_old_logs(keep_count=5):
    """Clear old log files, keeping the most recent ones."""
    print(f"🧹 Clearing old logs (keeping last {keep_count})...")
    logs_dir = Path('data/logs')
    
    if not logs_dir.exists():
        print("  ℹ️  No logs directory found")
        return 0
    
    # Get all log files sorted by modification time
    log_files = sorted(logs_dir.glob('*.log'), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if len(log_files) <= keep_count:
        print(f"  ℹ️  Only {len(log_files)} log files found, nothing to clear")
        return 0
    
    # Delete old logs
    count = 0
    for log_file in log_files[keep_count:]:
        try:
            log_file.unlink()
            count += 1
        except Exception as e:
            print(f"  ⚠️  Failed to delete {log_file}: {e}")
    
    print(f"  ✅ Cleared {count} old log files")
    return count

def clear_discord_cache():
    """Clear Discord.py cache."""
    print("🧹 Clearing Discord cache...")
    count = 0
    
    # Common Discord cache locations
    cache_locations = [
        Path.home() / 'AppData' / 'Local' / 'discord',
        Path.home() / 'AppData' / 'Roaming' / 'discord',
        Path.home() / '.cache' / 'discord',
    ]
    
    for cache_dir in cache_locations:
        if cache_dir.exists():
            try:
                shutil.rmtree(cache_dir)
                count += 1
                print(f"  ✅ Cleared {cache_dir}")
            except Exception as e:
                print(f"  ⚠️  Failed to clear {cache_dir}: {e}")
    
    if count == 0:
        print("  ℹ️  No Discord cache found")
    
    return count

def clear_build_artifacts():
    """Clear build artifacts."""
    print("🧹 Clearing build artifacts...")
    count = 0
    
    build_dirs = ['build', 'dist', '*.egg-info']
    for pattern in build_dirs:
        for build_dir in Path('.').glob(pattern):
            if build_dir.is_dir():
                try:
                    shutil.rmtree(build_dir)
                    count += 1
                except Exception as e:
                    print(f"  ⚠️  Failed to delete {build_dir}: {e}")
    
    if count > 0:
        print(f"  ✅ Cleared {count} build artifacts")
    else:
        print("  ℹ️  No build artifacts found")
    
    return count

def main():
    """Main cleanup function."""
    # Check if running in automated mode
    automated = '--auto' in sys.argv
    
    if not automated:
        print("\n" + "="*60)
        print("MalaBoT Complete System Cleanup")
        print("="*60 + "\n")
        print("This will clear:")
        print("  • Python cache files (.pyc, __pycache__)")
        print("  • Pytest cache")
        print("  • Temporary files (*.tmp, *.log, *.bak)")
        print("  • Old log files (keeping last 5)")
        print("  • Discord cache")
        print("  • Build artifacts")
        print("\n⚠️  WARNING: This operation cannot be undone!\n")
        
        try:
            response = input("Continue? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("❌ Cancelled by user")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user")
            sys.exit(0)
        
        print("\n🚀 Starting cleanup process...\n")
    
    try:
        total_cleared = 0
        
        # Run all cleanup operations
        total_cleared += clear_python_cache()
        total_cleared += clear_pytest_cache()
        total_cleared += clear_temp_files()
        total_cleared += clear_old_logs(keep_count=5)
        total_cleared += clear_discord_cache()
        total_cleared += clear_build_artifacts()
        
        print("\n" + "="*60)
        print(f"✅ Cleanup Complete! Cleared {total_cleared} items total")
        print("="*60)
        
        if not automated:
            print("\n📝 Next steps:")
            print("   1. Run: python clear_and_sync.py (to clear Discord commands)")
            print("   2. Start your bot: python bot.py")
            print("   3. Wait 30 seconds for commands to sync")
            print("   4. Test commands in Discord\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())