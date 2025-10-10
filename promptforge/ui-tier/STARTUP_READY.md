# UI Tier - Ready for Startup

**Date**: 2025-10-05
**Status**: ✅ **READY TO START**

---

## Pre-Flight Checklist

### Backend Services ✅
- [x] PostgreSQL running and healthy (port 5432)
- [x] Redis running and healthy (port 6379)
- [x] API server running and healthy (port 8000)

**Verification**:
```bash
docker-compose ps
curl http://localhost:8000/health
```

### UI Configuration ✅
- [x] All MFE dependencies installed
- [x] Import paths fixed (evaluationService)
- [x] Startup scripts created and executable
- [x] Package.json in correct location (ui-tier/)

### Scripts Available ✅
- [x] `start-all-mfes.sh` - Start all MFE applications
- [x] `stop-all-mfes.sh` - Stop all MFE applications
- [x] `test-integration.sh` - Run integration tests

---

## Quick Start

### Step 1: Verify Backend
```bash
cd /Users/rohitiyer/datagrub/promptforge
docker-compose ps
curl http://localhost:8000/health
```

**Expected Output**:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "version": "2.0.0"
}
```

### Step 2: Start UI
```bash
cd /Users/rohitiyer/datagrub/promptforge/ui-tier
./start-all-mfes.sh
```

**Expected Output**:
```
[INFO]   PromptForge UI - Starting All Micro-Frontends
[SUCCESS] Backend API is healthy
[INFO]   Installing dependencies for all MFEs...
[SUCCESS] shell started (PID: xxxxx)
[SUCCESS] mfe-projects started (PID: xxxxx)
[SUCCESS] mfe-evaluations started (PID: xxxxx)
[SUCCESS] mfe-playground started (PID: xxxxx)
[SUCCESS] mfe-traces started (PID: xxxxx)
[SUCCESS] mfe-policy started (PID: xxxxx)
[SUCCESS] mfe-models started (PID: xxxxx)

All MFE applications started successfully!

Application URLs:
  - Shell (Main App):    http://localhost:3000
  - Projects MFE:        http://localhost:3001
  - Evaluations MFE:     http://localhost:3002
  - Playground MFE:      http://localhost:3003
  - Traces MFE:          http://localhost:3004
  - Policy MFE:          http://localhost:3005
  - Models MFE:          http://localhost:3006
```

### Step 3: Access Application
Open browser and navigate to:
- **Main Application**: http://localhost:3000
- **Evaluations (standalone)**: http://localhost:3002

### Step 4: Verify Evaluations API Integration
1. Open http://localhost:3000
2. Navigate to Evaluations page
3. Check browser DevTools → Network tab
4. Verify:
   - ✅ Loading spinner appears briefly
   - ✅ API call to `/api/v1/evaluations`
   - ✅ Data loaded from backend (no "Mock Data" label)
   - ✅ Table shows evaluation data

---

## Troubleshooting

### Issue 1: Module Not Found Error

**Error**:
```
ERROR in ./src/App.tsx
Module not found: Error: Can't resolve '../../../shared/services/evaluationService'
```

**Status**: ✅ **FIXED**
**Solution**: Import path corrected from `../../../` to `../../`
**Reference**: See `IMPORT_PATH_FIX.md` for details

### Issue 2: Port Already in Use

**Error**:
```
Error: listen EADDRINUSE: address already in use :::3000
```

**Solution**:
```bash
# Stop all MFEs
./stop-all-mfes.sh

# Or kill specific port
lsof -ti:3000 | xargs kill -9
```

### Issue 3: API Not Responding

**Symptom**: Yellow warning banner, "(Mock Data)" label visible

**Check**:
```bash
curl http://localhost:8000/health
```

**Solution**:
```bash
cd /Users/rohitiyer/datagrub/promptforge
docker-compose up -d
```

### Issue 4: Dependency Issues

**Error**:
```
Module not found: Error: Can't resolve 'react'
```

**Solution**:
```bash
cd ui-tier/mfe-evaluations
rm -rf node_modules package-lock.json
npm install
```

---

## Log Files

All MFE logs are stored in `ui-tier/logs/`:

```bash
# View all logs
ls ui-tier/logs/

# View specific MFE log
tail -f ui-tier/logs/mfe-evaluations.log

# View only errors
grep -i error ui-tier/logs/*.log

# View last 50 lines of all logs
tail -50 ui-tier/logs/*.log
```

---

## Testing

### Integration Test
```bash
cd ui-tier
./test-integration.sh
```

### Manual Test Checklist
- [ ] All 7 MFEs start without errors
- [ ] Shell accessible at http://localhost:3000
- [ ] Evaluations accessible at http://localhost:3002
- [ ] API integration working (no mock data)
- [ ] Authentication flow works
- [ ] Token refresh works
- [ ] Module Federation loads remote entries

---

## Next Steps After Startup

1. **Login to Application**:
   - Navigate to http://localhost:3000/login
   - Use test credentials (Oiiro user)

2. **Test Evaluations Page**:
   - Navigate to Evaluations
   - Verify data loads from API
   - Check Network tab for API calls

3. **Test Model Provider Config**:
   - Once UI is created, test API key management

4. **Run Full Integration Tests**:
   - Test all MFE components
   - Verify Module Federation
   - Test authentication flow

---

## Current Status

| Component | Status | Port | Notes |
|-----------|--------|------|-------|
| Backend API | ✅ Running | 8000 | Healthy |
| PostgreSQL | ✅ Running | 5432 | Healthy |
| Redis | ✅ Running | 6379 | Healthy |
| Shell | 🟡 Ready | 3000 | Start with script |
| Projects | 🟡 Ready | 3001 | Start with script |
| Evaluations | ✅ Updated | 3002 | API integration ready |
| Playground | 🟡 Ready | 3003 | Start with script |
| Traces | 🟡 Ready | 3004 | Start with script |
| Policy | 🟡 Ready | 3005 | Start with script |
| Models | 🟡 Ready | 3006 | Start with script |

Legend:
- ✅ Running/Updated: Service is active or component has API integration
- 🟡 Ready: Can be started with startup script

---

## Documentation

- `UI_DEPLOYMENT_GUIDE.md` - Comprehensive deployment guide
- `UI_DEPLOYMENT_COMPLETION.md` - Deployment completion summary
- `UI_INTEGRATION_VALIDATION.md` - Integration validation report
- `IMPORT_PATH_FIX.md` - Import path fix documentation
- `SCRIPT_CLEANUP_SUMMARY.md` - Script cleanup summary
- `STARTUP_READY.md` - This file

---

**Prepared by**: Claude Code
**Date**: 2025-10-05
**Status**: ✅ **READY FOR STARTUP**

---

## Commands Summary

```bash
# Start everything
cd ui-tier && ./start-all-mfes.sh

# Stop everything
cd ui-tier && ./stop-all-mfes.sh

# Test integration
cd ui-tier && ./test-integration.sh

# View logs
tail -f ui-tier/logs/mfe-evaluations.log

# Check backend health
curl http://localhost:8000/health

# Access UI
open http://localhost:3000
```

**You are now ready to start the UI! 🚀**
