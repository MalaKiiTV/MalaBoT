# Role Connections Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: Connections Not Applying Immediately

**Symptom:** Role connections don't apply right away when conditions are met.

**Cause:** The system checks connections in two ways:
1. When member roles change (instant)
2. Every 5 minutes (periodic check)

**Solution:** 
- Wait up to 5 minutes for the periodic check
- OR trigger a role change (add/remove any role) to force immediate check

### Issue 2: Connection Shows as "Disabled"

**Symptom:** Connection exists but shows as disabled in config.

**Cause:** Connection was created but not enabled.

**Solution:**
1. Run `/setup` → Role Connections → Manage Connections
2. Select your connection
3. Click "Toggle Enable/Disable"
4. Verify it shows as "Enabled"

### Issue 3: Protected Roles Blocking Connections

**Symptom:** Connections don't apply to certain users.

**Cause:** Users have a protected role, which exempts them from all role connections.

**Solution:**
1. Run `/setup` → Role Connections → Manage Protected Roles
2. Check if the user has any protected roles
3. Remove protected role if needed

### Issue 4: Bot Missing Permissions

**Symptom:** Connections configured but roles not being assigned/removed.

**Cause:** Bot doesn't have permission to manage roles.

**Solution:**
1. Check bot's role position in Server Settings → Roles
2. Bot's role must be ABOVE the roles it's trying to assign/remove
3. Bot needs "Manage Roles" permission
4. Check bot logs for `[ROLE_CONNECTION] Missing permissions` errors

### Issue 5: Conditions Not Met

**Symptom:** Role not being assigned even though it should be.

**Cause:** Conditions might not be configured correctly.

**Solution:**
1. Review your connection logic:
   - **AND logic:** ALL conditions must be true
   - **OR logic:** AT LEAST ONE condition must be true
2. Check condition types:
   - **HAS:** User must have the specified role
   - **DOESN'T HAVE:** User must NOT have the specified role
3. Verify the user actually meets the conditions

### Issue 6: Target Role Deleted

**Symptom:** Connection exists but nothing happens.

**Cause:** The target role was deleted from the server.

**Solution:**
1. Run `/setup` → Role Connections → Manage Connections
2. Delete the broken connection
3. Create a new connection with a valid role

## Diagnostic Steps

### Step 1: Verify Connection Exists and is Enabled

```
1. Run /setup → View Current Config
2. Check "Role Connections" section
3. Should show: "Active Connections: X" (where X > 0)
4. If X = 0, no active connections exist
```

### Step 2: Check Connection Details

```
1. Run /setup → Role Connections → Manage Connections
2. Select your connection
3. Verify:
   - Target role is correct
   - Action is correct (give/remove)
   - Conditions are correct
   - Logic is correct (AND/OR)
   - Status shows "Enabled"
```

### Step 3: Check Bot Logs

Look for these log messages:
- `[ROLE_CONNECTION] Added {role} to {user}` - Success
- `[ROLE_CONNECTION] Removed {role} from {user}` - Success
- `[ROLE_CONNECTION] Missing permissions` - Permission error
- `[ROLE_CONNECTION] Skipping {user} - member is locked` - Processing conflict
- `[ROLE_CONNECTION] Error processing {user}` - General error

### Step 4: Test with Simple Connection

Create a test connection:
```
Target Role: TestRole
Action: Give
Condition: User DOESN'T HAVE @everyone
Logic: AND
```

This should give TestRole to everyone (since no one can "not have" @everyone is false, but you can test with a real role).

Better test:
```
Target Role: TestRole
Action: Give
Condition: User HAS @everyone
Logic: AND
```

This should give TestRole to everyone immediately.

### Step 5: Force Immediate Check

To force an immediate check without waiting 5 minutes:
1. Add any role to yourself
2. Remove that role
3. This triggers on_member_update which processes connections

## Common Configuration Mistakes

### Mistake 1: Backwards Logic

**Wrong:**
- Give "Verified" when user DOESN'T HAVE "Unverified"

**Right:**
- Give "Verified" when user HAS "Member"
- OR Remove "Unverified" when user HAS "Verified"

### Mistake 2: Conflicting Connections

**Problem:**
- Connection 1: Give "RoleA" when has "RoleB"
- Connection 2: Remove "RoleA" when has "RoleB"

**Result:** Infinite loop (fixed with processing lock, but still inefficient)

**Solution:** Review all connections for conflicts

### Mistake 3: Using AND with DOESN'T HAVE

**Problem:**
- Give "RoleA" when user DOESN'T HAVE "RoleB" AND DOESN'T HAVE "RoleC"

**Issue:** User must not have BOTH roles (might not be what you want)

**Solution:** Consider using OR logic instead

## System Behavior

### When Connections Are Checked

1. **On Member Role Change:**
   - Triggered by: Manual role add/remove, other bots, other systems
   - Processing: Immediate
   - Scope: Only the member whose roles changed

2. **Periodic Check (Every 5 Minutes):**
   - Triggered by: Automatic timer
   - Processing: All members in all guilds
   - Scope: Everyone

3. **On Bot Startup:**
   - Triggered by: Bot restart
   - Processing: After bot is ready
   - Scope: All members in all guilds (first periodic check)

### Processing Lock System

The bot uses a processing lock to prevent conflicts:
- When cheater role is being assigned, role connections are paused
- When role connections are processing, cheater system waits
- This prevents infinite loops and rate limits

## Getting Help

If role connections still aren't working after following this guide:

1. **Gather Information:**
   - Screenshot of connection configuration
   - Screenshot of "View Current Config" showing role connections
   - Bot log messages (last 50 lines with [ROLE_CONNECTION])
   - Description of expected vs actual behavior

2. **Check These:**
   - [ ] Connection is enabled
   - [ ] Bot has "Manage Roles" permission
   - [ ] Bot's role is above target role
   - [ ] User doesn't have protected role
   - [ ] Conditions are correct
   - [ ] Logic (AND/OR) is correct
   - [ ] Target role exists
   - [ ] Waited at least 5 minutes OR triggered role change

3. **Test Connection:**
   - Create a simple test connection
   - Test with yourself
   - Check if it works
   - If yes: Original connection has wrong conditions
   - If no: Permission or system issue

## Technical Details

### Database Storage

Connections are stored in the database with this structure:
```python
{
    "id": "unique_id",
    "target_role_id": 123456789,
    "action": "give" or "remove",
    "conditions": [
        {"role_id": 123456789, "type": "has"},
        {"role_id": 987654321, "type": "doesnt_have"}
    ],
    "logic": "AND" or "OR",
    "enabled": true or false
}
```

### Condition Evaluation

**AND Logic:**
- ALL conditions must be true
- Example: Has RoleA AND Has RoleB → Both required

**OR Logic:**
- AT LEAST ONE condition must be true
- Example: Has RoleA OR Has RoleB → Either one works

**Condition Types:**
- **has:** User must have the role
- **doesnt_have:** User must NOT have the role

### Processing Flow

```
1. Member roles change (or periodic check)
2. Check if member is locked (processing_members)
3. Check if member has protected role
4. Load all connections for guild
5. For each enabled connection:
   a. Evaluate conditions
   b. Check if action needed
   c. Apply role change if needed
6. Log result
```