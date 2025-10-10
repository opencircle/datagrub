# PromptForge Phase 1 - Testing Checklist

Use this checklist to validate that PromptForge Phase 1 is working correctly on your local machine.

---

## Prerequisites ✅

- [ ] Node.js 18.x or later installed (`node -v`)
- [ ] npm 9.x or later installed (`npm -v`)
- [ ] Git installed (`git --version`)
- [ ] At least 2GB free disk space
- [ ] Ports 3000-3006 available

---

## Installation Testing

### Step 1: Install Dependencies
```bash
cd promptforge
npm run install:all
```

**Expected:**
- [ ] Root dependencies install successfully
- [ ] Shell dependencies install successfully
- [ ] All 6 MFE dependencies install successfully
- [ ] No critical errors in console
- [ ] `node_modules/` exists in 8 directories

**Time:** 3-5 minutes

---

## Development Server Testing

### Step 2: Start All Services
```bash
npm run start:all
```

**Expected:**
- [ ] All 7 webpack dev servers start
- [ ] Shell compiles on port 3000
- [ ] Projects compiles on port 3001
- [ ] Evaluations compiles on port 3002
- [ ] Playground compiles on port 3003
- [ ] Traces compiles on port 3004
- [ ] Policy compiles on port 3005
- [ ] Models compiles on port 3006
- [ ] All show "compiled successfully"

**Time:** 15-30 seconds for all services

---

## Shell Application Testing

### Step 3: Access Shell
Open browser to: **http://localhost:3000**

**Expected:**
- [ ] Login page displays
- [ ] No console errors
- [ ] Page is responsive
- [ ] Form fields are visible

### Step 4: Test Login
**Credentials:**
- Email: `demo@promptforge.ai`
- Password: `demo123`

**Expected:**
- [ ] Login button is enabled
- [ ] Click shows loading state
- [ ] Redirect to dashboard after 1 second
- [ ] No console errors

### Step 5: Verify Dashboard
**Expected:**
- [ ] Dashboard page loads
- [ ] Sidebar is visible on left
- [ ] Header is visible on top
- [ ] 4 metric cards display
- [ ] Quick action buttons visible
- [ ] User name shows "Demo User"
- [ ] No console errors

---

## MFE Integration Testing

### Step 6: Test Projects MFE
Click "Projects" in sidebar

**Expected:**
- [ ] Projects page loads
- [ ] 5 project cards display
- [ ] Search box is functional
- [ ] Status badges show (active, draft, archived)
- [ ] Icons and images load
- [ ] Hover effects work on cards
- [ ] No console errors

**Test Search:**
- [ ] Type "customer" in search
- [ ] Projects filter to show "Customer Support Assistant"
- [ ] Clear search shows all projects again

### Step 7: Test Evaluations MFE
Click "Evaluations" in sidebar

**Expected:**
- [ ] Evaluations page loads
- [ ] Table displays with 5 rows
- [ ] Status badges show (running, completed, failed)
- [ ] Metrics display correctly
- [ ] 4 summary cards at top show data
- [ ] Table is scrollable if needed
- [ ] No console errors

### Step 8: Test Playground MFE
Click "Playground" in sidebar

**Expected:**
- [ ] Playground page loads
- [ ] Model dropdown shows options
- [ ] Text input areas are visible
- [ ] Parameter sliders are functional
- [ ] 3 session history items display
- [ ] Expandable sessions work
- [ ] No console errors

### Step 9: Test Traces MFE
Click "Traces" in sidebar

**Expected:**
- [ ] Traces page loads
- [ ] Table displays with 5 traces
- [ ] Expandable rows work
- [ ] Span details show when expanded
- [ ] Metrics cards display at top
- [ ] Status badges show correctly
- [ ] No console errors

### Step 10: Test Policy MFE
Click "Policy" in sidebar

**Expected:**
- [ ] Policy page loads
- [ ] Tabs work (Policies / Violations)
- [ ] 6 policy cards display on Policies tab
- [ ] Enable/disable toggle works (UI only)
- [ ] 5 violations display on Violations tab
- [ ] Severity badges show
- [ ] No console errors

### Step 11: Test Models MFE
Click "Models" in sidebar

**Expected:**
- [ ] Models page loads
- [ ] 8 model cards display
- [ ] Provider filter dropdown works
- [ ] Pricing information displays
- [ ] Performance metrics show
- [ ] Status badges (active, beta, deprecated) display
- [ ] No console errors

---

## Navigation Testing

### Step 12: Test Navigation Flow
**Execute:**
1. [ ] Click Projects → page loads
2. [ ] Click Evaluations → page loads
3. [ ] Click Playground → page loads
4. [ ] Click Traces → page loads
5. [ ] Click Policy → page loads
6. [ ] Click Models → page loads
7. [ ] Click Dashboard → returns to dashboard

**Expected:**
- [ ] All navigation works without page reload
- [ ] Active menu item highlights correctly
- [ ] Sidebar selection updates on each click
- [ ] No console errors during navigation

---

## Theme Testing

### Step 13: Test Dark Mode
**Execute:**
1. [ ] Click moon/sun icon in header
2. [ ] Theme switches to dark mode
3. [ ] Click again to switch back to light

**Expected:**
- [ ] Background changes to dark/light
- [ ] Text color inverts appropriately
- [ ] All components respect theme
- [ ] Theme persists across page navigation

---

## Authentication Testing

### Step 14: Test Logout
**Execute:**
1. [ ] Click "Logout" button in header
2. [ ] Wait for redirect

**Expected:**
- [ ] Redirects to login page
- [ ] Session is cleared
- [ ] Can't access protected routes
- [ ] No console errors

### Step 15: Test Protected Routes
**Execute:**
1. [ ] While logged out, try accessing: http://localhost:3000/projects

**Expected:**
- [ ] Redirects to login page
- [ ] Shows login form
- [ ] URL changes to /login

### Step 16: Test Login Again
**Execute:**
1. [ ] Login with any credentials
2. [ ] Verify redirect to projects page

**Expected:**
- [ ] Login succeeds
- [ ] Redirects to /projects
- [ ] Projects MFE loads
- [ ] Session persists on navigation

---

## Responsive Design Testing

### Step 17: Test Mobile Layout
**Execute:**
1. [ ] Open browser DevTools (F12)
2. [ ] Switch to mobile view (iPhone/Android)
3. [ ] Navigate through pages

**Expected:**
- [ ] Layout adapts to mobile width
- [ ] Sidebar collapses (if implemented) or adapts
- [ ] Cards stack vertically
- [ ] Text is readable
- [ ] Buttons are touch-friendly
- [ ] No horizontal scroll

### Step 18: Test Tablet Layout
**Execute:**
1. [ ] Set viewport to 768px width
2. [ ] Navigate through pages

**Expected:**
- [ ] 2-column grid for cards
- [ ] Sidebar and content both visible
- [ ] Readable text size
- [ ] Proper spacing

### Step 19: Test Desktop Layout
**Execute:**
1. [ ] Set viewport to 1920px width
2. [ ] Navigate through pages

**Expected:**
- [ ] 3-4 column grid for cards
- [ ] Full sidebar visible
- [ ] Proper use of whitespace
- [ ] No content too narrow or too wide

---

## Performance Testing

### Step 20: Test Load Times
**Execute:**
1. [ ] Open Network tab in DevTools
2. [ ] Refresh page
3. [ ] Check load times

**Expected:**
- [ ] Initial page load < 3 seconds
- [ ] MFE loads < 1 second each
- [ ] No failed network requests
- [ ] All assets load successfully

### Step 21: Test Hot Reload
**Execute:**
1. [ ] Keep `npm run start:all` running
2. [ ] Edit `shell/src/pages/Dashboard.tsx`
3. [ ] Change welcome text
4. [ ] Save file

**Expected:**
- [ ] Browser auto-refreshes
- [ ] Changes appear immediately
- [ ] No manual reload needed
- [ ] No errors in console

---

## Console Testing

### Step 22: Check for Console Errors
**Execute:**
1. [ ] Open browser DevTools console
2. [ ] Navigate through all pages
3. [ ] Check for errors/warnings

**Expected:**
- [ ] No critical errors (red)
- [ ] Minor warnings acceptable (yellow)
- [ ] No CORS errors
- [ ] No 404s for assets
- [ ] Module Federation loads successfully

---

## Individual MFE Testing (Standalone)

### Step 23: Test Projects MFE Standalone
**Execute:**
1. [ ] Open: http://localhost:3001
2. [ ] Verify it loads independently

**Expected:**
- [ ] Projects page displays
- [ ] Mock data shows
- [ ] Styling is applied
- [ ] Fully functional

### Step 24: Test Each MFE Standalone
**Execute for each:**
- [ ] http://localhost:3002 (Evaluations)
- [ ] http://localhost:3003 (Playground)
- [ ] http://localhost:3004 (Traces)
- [ ] http://localhost:3005 (Policy)
- [ ] http://localhost:3006 (Models)

**Expected:**
- [ ] Each MFE loads independently
- [ ] Mock data displays
- [ ] UI is functional
- [ ] No dependency on shell

---

## Build Testing

### Step 25: Test Production Build
**Execute:**
```bash
npm run build:all
```

**Expected:**
- [ ] Shell builds successfully
- [ ] All 6 MFEs build successfully
- [ ] No build errors
- [ ] dist/ folders created in each app
- [ ] Assets are minified

**Time:** 1-2 minutes

---

## Cross-Browser Testing (Optional)

### Step 26: Test in Chrome
**Execute:**
1. [ ] Open in Chrome
2. [ ] Test login and navigation
3. [ ] Check console for errors

### Step 27: Test in Firefox
**Execute:**
1. [ ] Open in Firefox
2. [ ] Test login and navigation
3. [ ] Check console for errors

### Step 28: Test in Safari
**Execute:**
1. [ ] Open in Safari
2. [ ] Test login and navigation
3. [ ] Check console for errors

**Expected:**
- [ ] Works in all browsers
- [ ] Consistent UI
- [ ] No browser-specific errors

---

## Final Validation

### Step 29: Complete User Flow
**Execute full user journey:**
1. [ ] Visit http://localhost:3000
2. [ ] Login with demo credentials
3. [ ] View dashboard
4. [ ] Navigate to Projects → search for a project
5. [ ] Navigate to Evaluations → view test results
6. [ ] Navigate to Playground → interact with UI
7. [ ] Navigate to Traces → expand a trace
8. [ ] Navigate to Policy → switch tabs
9. [ ] Navigate to Models → filter by provider
10. [ ] Toggle theme to dark mode
11. [ ] Logout
12. [ ] Login again

**Expected:**
- [ ] Entire flow works seamlessly
- [ ] No errors at any step
- [ ] UI is responsive and polished
- [ ] Data persists appropriately

---

## Issue Reporting Template

If you encounter issues, document them:

```
Issue: [Brief description]
Location: [Which MFE or page]
Steps to Reproduce:
1.
2.
3.
Expected: [What should happen]
Actual: [What actually happened]
Console Errors: [Any errors from console]
Browser: [Chrome, Firefox, Safari, etc.]
```

---

## Success Criteria

**All tests should pass ✅**

- [ ] All installation steps completed
- [ ] All 7 services start successfully
- [ ] All 6 MFEs load in shell
- [ ] All navigation works
- [ ] All mock data displays
- [ ] No critical console errors
- [ ] Theme switching works
- [ ] Authentication flow works
- [ ] Responsive design works
- [ ] Production build succeeds

**If all checkboxes are marked, Phase 1 is validated! ✅**

---

**PromptForge Testing Checklist** - Phase 1
*Validate before proceeding to Phase 2*
