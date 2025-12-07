# Birthday Announcement System Improvements

## Overview
Enhance the birthday announcement system to prevent duplicate announcements and track which birthdays have been announced each year.

## Tasks

### 1. Database Schema Updates
- [x] User added `announced_year` column to birthdays table
- [x] Add `mark_birthday_announced` method to DatabaseManager
- [x] Add `get_unannounced_birthdays` method to DatabaseManager

### 2. Birthday Check Logic Updates
- [x] Update birthday check task in cogs/birthdays.py to use new methods
- [x] Implement year tracking to prevent duplicate announcements
- [x] Logging already exists for birthday announcements

### 3. Testing & Verification
- [ ] Test the new system
- [ ] Create documentation for the changes
- [ ] Commit and push changes
- [ ] Create pull request

## Notes
- The system should only announce each birthday once per year
- Must handle timezone correctly (already implemented)
- Should log all birthday announcements for audit purposes