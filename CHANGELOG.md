# MalaBoT Changelog

## [Unreleased] - 2025-01-27

### Fixed
- **DatabaseManager**: Added missing `get_leaderboard()` method for XP leaderboard functionality
- **DatabaseManager**: Added missing `set_daily_claimed()` method for daily reward tracking
- **DatabaseManager**: Fixed `log_event()` parameter name from `target_user_id` to `target_id`
- **SystemHelper**: Added missing `sanitize_input()` method for input validation
- **CooldownHelper**: Added missing `check_cooldown()` method for command cooldown management
- **EmbedHelper**: Enhanced `create_embed()` to support optional `description` and `thumbnail` parameters
- **Moderation Cog**: Fixed all `log_event()` calls to use correct `target_id` parameter
- **Utility Cog**: Fixed embed creation calls to include required parameters

### Commands Fixed
- `/daily` - Daily XP rewards now work correctly
- `/leaderboard` - XP leaderboard now displays properly
- `/joke`, `/fact`, `/roast` - Cooldown system now functions
- `/8ball` - Input sanitization now works
- `/ban`, `/mute`, `/unmute` - Moderation logging now works
- `/userinfo`, `/serverinfo` - Thumbnails now display correctly
- `/serverstats` - Embed creation now works

### Technical Details
- All helper methods are now properly implemented
- Database methods support async operations
- Cooldown system automatically manages command usage
- Input sanitization prevents control character issues
- Embed creation supports flexible parameters

---

## Previous Updates

See commit history for earlier changes.