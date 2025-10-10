# PromptForge Setup Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Running Locally](#running-locally)
4. [Troubleshooting](#troubleshooting)
5. [Configuration](#configuration)
6. [Development Workflow](#development-workflow)

---

## System Requirements

### Required Software

- **Node.js:** 18.x or later ([Download](https://nodejs.org/))
- **npm:** 9.x or later (comes with Node.js)
- **Git:** Latest version ([Download](https://git-scm.com/))

### Recommended

- **VS Code:** Latest version with extensions:
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense
  - TypeScript and JavaScript Language Features

### System Specifications

- **RAM:** 8GB minimum, 16GB recommended
- **Disk Space:** 2GB free space
- **OS:** macOS, Windows, or Linux

---

## Installation

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd promptforge
```

### Step 2: Install Dependencies

#### Option A: Install All at Once (Recommended)

```bash
npm run install:all
```

This command will:
1. Install root dependencies
2. Navigate to each MFE directory
3. Install dependencies for all 7 applications

**Expected time:** 3-5 minutes depending on network speed

#### Option B: Install Individually

```bash
# Root dependencies
npm install

# Shell
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

### Step 3: Verify Installation

Check that `node_modules/` exists in:
- `/promptforge/node_modules/`
- `/promptforge/shell/node_modules/`
- `/promptforge/mfe-*/node_modules/` (6 directories)

---

## Running Locally

### Quick Start (All Services)

```bash
npm run start:all
```

This uses `concurrently` to start all 7 services in parallel.

**Services Started:**
- Shell: http://localhost:3000
- Projects: http://localhost:3001
- Evaluations: http://localhost:3002
- Playground: http://localhost:3003
- Traces: http://localhost:3004
- Policy: http://localhost:3005
- Models: http://localhost:3006

**Startup time:** 20-30 seconds for all services to be ready

### Individual Services

Start services in separate terminal windows:

**Terminal 1 - Shell (Required)**
```bash
npm run start:shell
```

**Terminal 2 - Projects MFE**
```bash
npm run start:projects
```

**Terminal 3 - Evaluations MFE**
```bash
npm run start:evaluations
```

**Terminal 4 - Playground MFE**
```bash
npm run start:playground
```

**Terminal 5 - Traces MFE**
```bash
npm run start:traces
```

**Terminal 6 - Policy MFE**
```bash
npm run start:policy
```

**Terminal 7 - Models MFE**
```bash
npm run start:models
```

### Accessing the Application

1. **Wait for all services to start**
   - Look for "webpack compiled successfully" messages
   - All 7 services should show "compiled successfully"

2. **Open browser**
   ```
   http://localhost:3000
   ```

3. **Login with demo credentials**
   - Email: `demo@promptforge.ai`
   - Password: `demo123`
   - Or use any email/password combination

4. **Navigate the application**
   - Dashboard: Overview and metrics
   - Projects: Manage prompt projects
   - Evaluations: Performance testing
   - Playground: Interactive testing
   - Traces: Request monitoring
   - Policy: Governance rules
   - Models: Model registry

---

## Troubleshooting

### Port Already in Use

**Error:** `Port 3000 is already in use`

**Solution:**
```bash
# Find process using port
lsof -i :3000

# Kill process
kill -9 <PID>

# Or use different port
PORT=3100 npm run start:shell
```

### Module Federation Error

**Error:** `Uncaught Error: Shared module is not available for eager consumption`

**Solution:**
1. Ensure all MFEs are running
2. Check webpack.config.js has correct remote URLs
3. Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+F5)
4. Clear browser cache

### Dependency Issues

**Error:** `Cannot find module 'react'`

**Solution:**
```bash
# Remove all node_modules
find . -name "node_modules" -type d -prune -exec rm -rf '{}' +

# Reinstall
npm run install:all
```

### TypeScript Errors

**Error:** `TS2307: Cannot find module`

**Solution:**
```bash
# Clean TypeScript cache
cd shell && rm -rf node_modules/.cache && cd ..
cd mfe-projects && rm -rf node_modules/.cache && cd ..

# Restart dev server
```

### CORS Errors

**Error:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Cause:** MFE not running or wrong port

**Solution:**
1. Check all MFEs are running on correct ports
2. Verify webpack.config.js has CORS headers
3. Restart affected MFE

### Build Errors

**Error:** `Module not found: Error: Can't resolve`

**Solution:**
```bash
# Check package.json dependencies
npm list <package-name>

# Reinstall specific package
npm install <package-name>

# Or reinstall all
npm run install:all
```

---

## Configuration

### Environment Variables

Create `.env.local` files in each application directory:

**shell/.env.local**
```env
PORT=3000
REACT_APP_API_URL=http://localhost:8000
```

**mfe-projects/.env.local**
```env
PORT=3001
```

### Webpack Configuration

Each MFE has a `webpack.config.js` file:

**Key Settings:**
- `port`: Development server port
- `name`: Module Federation name
- `exposes`: Exported components
- `remotes`: Remote module URLs
- `shared`: Shared dependencies

### Tailwind Configuration

Customize `tailwind.config.js` in each application:

```javascript
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      // Custom colors, fonts, etc.
    },
  },
  plugins: [],
}
```

### TypeScript Configuration

Modify `tsconfig.json` for stricter typing:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

---

## Development Workflow

### Making Changes

1. **Start development servers**
   ```bash
   npm run start:all
   ```

2. **Edit source files**
   - Changes auto-reload via webpack HMR
   - Check browser console for errors

3. **Test changes**
   - Manual testing in browser
   - Unit tests: `npm test` (in specific MFE)

4. **Build for production**
   ```bash
   npm run build:all
   ```

### Adding New Features

1. **Identify the MFE**
   - Which module owns this feature?

2. **Create components**
   ```bash
   cd mfe-<name>/src/components
   touch NewFeature.tsx
   ```

3. **Update routing** (if needed)
   - Shell: `src/App.tsx`
   - MFE: `src/App.tsx`

4. **Add mock data** (if needed)
   - Update `src/mockData.ts`

5. **Test integration**
   - Standalone: http://localhost:300X
   - Integrated: http://localhost:3000

### Code Quality

**Linting:**
```bash
cd shell
npm run lint
```

**Type Checking:**
```bash
cd shell
npx tsc --noEmit
```

**Formatting:**
```bash
npx prettier --write "src/**/*.{ts,tsx}"
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/new-feature

# Create pull request
```

---

## Performance Tips

### Development

1. **Run only needed MFEs**
   - Start shell + specific MFE only
   - Reduces memory usage

2. **Use production build for testing**
   ```bash
   npm run build:shell
   npx serve -s shell/dist -p 3000
   ```

3. **Clear webpack cache**
   ```bash
   find . -name ".cache" -type d -prune -exec rm -rf '{}' +
   ```

### Production

1. **Enable compression**
   - Configure webpack compression plugin

2. **Tree shaking**
   - Ensure `sideEffects: false` in package.json

3. **Code splitting**
   - Use dynamic imports for routes

4. **CDN for shared dependencies**
   - Host React, etc. on CDN
   - Update webpack externals

---

## Next Steps

✅ **Phase 1 Complete** - You have a working micro-frontend application!

📋 **Ready for Phase 2:**
- Backend API implementation
- Database integration
- Real authentication
- Production deployment

---

**Need Help?**
- Check the main README.md
- Review webpack.config.js files
- Inspect browser console for errors
- Check terminal output for build errors

---

*PromptForge Setup Guide - Phase 1*
