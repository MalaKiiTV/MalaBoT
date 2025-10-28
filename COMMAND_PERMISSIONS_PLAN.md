# Command Permissions Plan

## 🎯 Permission Levels

1. **PUBLIC** - Anyone can use
2. **STAFF** - Requires staff role (configurable)
3. **ADMIN** - Requires administrator permission
4. **OWNER** - Bot owner only

---

## 📋 Command Audit & Recommendations

### ✅ appeal.py
| Command | Current | Recommended | Reason |
|---------|---------|-------------|--------|
| `/appeal submit` | PUBLIC | PUBLIC | Users in jail need to appeal |
| `/appeal review` | PUBLIC | **STAFF** | Only staff should review appeals |

**Action:** Add staff role check to `/appeal review`

---

### ✅ birthdays.py
| Command | Current | Recommended | Reason |
|---------|---------|-------------|--------|
| `/bday` (all subcommands) | PUBLIC | PUBLIC | Users manage their own birthdays |

**Action:** No changes needed

---

### ✅ fun.py
| Command | Current | Recommended | Reason |
|---------|---------|-------------|--------|
| `/joke` | PUBLIC | PUBLIC | Fun command for everyone |
| `/fact` | PUBLIC | PUBLIC | Fun command for everyone |
| `/roast` | PUBLIC | PUBLIC | Fun command for everyone |
| `/8ball` | PUBLIC | PUBLIC | Fun command for everyone |
| `/roll` | PUBLIC | PUBLIC | Fun command for everyone |
| `/coinflip` | PUBLIC | PUBLIC | Fun command for everyone |

**Action:** No changes needed

---

### ⚠️ moderation.py
| Command | Current | Recommended | Reason |
|---------|---------|-------------|--------|
| `/delete` | PUBLIC | **STAFF** | Should require staff role |
| `/kick` | PUBLIC | **STAFF** | Should require staff role |
| `/ban` | PUBLIC | **STAFF** | Should require staff role |
| `/mute` | PUBLIC | **STAFF** | Should require staff role |
| `/unmute` | PUBLIC | **STAFF** | Should require staff role |

**Action:** Add staff role checks to ALL moderation commands

---

### ✅ owner.py
| Command | Current | Recommended | Reason |
|---------|---------|-------------|--------|
| `/owner` | PUBLIC | **OWNER** | Already has owner check in code |

**Action:** Verify owner check is working

---

### ✅ setup.py
| Command | Current | Recommended | Reason |
|---------|---------|-------------|--------|
| `/setup` | ADMIN | ADMIN | Correct - admins configure bot |

**Action:** No changes needed

---

### ✅ utility.py
| Command | Current | Recommended | Reason |
|---------|---------|-------------|--------|
| `/help` | PUBLIC | PUBLIC | Everyone needs help |
| `/ping` | PUBLIC | PUBLIC | Useful for everyone |
| `/userinfo` | PUBLIC | PUBLIC | Useful for everyone |
| `/serverinfo` | PUBLIC | PUBLIC | Useful for everyone |
| `/about` | PUBLIC | PUBLIC | Bot information |
| `/serverstats` | PUBLIC | PUBLIC | Server information |

**Action:** No changes needed

---

### ⚠️ verify.py
| Command | Current | Recommended | Reason |
|---------|---------|-------------|--------|
| `/verify activision` | PUBLIC | PUBLIC | Users submit their verification |
| `/verify review` | PUBLIC | **STAFF** | Already has staff check! ✅ |

**Action:** Verify staff check is working properly

---

### ⚠️ welcome.py
| Command | Current | Recommended | Reason |
|---------|---------|-------------|--------|
| `/welcome` | PUBLIC | ADMIN | Should require admin |

**Action:** Add admin permission check

---

### ⚠️ xp.py
| Command | Current | Recommended | Reason |
|---------|---------|-------------|--------|
| `/rank` | PUBLIC | PUBLIC | Users check their rank |
| `/leaderboard` | PUBLIC | PUBLIC | Everyone can view |
| `/daily` | PUBLIC | PUBLIC | Users claim daily bonus |
| `/xpadd` | PUBLIC | **STAFF** | Should require staff role |
| `/xpremove` | PUBLIC | **STAFF** | Should require staff role |
| `/xpset` | PUBLIC | **STAFF** | Should require staff role |
| `/xpreset` | PUBLIC | **STAFF** | Should require staff role |
| `/xpconfig` | PUBLIC | ADMIN | Should require admin |

**Action:** Add staff role checks to XP admin commands

---

## 🔧 Implementation Plan

### Phase 1: Add Staff Role to General Settings
- Add staff role selector to `/setup` → General Settings
- Store as `staff_role_{guild_id}` in database
- Make it globally accessible for all cogs

### Phase 2: Update Commands with Staff Checks
1. **appeal.py** - `/appeal review`
2. **moderation.py** - ALL commands
3. **xp.py** - `/xpadd`, `/xpremove`, `/xpset`, `/xpreset`

### Phase 3: Update Commands with Admin Checks
1. **welcome.py** - `/welcome`
2. **xp.py** - `/xpconfig`

### Phase 4: Create Helper Function
Create a reusable permission checker:
```python
async def check_staff_role(interaction: discord.Interaction, db_manager) -> bool:
    """Check if user has staff role or admin permissions"""
    # Check admin first (admins bypass staff role)
    if interaction.user.guild_permissions.administrator:
        return True
    
    # Check staff role
    guild_id = interaction.guild.id
    staff_role_id = await db_manager.get_setting(f"staff_role_{guild_id}")
    
    if staff_role_id:
        staff_role = interaction.guild.get_role(int(staff_role_id))
        if staff_role and staff_role in interaction.user.roles:
            return True
    
    return False
```

---

## 📊 Summary

**Commands Needing Updates:**
- ✅ `/verify activision` - Already renamed
- ⚠️ `/appeal review` - Add staff check
- ⚠️ `/delete`, `/kick`, `/ban`, `/mute`, `/unmute` - Add staff checks
- ⚠️ `/xpadd`, `/xpremove`, `/xpset`, `/xpreset` - Add staff checks
- ⚠️ `/welcome` - Add admin check
- ⚠️ `/xpconfig` - Add admin check

**Total Commands to Update:** 12 commands across 5 cogs