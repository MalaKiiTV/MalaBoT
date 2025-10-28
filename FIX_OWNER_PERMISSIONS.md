# 🚨 URGENT: Fix Owner Permissions

## Problem
The bot doesn't recognize you as the owner because `OWNER_IDS` is not set in your `.env` file.

## Solution

### Step 1: Get Your Discord User ID
1. Open Discord
2. Go to Settings → Advanced
3. Enable "Developer Mode"
4. Right-click your username
5. Click "Copy User ID"
6. Save this number (it's your Discord user ID)

### Step 2: Add Your ID to .env File
1. Open your MalaBoT folder on your computer
2. Find the `.env` file (if it doesn't exist, create it)
3. Add this line (replace with YOUR user ID):
```
OWNER_IDS=YOUR_DISCORD_USER_ID_HERE
```

Example:
```
DISCORD_TOKEN=your_bot_token_here
OWNER_IDS=123456789012345678
DEBUG_GUILDS=542004156513255445
```

### Step 3: Restart Bot
1. Stop bot (dev.bat Option 2)
2. Start bot (dev.bat Option 1)

## Multiple Owners (Optional)
If you want multiple owners, separate IDs with commas:
```
OWNER_IDS=123456789012345678,987654321098765432
```

## Verify It Works
After restarting, try any command. You should now have access.

## What Went Wrong
The bot was updated to use owner-only permissions, but your .env file didn't have OWNER_IDS configured. This is a one-time setup issue.

## Important Notes
- OWNER_IDS is for YOU (the bot developer)
- This is separate from server admins
- Server admins will NOT see /owner commands
- Only people in OWNER_IDS can use owner commands
- Mod role settings only apply to /verify and /appeal commands