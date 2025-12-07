# Birthday Pending System - Testing Guide

## Pre-Testing Setup

### 1. Database Verification
Ensure the settings table exists and can handle new settings:
```sql
SELECT * FROM settings WHERE setting_key LIKE '%birthday%' OR setting_key LIKE '%welcome%' OR setting_key LIKE '%goodbye%';
```

### 2. Required Settings
The following settings will be used:
- `birthday_pending_enabled` - "true"/"false"
- `birthday_pending_role` - role_id as string
- `birthday_reminder_channel` - channel_id as string
- `birthday_reminder_message_id` - message_id as string
- `birthday_announcements_enabled` - "true"/"false"
- `welcome_enabled` - "true"/"false"
- `goodbye_enabled` - "true"/"false"

---

## Test Scenarios

### TEST 1: Birthday Pending System Setup
**Goal:** Verify setup UI works correctly

**Steps:**
1. Run `/setup` → Select "Birthday System"
2. Click "Birthday Pending" button
3. Click "Toggle System" → Should enable
4. Click "Set Role" → Select a role
5. Click "Set Channel" → Select a channel
6. Click "Setup Message" → Should post message in channel
7. Click "View Config" → Verify all settings shown

**Expected Results:**
- ✅ All buttons respond correctly
- ✅ Settings saved to database
- ✅ Persistent message appears in channel
- ✅ Role added to protected roles automatically

---

### TEST 2: New Member Join
**Goal:** Verify Birthday Pending role is assigned

**Steps:**
1. Enable Birthday Pending system
2. Set Birthday Pending role
3. Have a new member join the server
4. Check member's roles

**Expected Results:**
- ✅ Member receives Birthday Pending role
- ✅ Log entry created
- ✅ No errors in console

---

### TEST 3: Birthday Button Click
**Goal:** Verify persistent button works

**Steps:**
1. Click the "Set Your Birthday" button in reminder channel
2. Modal should open
3. Enter birthday in MM-DD format
4. Submit

**Expected Results:**
- ✅ Modal opens correctly
- ✅ Birthday saved to database
- ✅ Birthday Pending role removed
- ✅ Success message shown

---

### TEST 4: Bot Restart Persistence
**Goal:** Verify button works after restart

**Steps:**
1. Setup birthday reminder message
2. Restart the bot
3. Click the button

**Expected Results:**
- ✅ Button still works after restart
- ✅ Modal opens correctly
- ✅ No "Interaction Failed" errors

---

### TEST 5: Protected Roles Integration
**Goal:** Verify Birthday Pending role is protected

**Steps:**
1. Enable Birthday Pending system
2. Set Birthday Pending role
3. Check protected roles in Role Connections
4. Verify member with Birthday Pending role is skipped by role connections

**Expected Results:**
- ✅ Birthday Pending role in protected roles list
- ✅ Role connections skips users with this role
- ✅ No role connection rules apply to these users

---

### TEST 6: System Toggles
**Goal:** Verify all toggles work

**Steps:**
1. Toggle Welcome System OFF → New members should not get welcome message
2. Toggle Goodbye System OFF → Leaving members should not get goodbye message
3. Toggle Birthday Announcements OFF → No birthday announcements sent
4. Toggle Birthday Pending OFF → New members should not get pending role

**Expected Results:**
- ✅ Each system respects its toggle
- ✅ Disabled systems don't run
- ✅ Enabled systems work normally

---

### TEST 7: Multiple Members
**Goal:** Verify system handles multiple users

**Steps:**
1. Have 3-5 members join
2. All should get Birthday Pending role
3. Have each set their birthday
4. All should have role removed

**Expected Results:**
- ✅ All members get role
- ✅ All members can set birthday
- ✅ All members have role removed
- ✅ No race conditions or errors

---

### TEST 8: Edge Cases

#### 8a: Member Leaves Before Setting Birthday
**Steps:**
1. Member joins → Gets Birthday Pending role
2. Member leaves server
3. Member rejoins

**Expected:**
- ✅ Gets Birthday Pending role again
- ✅ No errors

#### 8b: Birthday Already Set
**Steps:**
1. Member with birthday set joins server
2. Check if they get Birthday Pending role

**Expected:**
- ✅ Should still get role (they can update birthday)
- ✅ Can remove role by re-setting birthday

#### 8c: Invalid Birthday Format
**Steps:**
1. Click birthday button
2. Enter invalid format (e.g., "13-45", "abc", "2024-01-01")

**Expected:**
- ✅ Error message shown
- ✅ Modal doesn't close
- ✅ No database changes

#### 8d: Missing Permissions
**Steps:**
1. Remove bot's "Manage Roles" permission
2. New member joins

**Expected:**
- ✅ Error logged
- ✅ Bot doesn't crash
- ✅ Clear error message

---

### TEST 9: Birthday Announcement Integration
**Goal:** Verify birthday announcements still work

**Steps:**
1. Set a birthday for today
2. Wait for birthday check (or restart bot)
3. Verify announcement sent

**Expected Results:**
- ✅ Birthday announced in birthday channel
- ✅ User mentioned
- ✅ No duplicate announcements
- ✅ Works with Birthday Pending system

---

### TEST 10: Configuration Viewing
**Goal:** Verify all config views work

**Steps:**
1. Run `/setup` → "View Current Config"
2. Check Birthday section
3. Verify all settings displayed

**Expected Results:**
- ✅ All birthday settings shown
- ✅ Birthday Pending settings shown
- ✅ Status indicators correct
- ✅ Role/channel mentions work

---

## Regression Testing

### Existing Features to Verify Still Work:
- [ ] `/bday set` - Manual birthday setting
- [ ] `/bday view` - View birthday
- [ ] `/bday list` - List all birthdays
- [ ] `/bday remove` - Remove birthday
- [ ] Birthday announcements at scheduled time
- [ ] Timezone support
- [ ] Welcome messages
- [ ] Goodbye messages
- [ ] Role connections
- [ ] Onboarding role assignment

---

## Performance Testing

### Load Test:
1. Simulate 50+ members joining
2. Verify all get Birthday Pending role
3. Check for memory leaks
4. Verify no slowdowns

### Database Test:
1. Check query performance
2. Verify indexes work
3. Check for N+1 queries

---

## Error Handling Testing

### Test Error Scenarios:
1. Database connection lost
2. Discord API timeout
3. Missing permissions
4. Invalid role/channel IDs
5. Corrupted settings data

**Expected:**
- ✅ Graceful error handling
- ✅ Clear error messages
- ✅ No crashes
- ✅ Proper logging

---

## Success Criteria

All tests must pass with:
- ✅ No breaking changes to existing features
- ✅ No errors in console
- ✅ All new features working
- ✅ Proper error handling
- ✅ Good performance
- ✅ Clear user feedback

---

## Test Results Log

| Test | Status | Notes | Date |
|------|--------|-------|------|
| TEST 1 | ⏳ Pending | | |
| TEST 2 | ⏳ Pending | | |
| TEST 3 | ⏳ Pending | | |
| TEST 4 | ⏳ Pending | | |
| TEST 5 | ⏳ Pending | | |
| TEST 6 | ⏳ Pending | | |
| TEST 7 | ⏳ Pending | | |
| TEST 8 | ⏳ Pending | | |
| TEST 9 | ⏳ Pending | | |
| TEST 10 | ⏳ Pending | | |

---

## Rollback Plan

If critical issues found:
1. Restore backup files:
   - `cogs/setup.py.backup`
   - `cogs/welcome.py.backup`
   - `cogs/birthdays.py.backup`
2. Restart bot
3. Verify old functionality restored
4. Debug issues in separate branch