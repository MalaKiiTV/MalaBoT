# Role Connection System - Complete Guide

## 🎯 Overview

The Role Connection System allows you to automatically assign or remove roles based on conditions. This replaces external bots like Saphire and gives you full control over automatic role management.

## ✨ Key Features

- ✅ **Automatic Role Management** - Give or remove roles based on conditions
- ✅ **Flexible Conditions** - User HAS or DOESN'T HAVE specific roles
- ✅ **AND/OR Logic** - Combine multiple conditions
- ✅ **Protected Roles** - Exempt specific roles from all rules
- ✅ **Real-time Processing** - Event-based + periodic checks every 5 minutes
- ✅ **Easy Management** - All through `/setup` command
- ✅ **Server-Specific** - Each server has its own independent rules
- ✅ **No Hardcoding** - Fully configurable, works with any role names

## 🚀 Getting Started

### Step 1: Access the System

```
/setup → Select "Role Connections"
```

You'll see the main Role Connection menu with options:
- **Add Connection** - Create a new rule
- **Manage Connections** - View, toggle, or delete existing rules
- **Protected Roles** - Manage roles exempt from rules
- **Back to Setup** - Return to main setup menu

### Step 2: Set Up Protected Roles (Recommended First)

Protected roles are exempt from ALL role connection rules. This is perfect for:
- Cheater role
- Timeout role
- Banned role
- Any role that should override normal rules

**How to add:**
1. Click "Protected Roles"
2. Click "Add Protected Role"
3. Select the role
4. Done! Users with this role won't have connections applied

### Step 3: Create Your First Connection

**Example: Give "Sus" role when user doesn't have "Mala" role**

1. Click "Add Connection"
2. **Step 1:** Select target role → Choose "Sus"
3. **Step 2:** Select action → Click "Give Role"
4. **Step 3:** Add condition → Select "User DOESN'T HAVE role"
5. **Step 4:** Select condition role → Choose "Mala"
6. **Step 5:** Click "Save Connection"

Done! Now anyone without the "Mala" role will automatically get "Sus".

## 📋 Example Configurations

### Example 1: Sus Role (From Your Saphire Setup)
**Rule:** Give "Sus (Unranked)" when user doesn't have "Mala"

**Setup:**
- Target Role: Sus (Unranked)
- Action: Give
- Condition: User DOESN'T HAVE Mala
- Logic: (single condition, no logic needed)

### Example 2: SnackPack Role (From Your Saphire Setup)
**Rule:** Give "SnackPack" when user has BOTH "TikTok Sub" AND "Discord Sub"

**Setup:**
- Target Role: SnackPack
- Action: Give
- Condition 1: User HAS TikTok Sub
- Condition 2: User HAS Discord Sub
- Logic: AND

### Example 3: Mala Role (From Your Saphire Setup)
**Rule:** Give "Mala" when user has "Noob Lvl 1-9" AND "Bot" AND "cr-fan-M10"

**Setup:**
- Target Role: Mala
- Action: Give
- Condition 1: User HAS Noob Lvl 1-9
- Condition 2: User HAS Bot
- Condition 3: User HAS cr-fan-M10
- Logic: AND

### Example 4: Remove Guest Role
**Rule:** Remove "Guest" when user has "Member"

**Setup:**
- Target Role: Guest
- Action: Remove
- Condition: User HAS Member
- Logic: (single condition)

## 🔧 Managing Connections

### View All Connections
1. Go to Role Connections menu
2. Click "Manage Connections"
3. See list of all active connections with their conditions

### Toggle Connection On/Off
1. Click "Manage Connections"
2. Select the connection
3. Click "Toggle On/Off"
4. Connection is now enabled/disabled

### Delete Connection
1. Click "Manage Connections"
2. Select the connection
3. Click "Delete"
4. Confirm deletion

## 🛡️ Protected Roles System

### Why Use Protected Roles?

Protected roles prevent conflicts and ensure certain roles override normal rules. For example:
- User gets "Cheater" role
- Normally, they'd get "Sus" because they don't have "Mala"
- But "Cheater" is protected, so NO connections apply
- User keeps ONLY "Cheater" role

### Managing Protected Roles

**Add Protected Role:**
1. Role Connections menu → "Protected Roles"
2. Click "Add Protected Role"
3. Select role
4. Done!

**Remove Protected Role:**
1. Role Connections menu → "Protected Roles"
2. Click "Remove Protected Role"
3. Select role to unprotect
4. Done!

## ⚙️ How It Works

### Processing Logic

1. **Event-Based:** When a user's roles change, connections are checked immediately
2. **Periodic Scan:** Every 5 minutes, all members are checked
3. **Protected Check:** If user has protected role, skip all connections
4. **Condition Check:** For each enabled connection, check if conditions are met
5. **Action:** Give or remove target role based on conditions

### Condition Evaluation

**AND Logic:**
- ALL conditions must be true
- Example: User HAS Role A AND User HAS Role B
- Both must be true for action to trigger

**OR Logic:**
- ANY condition can be true
- Example: User HAS Role A OR User HAS Role B
- Either one being true triggers action

### Role Removal

When using "Give" action:
- If conditions are met → Give role
- If conditions are NO LONGER met → Remove role automatically

This ensures roles stay synchronized with conditions.

## 🔄 Migration from Saphire

### Step-by-Step Migration

1. **Set up protected roles first**
   - Add your "Cheater" role as protected
   - Add any other special roles

2. **Recreate your Saphire rules**
   - Use the examples above as templates
   - Test each rule individually

3. **Test thoroughly**
   - Assign roles manually to test users
   - Verify connections trigger correctly
   - Check protected roles work

4. **Disable Saphire**
   - Once everything works, disable Saphire bot
   - Remove Saphire from your server

### Advantages Over Saphire

✅ **Integrated** - All in one bot, one command
✅ **Faster** - No external bot communication
✅ **Smarter** - Knows about your other bot features
✅ **No Conflicts** - Single source of truth
✅ **More Control** - Full customization
✅ **Better Logging** - See exactly what happens

## 🐛 Troubleshooting

### Connection Not Working

**Check:**
1. Is the connection enabled? (✅ in manage menu)
2. Does the bot have permission to manage roles?
3. Is the bot's role higher than target role in hierarchy?
4. Are conditions set up correctly?
5. Is the user protected by a protected role?

### Role Not Being Removed

**Possible causes:**
1. Connection is set to "Remove" instead of "Give"
2. Conditions are still being met
3. User has protected role
4. Bot lacks permissions

### Multiple Bots Fighting

**Solution:**
- Only run ONE role management system at a time
- Either use MalaBoT's system OR Saphire, not both
- Disable Saphire once MalaBoT is working

## 📊 Performance

- **Event-based processing:** Instant (< 1 second)
- **Periodic scan:** Every 5 minutes
- **Impact:** Minimal - only processes when roles change
- **Scalability:** Handles thousands of members efficiently

## 🔐 Permissions Required

The bot needs:
- **Manage Roles** permission
- Bot's role must be **higher** than roles it manages
- Access to view member roles

## 💡 Best Practices

1. **Start Simple**
   - Create one connection at a time
   - Test before adding more

2. **Use Protected Roles**
   - Always protect special roles (cheater, timeout, etc.)
   - Prevents unexpected behavior

3. **Logical Conditions**
   - Keep conditions clear and simple
   - Document complex rules

4. **Regular Audits**
   - Review connections periodically
   - Remove unused rules

5. **Test Changes**
   - Test with a test user before applying to everyone
   - Verify conditions work as expected

## 📝 Examples for Common Use Cases

### Subscriber Tiers
```
Connection 1: Give "Bronze Tier" when user HAS "1 Month Sub"
Connection 2: Give "Silver Tier" when user HAS "3 Month Sub"
Connection 3: Give "Gold Tier" when user HAS "6 Month Sub"
```

### Activity Levels
```
Connection 1: Give "Active" when user HAS "Level 10+"
Connection 2: Remove "Inactive" when user HAS "Active"
```

### Verification Status
```
Connection 1: Give "Unverified" when user DOESN'T HAVE "Verified"
Connection 2: Remove "Unverified" when user HAS "Verified"
```

### Platform Supporters
```
Connection 1: Give "Supporter" when user HAS "Twitch Sub" OR "YouTube Member"
```

## 🆘 Support

If you encounter issues:
1. Check bot logs for error messages
2. Verify bot permissions
3. Test with a single simple connection first
4. Review this guide for common issues

## 🎉 You're Ready!

The Role Connection System is now fully set up and ready to use. Start by:
1. Setting up protected roles
2. Creating your first simple connection
3. Testing it works
4. Adding more complex rules as needed

Enjoy automated role management! 🚀