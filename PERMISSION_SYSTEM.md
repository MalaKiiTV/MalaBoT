# Permission System Documentation

## Overview
MalaBoT uses a three-tier permission system for command access control:

1. **Owner** - Bot owners (defined in config)
2. **Mod** - Users with the configured mod role
3. **Public** - All users

## Permission Tiers

### Owner Permissions
- Full access to all commands
- Can configure bot settings via `/setup`
- Defined in `config/settings.py` via `OWNER_IDS`

### Mod Permissions
- Can use moderation commands (`/delete`, `/kick`, `/ban`, `/mute`, `/unmute`)
- Can manage XP (`/xpadd`, `/xpremove`, `/xpset`, `/xpreset`)
- Can review verifications (`/verify review`)
- Can review appeals (`/appeal review`) - when implemented
- Configured via `/setup` → General Settings → Set Mod Role

### Public Permissions
- Can use all public commands
- Can submit verifications (`/verify activision`)
- Can submit appeals (`/appeal submit`) - when implemented
- Can check XP, leaderboard, etc.

## Configuration

### Setting Up Mod Roles

#### General Mod Role
The general mod role applies to all mod-level commands:
1. Use `/setup`
2. Select "General Settings"
3. Click "Set Mod Role"
4. Select the role from the dropdown

This role will be used for:
- All moderation commands
- XP management commands
- Verification reviews (if no specific role is set)
- Appeal reviews (if no specific role is set)

#### Verification-Specific Mod Role (Optional)
You can set a specific role for verification reviews:
1. Use `/setup`
2. Select "Verification System"
3. Select the verification mod role from the dropdown

If set, this role will be checked first for `/verify review` commands.
If not set, the general mod role will be used.

#### Appeal-Specific Mod Role (Optional) - When Implemented
You can set a specific role for appeal reviews:
1. Use `/setup`
2. Select "Appeal System"
3. Select the appeal mod role from the dropdown

If set, this role will be checked first for `/appeal review` commands.
If not set, the general mod role will be used.

## Database Keys

### Mod Role Keys
- `mod_role_{guild_id}` - General mod role for all commands
- `verification_mod_role_{guild_id}` - Specific role for verification reviews
- `appeal_mod_role_{guild_id}` - Specific role for appeal reviews (when implemented)

## Permission Check Flow

### For Commands with Specific Mod Roles
1. Check if user is bot owner → Grant access
2. Check if user has specific mod role (e.g., verification_mod_role) → Grant access
3. Check if user has general mod role → Grant access
4. Deny access

### For Commands with General Mod Role Only
1. Check if user is bot owner → Grant access
2. Check if user has general mod role → Grant access
3. Deny access

## Helper Functions

### `is_mod(interaction, db_manager, specific_mod_role_key=None)`
Checks if a user has mod permissions.

**Parameters:**
- `interaction`: Discord interaction object
- `db_manager`: Database manager instance
- `specific_mod_role_key`: Optional specific mod role key (e.g., "verification_mod_role")

**Returns:** `bool` - True if user has permission

**Example:**
```python
if await is_mod(interaction, self.bot.db_manager, "verification_mod_role"):
    # User has permission
    pass
```

### `check_mod_permission(interaction, db_manager, specific_mod_role_key=None)`
Checks mod permission and sends error message if denied.

**Parameters:**
- `interaction`: Discord interaction object
- `db_manager`: Database manager instance
- `specific_mod_role_key`: Optional specific mod role key

**Returns:** `bool` - True if user has permission (False and sends error message if not)

**Example:**
```python
if not await check_mod_permission(interaction, self.bot.db_manager, "verification_mod_role"):
    return  # Error message already sent
```

## Command Permission Requirements

### Owner Only
- `/setup` - Configure all bot settings

### Mod Only
- `/delete` - Delete messages
- `/kick` - Kick users
- `/ban` - Ban users
- `/mute` - Mute users
- `/unmute` - Unmute users
- `/xpadd` - Add XP to users
- `/xpremove` - Remove XP from users
- `/xpset` - Set user XP
- `/xpreset` - Reset user XP
- `/verify review` - Review verifications (uses verification_mod_role or mod_role)
- `/appeal review` - Review appeals (uses appeal_mod_role or mod_role) - when implemented

### Public
- All other commands

## Migration from Old System

### Changes Made
1. **Removed Administrator Checks**: All commands that required administrator permissions now require owner permissions
2. **Renamed Staff to Mod**: All references to "staff" have been changed to "mod"
3. **Database Keys Updated**: `staff_role_{guild_id}` → `mod_role_{guild_id}`
4. **Specific Mod Roles**: Added support for command-specific mod roles (verification, appeals)

### What Users Need to Do
1. Reconfigure mod role in `/setup` → General Settings
2. Optionally configure verification-specific mod role in `/setup` → Verification System
3. Restart Discord client to clear command cache

## Error Messages

When a user lacks permissions, they will see:
```
🚫 Permission Denied

This command is only available to:
• Bot Owners
• Users with mod role:
  • [Role Name]

Your current permissions:
• Bot Owner: ❌
```

For commands with specific mod roles, both the specific and general mod roles will be listed.