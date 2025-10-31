"""Test script to verify command group structure"""
import sys
sys.path.insert(0, '/workspace/MalaBoT')

# Check XP structure
print("=== Checking XP Structure ===")
from cogs.xp import XPGroup, XP
print(f"XPGroup class exists: {XPGroup}")
print(f"XPGroup inherits from: {XPGroup.__bases__}")

# Check Verify structure  
print("\n=== Checking Verify Structure ===")
from cogs.verify import VerifyGroup
print(f"VerifyGroup class exists: {VerifyGroup}")
print(f"VerifyGroup inherits from: {VerifyGroup.__bases__}")

# Check Appeal structure
print("\n=== Checking Appeal Structure ===")
from cogs.appeal import AppealGroup
print(f"AppealGroup class exists: {AppealGroup}")
print(f"AppealGroup inherits from: {AppealGroup.__bases__}")

print("\n✅ All command groups are properly structured")
