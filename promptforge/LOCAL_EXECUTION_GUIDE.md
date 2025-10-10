# PromptForge - Local Execution Guide

**Complete Step-by-Step Instructions for Running PromptForge Locally**

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (Automated)](#quick-start-automated)
3. [Manual Step-by-Step Setup](#manual-step-by-step-setup)
4. [Port Configuration Reference](#port-configuration-reference)
5. [Validation & Testing](#validation--testing)
6. [Common Issues & Solutions](#common-issues--solutions)
7. [Development Workflow](#development-workflow)

---

## Prerequisites

### Required Software

**1. Node.js (18.x or later)**
```bash
# Check version
node -v
# Expected: v18.x.x or later

# If not installed, download from:
# https://nodejs.org/
```

**2. npm (9.x or later)**
```bash
# Check version
npm -v
# Expected: 9.x.x or later

# npm comes with Node.js
```

**3. Git (Latest)**
```bash
# Check version
git --version
# Expected: git version 2.x.x or later
```

### System Requirements

- **OS:** macOS, Windows, or Linux
- **RAM:** 8GB minimum, 16GB recommended
- **Disk Space:** 2GB free
- **Available Ports:** 3000-3006 (7 ports total)

### Optional Tools

- **VS Code** with extensions:
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense
- **Concurrently** (installed via npm automatically)

---

## Quick Start (Automated)

### Method 1: Using Quick Start Script

```bash
# Navigate to project directory
cd /Users/rohitiyer/datagrub/promptforge

# Run automated setup
./quick-start.sh
```

This script will:
1. ✅ Check Node.js and npm versions
2. ✅ Install all dependencies (7 applications)
3. ✅ Provide next steps

**Then start all services:**
```bash
npm run start:all
```

**Access the application:**
```
http://localhost:3000
```

---

## Manual Step-by-Step Setup

### Step 1: Navigate to Project Directory

```bash
cd /Users/rohitiyer/datagrub/promptforge
```

**Verify you're in the correct directory:**
```bash
ls -la
# Should see: shell/, mfe-projects/, mfe-evaluations/, etc.
```

---

### Step 2: Install Dependencies

#### Option A: Install All at Once (Recommended)

```bash
npm run install:all
```

**What this does:**
- Installs root dependencies
- Installs shell dependencies
- Installs dependencies for all 6 MFEs
- Takes 3-5 minutes depending on network speed

**Expected Output:**
```
Installing dependencies for shell...
Installing dependencies for mfe-projects...
Installing dependencies for mfe-evaluations...
Installing dependencies for mfe-playground...
Installing dependencies for mfe-traces...
Installing dependencies for mfe-policy...
Installing dependencies for mfe-models...
✓ All dependencies installed successfully
```

#### Option B: Install Individually

If you prefer to install dependencies one by one:

```bash
# Root dependencies
npm install

# Shell application
cd shell && npm install && cd ..

# Projects MFE
cd mfe-projects && npm install && cd ..

# Evaluations MFE
cd mfe-evaluations && npm install && cd ..

# Playground MFE
cd mfe-playground && npm install && cd ..

# Traces MFE
cd mfe-traces && npm install && cd ..

# Policy MFE
cd mfe-policy && npm install && cd ..

# Models MFE
cd mfe-models && npm install && cd ..
```

---

### Step 3: Verify Installation

**Check that node_modules exist:**
```bash
ls -d */node_modules
```

**Expected output:**
```
shell/node_modules
mfe-projects/node_modules
mfe-evaluations/node_modules
mfe-playground/node_modules
mfe-traces/node_modules
mfe-policy/node_modules
mfe-models/node_modules
```

**Total size should be ~500MB - 1GB**

---

### Step 4: Start Development Servers

#### Method A: Start All Services Concurrently (Recommended)

```bash
npm run start:all
```

**What this does:**
- Starts all 7 webpack dev servers simultaneously
- Uses `concurrently` package
- Shows combined output from all services
- Single terminal window

**Expected Output:**
```
[shell] webpack 5.89.0 compiled successfully
[projects] webpack 5.89.0 compiled successfully
[evaluations] webpack 5.89.0 compiled successfully
[playground] webpack 5.89.0 compiled successfully
[traces] webpack 5.89.0 compiled successfully
[policy] webpack 5.89.0 compiled successfully
[models] webpack 5.89.0 compiled successfully
```

**Time to start:** 15-30 seconds for all services

#### Method B: Start Services Individually

**Use separate terminal windows/tabs:**

**Terminal 1 - Shell (Required)**
```bash
npm run start:shell
# Starts on http://localhost:3000
```

**Terminal 2 - Projects MFE**
```bash
npm run start:projects
# Starts on http://localhost:3001
```

**Terminal 3 - Evaluations MFE**
```bash
npm run start:evaluations
# Starts on http://localhost:3002
```

**Terminal 4 - Playground MFE**
```bash
npm run start:playground
# Starts on http://localhost:3003
```

**Terminal 5 - Traces MFE**
```bash
npm run start:traces
# Starts on http://localhost:3004
```

**Terminal 6 - Policy MFE**
```bash
npm run start:policy
# Starts on http://localhost:3005
```

**Terminal 7 - Models MFE**
```bash
npm run start:models
# Starts on http://localhost:3006
```

---

### Step 5: Access the Application

**1. Wait for compilation to complete**

Look for these messages in your terminal:
```
✓ Compiled successfully
webpack 5.89.0 compiled successfully in XXXX ms
```

**All 7 services must show "compiled successfully"**

**2. Open your browser**

```
http://localhost:3000
```

**3. You should see the login page**

If you see errors, check the [Common Issues](#common-issues--solutions) section.

---

### Step 6: Login

**Demo Credentials:**
- **Email:** `demo@promptforge.ai`
- **Password:** `demo123`

**Or use ANY email/password combination** - the mock authentication accepts all credentials.

**Click "Sign In"**

You should be redirected to: `http://localhost:3000/projects`

---

### Step 7: Verify All MFEs Load

Click through each menu item in the sidebar:

1. **Dashboard** → Should show metrics and quick actions
2. **Projects** → Should show 5 project cards
3. **Evaluations** → Should show evaluation results table
4. **Playground** → Should show prompt testing interface
5. **Traces** → Should show request traces
6. **Policy** → Should show governance rules
7. **Models** → Should show model registry

**All pages should load without errors.**

---

## Port Configuration Reference

### Service Port Mapping

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| **Shell** | 3000 | http://localhost:3000 | Host application (main entry) |
| **Projects** | 3001 | http://localhost:3001 | Projects MFE (standalone) |
| **Evaluations** | 3002 | http://localhost:3002 | Evaluations MFE (standalone) |
| **Playground** | 3003 | http://localhost:3003 | Playground MFE (standalone) |
| **Traces** | 3004 | http://localhost:3004 | Traces MFE (standalone) |
| **Policy** | 3005 | http://localhost:3005 | Policy MFE (standalone) |
| **Models** | 3006 | http://localhost:3006 | Models MFE (standalone) |

### Module Federation Configuration

**Shell (Host):**
- **Name:** `shell`
- **Remotes:** All 6 MFEs via http://localhost:300X/remoteEntry.js
- **Exposes:** Nothing (host only)

**Each MFE (Remote):**
- **Name:** `projects`, `evaluations`, `playground`, `traces`, `policy`, `models`
- **Filename:** `remoteEntry.js`
- **Exposes:** `'./App': './src/App'`
- **Shared:** React, React-DOM as singletons

### CORS Configuration

All MFEs have CORS headers enabled:
```javascript
headers: {
  'Access-Control-Allow-Origin': '*',
}
```

This allows the shell to load modules from different ports.

---

## Validation & Testing

### Quick Validation Checklist

**✅ All services running:**
```bash
# Check if all ports are listening
lsof -i :3000,3001,3002,3003,3004,3005,3006
```

Expected: 7 node processes

**✅ Shell loads:**
```bash
curl -I http://localhost:3000
```

Expected: `HTTP/1.1 200 OK`

**✅ Projects MFE remote entry loads:**
```bash
curl -I http://localhost:3001/remoteEntry.js
```

Expected: `HTTP/1.1 200 OK`

**✅ Browser console clean:**
- Open DevTools (F12)
- Check Console tab
- Should have no critical errors (red)

**✅ Module Federation working:**
- Navigate to Projects page
- Check Network tab in DevTools
- Should see: `remoteEntry.js` loaded from port 3001

### Full Test Procedure

See [TESTING_CHECKLIST.md](./TESTING_CHECKLIST.md) for comprehensive testing.

---

## Common Issues & Solutions

### Issue 1: Port Already in Use

**Error:**
```
Error: listen EADDRINUSE: address already in use :::3000
```

**Solution A - Kill the process:**
```bash
# Find process using port 3000
lsof -i :3000

# Kill it (replace PID with actual process ID)
kill -9 <PID>

# Or use killall
killall -9 node
```

**Solution B - Use different port:**
```bash
# For shell
PORT=3100 npm run start:shell

# Update shell/webpack.config.js port to 3100
# Update all MFE remote URLs in shell/webpack.config.js
```

---

### Issue 2: Module Not Found

**Error:**
```
Module not found: Error: Can't resolve 'react'
```

**Solution:**
```bash
# Remove all node_modules
find . -name "node_modules" -type d -prune -exec rm -rf '{}' +

# Clear npm cache
npm cache clean --force

# Reinstall everything
npm run install:all
```

---

### Issue 3: Webpack Compilation Failed

**Error:**
```
Failed to compile with X errors
```

**Solution:**
```bash
# Check for syntax errors in the error output
# Common issues:
# 1. Missing semicolon
# 2. Incorrect import path
# 3. TypeScript type error

# Clear webpack cache
rm -rf */node_modules/.cache

# Restart dev server
npm run start:all
```

---

### Issue 4: Module Federation Error

**Error:**
```
Uncaught Error: Shared module is not available for eager consumption
```

**Solution:**
1. Ensure ALL MFEs are running (check all 7 ports)
2. Hard refresh browser: Cmd+Shift+R (Mac) or Ctrl+Shift+F5 (Windows)
3. Clear browser cache
4. Verify webpack configs have correct remote URLs

**Check remotes are accessible:**
```bash
curl http://localhost:3001/remoteEntry.js
curl http://localhost:3002/remoteEntry.js
curl http://localhost:3003/remoteEntry.js
curl http://localhost:3004/remoteEntry.js
curl http://localhost:3005/remoteEntry.js
curl http://localhost:3006/remoteEntry.js
```

All should return JavaScript code.

---

### Issue 5: CORS Error

**Error:**
```
Access to fetch at 'http://localhost:3001/remoteEntry.js' from origin
'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**

1. Verify CORS headers in MFE webpack configs:
```javascript
devServer: {
  headers: {
    'Access-Control-Allow-Origin': '*',
  },
}
```

2. Restart the affected MFE
3. Hard refresh browser

---

### Issue 6: React Version Mismatch

**Error:**
```
Error: Invalid hook call. Hooks can only be called inside of the body
of a function component.
```

**Solution:**

This usually means multiple React instances. Check:

1. Ensure shared config is correct in webpack.config.js:
```javascript
shared: {
  react: { singleton: true, requiredVersion: '^18.2.0' },
  'react-dom': { singleton: true, requiredVersion: '^18.2.0' },
}
```

2. Verify package.json has same React version in all apps:
```bash
grep '"react"' */package.json
```

All should show `"react": "^18.2.0"`

---

### Issue 7: TypeScript Errors

**Error:**
```
TS2307: Cannot find module '@/components/Layout/Sidebar'
```

**Solution:**

1. Check tsconfig.json has correct paths:
```json
"baseUrl": ".",
"paths": {
  "@/*": ["src/*"]
}
```

2. Restart TypeScript server in VS Code:
   - Cmd+Shift+P → "TypeScript: Restart TS Server"

3. If still failing, check import path is correct

---

## Development Workflow

### Making Changes

**1. Edit source files**

Files in `src/` directories will hot reload automatically.

**Example:**
```bash
# Edit a file
vim shell/src/pages/Dashboard.tsx

# Save the file
# Browser auto-refreshes in ~1 second
```

**2. Add new components**

```bash
# Create new component
touch shell/src/components/NewFeature.tsx

# Import in parent component
# Add to routing if needed
```

**3. Add new mock data**

```bash
# Edit mock data
vim mfe-projects/src/mockData.ts

# Add new items to array
# Save - auto-reloads
```

### Debugging

**Browser DevTools:**
```
F12 → Console tab → Check for errors
F12 → Network tab → Check module loading
F12 → Sources tab → Set breakpoints
```

**Webpack Output:**
```
Check terminal for compilation errors
Look for "compiled successfully" messages
```

**React DevTools:**
```
Install React DevTools extension
F12 → Components tab → Inspect component tree
F12 → Profiler tab → Check performance
```

### Building for Production

```bash
# Build all applications
npm run build:all

# Build individual apps
npm run build:shell
npm run build:projects
# etc.
```

**Output locations:**
```
shell/dist/
mfe-projects/dist/
mfe-evaluations/dist/
... (and so on)
```

### Stopping Servers

**If using `npm run start:all`:**
```bash
# Press Ctrl+C in terminal
# All services stop together
```

**If using individual terminals:**
```bash
# Press Ctrl+C in each terminal
# Or close the terminal windows
```

**Force kill all node processes (last resort):**
```bash
killall -9 node
```

---

## Advanced Configuration

### Environment Variables

Create `.env.local` files in each application:

**shell/.env.local:**
```env
PORT=3000
REACT_APP_API_URL=http://localhost:8000
```

**mfe-projects/.env.local:**
```env
PORT=3001
```

### Custom Ports

If you need to use different ports:

1. Update webpack.config.js in each MFE:
```javascript
devServer: {
  port: 4001,  // Change this
}
```

2. Update shell/webpack.config.js remotes:
```javascript
remotes: {
  projects: 'projects@http://localhost:4001/remoteEntry.js',
}
```

### Performance Tuning

**Increase memory for Node.js:**
```bash
export NODE_OPTIONS="--max-old-space-size=4096"
npm run start:all
```

**Disable source maps (faster builds):**

In webpack.config.js:
```javascript
devtool: false,  // Disable source maps
```

---

## Validation Summary

### ✅ Success Criteria

Your setup is successful if:

1. ✅ All 7 services start without errors
2. ✅ http://localhost:3000 shows login page
3. ✅ Login works and redirects to dashboard
4. ✅ All 6 MFE pages load when clicked
5. ✅ No critical console errors
6. ✅ Mock data displays correctly
7. ✅ Theme toggle works
8. ✅ Logout/login flow works

### 🎉 You're Ready!

If all criteria are met, your PromptForge installation is working correctly!

---

## Next Steps

- **Explore the UI** - Navigate through all modules
- **Review the code** - Understand the architecture
- **Read ARCHITECTURE.md** - Learn technical details
- **Proceed to Phase 2** - Backend integration

---

## Quick Reference Commands

```bash
# Install everything
npm run install:all

# Start everything
npm run start:all

# Build everything
npm run build:all

# Start individual services
npm run start:shell
npm run start:projects
npm run start:evaluations
npm run start:playground
npm run start:traces
npm run start:policy
npm run start:models

# Check what's running
lsof -i :3000,3001,3002,3003,3004,3005,3006

# Kill all Node processes
killall -9 node

# Clean and reinstall
find . -name "node_modules" -type d -prune -exec rm -rf '{}' +
npm run install:all
```

---

## Support

**Documentation:**
- README.md - Project overview
- SETUP.md - Installation guide
- ARCHITECTURE.md - Technical details
- TESTING_CHECKLIST.md - Validation tests

**Common Issues:**
- See "Common Issues & Solutions" above
- Check browser console for errors
- Check terminal output for build errors

---

**PromptForge Local Execution Guide**
*Everything you need to run PromptForge locally* 🚀

**Version:** Phase 1 - Core UI Build
**Last Updated:** 2025-10-05
