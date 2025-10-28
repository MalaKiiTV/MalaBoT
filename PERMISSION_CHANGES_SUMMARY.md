# Permission System Restructuring - Summary of Changes

## Overview
Restructured the entire permission system from a four-tier system (Owner/Admin/Staff/Public) to a three-tier system (Owner/Mod/Public).

## Key Changes

### 1. Permission Tiers
**Before:**
- Owner (bot owners)
- Admin (server administrators)
- Staff (staff role)
- Public (everyone)

**After:**
- Owner (bot owners)
- Mod (mod role)
- Public (everyone)

### 2. Database Keys
- `staff_role_{guild_id}` → `mod_role_{guild_id}`
- Added `verification_mod_role_{guild_id}` for verification-specific permissions
- Added `appeal_mod_role_{guild_id}` for appeal-specific permissions (when implemented)

### 3. Helper Functions (utils/helpers.py)
**Added:**
- `is_mod(interaction, db_manager, specific_mod_role_key=None)` - Check if user has mod permissions
- `check_mod_permission(interaction, db_manager, specific_mod_role_key=None)` - Check and send error if denied

**Removed:**
- `is_staff()` - Replaced with `is_mod()`
- `check_staff_permission()` - Replaced with `check_mod_permission()`

### 4. Modified Files

#### cogs/moderation.py
- Updated all 5 commands (delete, kick, ban, mute, unmute)
- Replaced admin permission checks with mod permission checks
- Now uses `check_mod_permission()` helper function

#### cogs/xp.py
- Updated all 5 admin commands (xpadd, xpremove, xpset, xpreset, daily)
- Replaced admin permission checks with mod permission checks
- Now uses `check_mod_permission()` helper function

#### cogs/verify.py
- Updated `/verify review` command
- Removed `@app_commands.checks.has_permissions(manage_roles=True)` decorator
- Added permission check using `check_mod_permission()` with "verification_mod_role" key
- Falls back to general mod role if verification-specific role not set

#### cogs/setup.py
- Changed `/setup` command from admin-only to owner-only
- Added "Set Mod Role" button to General Settings
- Added `VerificationModRoleSelect` class for verification-specific mod role
- Updated all configuration views to show mod roles
- Updated descriptions to reflect new permission system

### 5. Setup System Changes

#### General Settings
**Added:**
- Mod Role selector (dropdown)
- Displays current mod role in config view

#### Verification System
**Added:**
- Verification Mod Role selector (dropdown, optional)
- Falls back to general mod role if not set
- Displays both roles in config view

### 6. Command Permission Changes

#### Owner Only (Changed from Admin)
- `/setup` - Now requires bot owner instead of administrator

#### Mod Only (Changed from Admin/Staff)
- `/delete` - Now requires mod role
- `/kick` - Now requires mod role
- `/ban` - Now requires mod role
- `/mute` - Now requires mod role
- `/unmute` - Now requires mod role
- `/xpadd` - Now requires mod role
- `/xpremove` - Now requires mod role
- `/xpset` - Now requires mod role
- `/xpreset` - Now requires mod role
- `/verify review` - Now requires verification mod role or general mod role

### 7. Error Messages
Updated error messages to show:
- Bot owner status
- Mod role requirements (both specific and general if applicable)
- Clear indication of which roles grant access

## Migration Guide for Users

### Step 1: Update Code
```bash
git pull origin main
```

### Step 2: Configure Mod Role
1. Use `/setup`
2. Select "General Settings"
3. Click "Set Mod Role"
4. Select your mod role

### Step 3: (Optional) Configure Verification Mod Role
1. Use `/setup`
2. Select "Verification System"
3. Select verification mod role (or leave empty to use general mod role)

### Step 4: Restart Discord
- Press Ctrl+R to clear Discord's command cache
- This ensures you see the updated command descriptions

## Technical Details

### Permission Check Flow
1. Check if user is bot owner → Grant access
2. Check if specific mod role exists and user has it → Grant access
3. Check if user has general mod role → Grant access
4. Deny access and send error message

### Database Schema
No database migrations needed - the system uses the existing settings table with new keys.

### Backward Compatibility
- Old `staff_role_{guild_id}` keys will not be automatically migrated
- Users must reconfigure their mod role via `/setup`

## Testing Checklist
- [ ] Owner can access `/setup`
- [ ] Non-owners cannot access `/setup`
- [ ] Mod role users can use moderation commands
- [ ] Mod role users can use XP commands
- [ ] Verification mod role users can review verifications
- [ ] General mod role users can review verifications (if no specific role set)
- [ ] Non-mod users cannot use mod commands
- [ ] Error messages display correctly
- [ ] Setup system shows all mod roles correctly

## Files Modified
1. `utils/helpers.py` - Added mod permission helper functions
2. `cogs/moderation.py` - Updated all moderation commands
3. `cogs/xp.py` - Updated all XP admin commands
4. `cogs/verify.py` - Updated review command
5. `cogs/setup.py` - Added mod role selectors, changed to owner-only

## Files Created
1. `PERMISSION_SYSTEM.md` - Comprehensive permission system documentation
2. `PERMISSION_CHANGES_SUMMARY.md` - This file

## Breaking Changes
- `/setup` now requires bot owner (was administrator)
- All mod commands now require configured mod role (was administrator or staff role)
- Users must reconfigure their mod role via `/setup`