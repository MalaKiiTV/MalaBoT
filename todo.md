# Fix /verify and Create Unified Setup System

## Issues Identified
[x] /verify config command not showing up
[x] 'Interaction' object has no attribute 'attachments' error still occurring
[x] Disorganized setup - need unified configuration system
[x] Failed webhook messages

## Analysis
[x] Check why /verify config not syncing - Command exists, may be sync issue
[x] Review interaction.attachments error source - Need to check on_message listener
[x] Design unified setup system for all bot features
[x] Check webhook configuration issues

## Implementation
[x] Fix /verify config command registration - Fixed group naming
[x] Create /setup command with comprehensive configuration
[x] Add setup for: timezone, channels, roles, welcome, birthday, verification
[x] Implement proper error handling
[x] Create missing cleanup.py and clear_and_sync.py scripts
[ ] Test all setup flows

## Push & Test
[ ] Commit and push fixes
[ ] Remove unnecessary files
[ ] Instruct user on testing