# Setup System & Cheater Jail Guide

## 🎯 Overview

This guide covers all the new features added to MalaBoT:
- Complete `/setup` system overhaul
- Staff role permissions
- Cheater jail system (replaces bans)
- Appeal system

---

## 📋 /setup Command - Complete Configuration

### 1. Verification System

**What it configures:**
- ✅ Review Channel - Where staff sees verification submissions
- ✅ Verified Role - Role assigned when user is verified
- ✅ Staff Role - Who can review verifications (NEW!)
- ✅ Cheater Role - Role assigned to cheaters (NEW!)
- ✅ Cheater Jail Channel - Where cheaters are isolated (NEW!)

**How to use:**
1. Run `/setup`
2. Select "Verification System" from dropdown
3. Use the dropdowns to select:
   - Review channel (text channel)
   - Verified role
   - Staff role (who can use `/verify review`)
   - Cheater role
   - Cheater jail channel
4. Click "View Current Config" to see settings

**User Workflow:**
1. User runs `/verify submit`
2. Enters Activision ID in modal
3. Uploads screenshot in next message
4. Selects platform from dropdown
5. Staff reviews with `/verify review @user <decision>`

**Review Decisions:**
- **Verified** - Assigns verified role
- **Cheater** - Sends to cheater jail (see below)
- **Unverified** - Leaves user unverified

---

### 2. Birthday System (NEW FEATURES!)

**What it configures:**
- 🎂 Birthday Channel - Where announcements are posted
- 🎂 Birthday Role - Role given on user's birthday
- 🎂 Announcement Time - What time to post (24-hour format)

**How to use:**
1. Run `/setup`
2. Select "Birthday System" from dropdown
3. Use the dropdowns to select:
   - Birthday announcement channel
   - Birthday role (given on user's birthday)
   - Announcement time (00:00 to 23:00)
4. **Note:** Timezone must be configured in General Settings first!

**User Commands:**
- `/bday set <MM-DD>` - Set your birthday
- `/bday view [@user]` - View a birthday
- `/bday list` - View all birthdays
- `/bday next` - See next upcoming birthday

---

### 3. XP System (NEW FEATURES!)

**What it configures:**
- 🏆 XP per Message
- 🏆 XP per Minute in Voice Chat
- 🏆 XP per Reaction Received
- 🏆 XP per Command Used
- 🏆 Daily Bonus XP

**How to use:**
1. Run `/setup`
2. Select "XP System" from dropdown
3. Click "Configure XP Amounts" button
4. Fill in the modal with your desired XP values
5. Click "View Current Config" to see settings

**Default Values:**
- Messages: 10 XP
- Voice: 5 XP per minute
- Reactions: 2 XP
- Commands: 3 XP
- Daily Bonus: 50 XP

---

### 4. General Settings (FIXED!)

**What it configures:**
- 🌍 Timezone - Dropdown with 25 common timezones (FIXED!)
- 💬 Online Message Channel - Where bot posts when coming online (NEW!)
- 💬 Online Message Text - Message sent when bot comes online

**How to use:**
1. Run `/setup`
2. Select "General Settings" from dropdown
3. Use the timezone dropdown to select your timezone
4. Use the channel dropdown to select where online messages go
5. Click "Set Online Message Text" to set the message

**Available Timezones:**
- UTC-12 to UTC+12 (all major timezones)
- Includes: Pacific, Mountain, Central, Eastern, London, Paris, Tokyo, etc.

---

## 🔒 Cheater Jail System

### What is Cheater Jail?

Instead of banning cheaters, they are:
1. Assigned a "Cheater" role
2. All other roles removed
3. Sent to an isolated "Cheater Jail" channel
4. Can ONLY see the jail channel
5. Can submit ONE appeal

### How to Set Up Cheater Jail

**1. Create the Cheater Role:**
- Create a new role (e.g., "Cheater")
- Set color to red or another warning color
- Don't assign any permissions yet

**2. Create the Cheater Jail Channel:**
- Create a new text channel (e.g., "cheater-jail")
- Set permissions:
  - `@everyone`: ❌ Cannot view channel
  - `Cheater Role`: ✅ Can view and send messages
  - `Staff Role`: ✅ Can view and manage

**3. Configure All Other Channels:**
- For EVERY other channel in your server:
  - Add permission override for `Cheater Role`
  - Set "View Channel" to ❌ (deny)

**4. Configure in /setup:**
- Run `/setup` → Verification System
- Select the Cheater role
- Select the Cheater Jail channel

### When Someone is Marked as Cheater

**What happens automatically:**
1. All roles removed (except @everyone)
2. Cheater role assigned
3. User can only see cheater jail channel
4. Notification sent to jail channel
5. User can submit ONE appeal

**Staff sees:**
- Log in review channel
- Audit log entry
- User appears in cheater jail

---

## 📝 Appeal System

### For Cheaters (Users)

**How to Submit an Appeal:**
1. Go to the cheater jail channel
2. Run `/appeal submit`
3. Fill out the modal with your appeal
4. Wait for staff review

**Important:**
- ⚠️ You can only submit ONE appeal
- ⚠️ Appeals can only be submitted in the jail channel
- ⚠️ You must have the cheater role to appeal

### For Staff

**How to Review Appeals:**
1. Staff gets notified in review channel when appeal is submitted
2. Run `/appeal review @user <approve/deny> [reason]`
3. Choose:
   - **Approve** - Removes cheater role, user regains access
   - **Deny** - User stays in jail permanently

**Requirements:**
- Must have the configured staff role
- Or have "Manage Roles" permission

---

## 🛡️ Staff Role System

### What is the Staff Role?

The staff role determines who can:
- Review verifications (`/verify review`)
- Review appeals (`/appeal review`)

### How to Configure:

1. Run `/setup` → Verification System
2. Use the "Staff Role" dropdown
3. Select the role that should have review permissions

### Fallback Behavior:

If no staff role is configured:
- Falls back to "Manage Roles" permission
- Anyone with that permission can review

---

## 🔍 Verification Workflow (Complete)

### User Side:
1. Run `/verify submit`
2. Modal opens - enter Activision ID
3. Upload screenshot in next message
4. Select platform from dropdown
5. Wait for staff review

### Staff Side:
1. Submission appears in review channel
2. Staff runs `/verify review @user <decision> [notes]`
3. Decisions:
   - **Verified**: Assigns verified role
   - **Cheater**: Sends to jail, assigns cheater role
   - **Unverified**: No action taken

### Permissions:
- Staff must have configured staff role
- Or "Manage Roles" permission

---

## 📊 View Current Configuration

**To see all settings:**
1. Run `/setup`
2. Select "View Current Config" from dropdown
3. See all configured settings for:
   - Verification (including staff role, cheater jail)
   - Welcome
   - Birthday
   - XP
   - General

---

## ⚠️ Important Notes

### Channel Permissions for Cheater Jail:

**This is CRITICAL for the system to work:**

1. **Cheater Jail Channel:**
   - @everyone: ❌ View Channel
   - Cheater Role: ✅ View Channel, ✅ Send Messages
   - Staff Role: ✅ View Channel, ✅ Manage Messages

2. **ALL Other Channels:**
   - Add permission override for Cheater Role
   - Set "View Channel" to ❌ (red X)

### Testing the System:

1. Set up all roles and channels first
2. Configure everything in `/setup`
3. Test with a test account:
   - Submit verification
   - Mark as cheater
   - Verify isolation works
   - Test appeal system

### Troubleshooting:

**Cheaters can see other channels:**
- Check permission overrides on ALL channels
- Cheater role must have "View Channel" denied

**Staff can't review:**
- Check staff role is configured in `/setup`
- Verify staff members have the role

**Appeals not working:**
- Verify user is in cheater jail channel
- Check user has cheater role
- Confirm user hasn't already appealed

---

## 🎉 Summary of Changes

### What's Fixed:
✅ Timezone is now a dropdown (25 options)
✅ Online message has channel selector
✅ XP system fully configurable
✅ Birthday system fully configurable
✅ Staff role system implemented

### What's New:
🆕 Cheater jail system (replaces bans)
🆕 Appeal system (one-time appeals)
🆕 Staff role permissions
🆕 Complete /setup overhaul

### What's Better:
⭐ All dropdowns where appropriate
⭐ No unnecessary text inputs
⭐ Better permission system
⭐ More humane cheater handling
⭐ Appeal process for mistakes

---

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Verify all permissions are set correctly
3. Check the review channel for error messages
4. Review the audit logs

**Common Issues:**
- Cheaters seeing other channels = Permission overrides not set
- Staff can't review = Staff role not configured or assigned
- Appeals not working = User not in jail channel or already appealed