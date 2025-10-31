# Role Connections Diagnostic Guide

## Quick Diagnostic Steps

### Step 1: Check Configuration
Run `/setup` → "View Current Config"
- Look at "Role Connections" section
- Note: Active Connections, Disabled Connections, Protected Roles counts

### Step 2: Check Connection Status
Run `/setup` → Role Connections → Manage Connections
- Select each connection
- Verify it shows "Enabled" (not "Disabled")
- Check the target role, action, conditions, and logic

### Step 3: Check Bot Logs
Look for `[ROLE_CONNECTION]` messages:
- "Added {role} to {user}" = Working ✅
- "Removed {role} from {user}" = Working ✅
- "Skipping {user} - member is locked" = Processing conflict
- "Missing permissions" = Permission issue
- "Error processing" = System error

### Step 4: Test Simple Connection
Create test connection:
- Target Role: Any test role
- Action: Give
- Condition: User HAS @everyone
- Logic: AND
- Enable it

Then:
1. Add/remove any role from yourself (triggers on_member_update)
2. OR wait 5 minutes (periodic check)
3. Check if you got the test role

## Common Issues

### Issue 1: Connections Disabled
**Symptom:** Connections exist but don't apply
**Fix:** Enable them in Manage Connections

### Issue 2: Bot Role Position
**Symptom:** No errors but roles not applying
**Fix:** Bot's role must be ABOVE target roles in Server Settings

### Issue 3: Protected Roles
**Symptom:** Works for some users, not others
**Fix:** Check if users have protected roles

### Issue 4: Wrong Conditions
**Symptom:** Roles not applying when expected
**Fix:** Review AND/OR logic and HAS/DOESN'T HAVE conditions

### Issue 5: Processing Lock Conflict
**Symptom:** Logs show "member is locked"
**Fix:** This is normal during cheater assignment, should resolve automatically

## Need More Help?

Provide:
1. Screenshot of connection configuration
2. Screenshot of "View Current Config" 
3. Bot log lines with [ROLE_CONNECTION]
4. Description of expected vs actual behavior