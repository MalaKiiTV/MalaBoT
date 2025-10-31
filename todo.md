# Fix Database Lock and Signal Handler Issues

## Problem Analysis
- Database lock errors on droplet startup
- Signal handler has event loop issues (RuntimeError: no running event loop)
- Bot crashes during initialization due to database being locked

## Tasks

### 1. Fix Signal Handler ✅
- [x] Update signal handler to properly handle event loop
- [x] Ensure shutdown is called correctly without event loop errors
- [x] Added try-catch for RuntimeError when no event loop exists

### 2. Add Database Connection Cleanup ✅
- [x] Ensure all database connections are closed on shutdown
- [x] Added proper cleanup in shutdown method
- [x] Reordered shutdown sequence: log event → close scheduler → close Discord → close database
- [x] Added commit before closing database connection
- [x] Added error handling for each shutdown step

### 3. Testing
- [ ] Verify bot starts without database lock errors
- [ ] Test graceful shutdown (Ctrl+C)
- [ ] Verify no event loop errors in logs

### 4. Deployment
- [ ] Commit changes with clear message
- [ ] Push to GitHub
- [ ] User pulls and deploys via dev.bat workflow