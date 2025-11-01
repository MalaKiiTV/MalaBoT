#!/usr/bin/env python3
"""Test script to validate bot startup without connecting to Discord"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Testing bot startup...")

try:
    # Test settings
    from config.settings import settings
    print("✓ Settings loaded")
    
    # Test basic imports
    from bot import MalaBoT
    print("✓ Bot class imported")
    
    # Create bot instance
    bot = MalaBoT()
    print("✓ Bot instance created")
    
    # Test database initialization
    import asyncio
    
    async def test_db():
        try:
            await bot._initialize_database()
            print("✓ Database initialized")
            return True
        except Exception as e:
            print(f"✗ Database initialization failed: {e}")
            return False
    
    # Run database test
    result = asyncio.run(test_db())
    
    if result:
        print("\n✅ Bot startup test passed! All core components are working.")
    else:
        print("\n❌ Bot startup test failed during database initialization.")
        
except Exception as e:
    print(f"\n❌ Bot startup test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)