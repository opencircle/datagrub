# MFE Deep Linking and Routing Pattern

**Version**: 1.0.0
**Created**: 2025-10-12
**Status**: Production Standard - Apply to All MFEs
**Reference Implementation**: mfe-insights

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [URL Structure Standard](#url-structure-standard)
4. [Implementation Patterns](#implementation-patterns)
5. [Router Configuration](#router-configuration)
6. [Navigation Best Practices](#navigation-best-practices)
7. [Common Pitfalls](#common-pitfalls)
8. [Code Examples](#code-examples)
9. [Testing Checklist](#testing-checklist)

---

## Overview

All PromptForge MFEs must implement **bookmarkable, shareable deep links** using React Router. This ensures:

- Users can bookmark any application state
- Direct links can be shared via email/Slack
- Browser back/forward buttons work correctly
- Application state persists across page refreshes
- SEO-friendly URLs for public-facing features

**Core Principle**: **URL is the source of truth** for navigation state.

---

## Architecture

### Shell-MFE Routing Hierarchy

```
Shell (BrowserRouter)
  └─ /insights/* → insights MFE (Module Federation)
       └─ <Routes> (NOT BrowserRouter)
            ├─ /insights (index)
            ├─ /insights/analysis/:analysisId
            ├─ /insights/compare
            ├─ /insights/compare/:analysisIdA/:analysisIdB
            └─ /insights/comparisons/:comparisonId
```

**Key Points**:
1. **Shell owns BrowserRouter** - Only ONE BrowserRouter per application
2. **Shell sets `<base href="/">`** in index.html - Enables absolute URL resolution
3. **MFE uses `<Routes>` directly** - No nested BrowserRouter
4. **MFE webpack has `output.publicPath: 'auto'`** - Dynamic chunk loading
5. **Shell route**: `<Route path="insights/*" element={<InsightsApp />} />`
6. **MFE route**: `<Route index element={<InsightsPage />} />` maps to `/insights`

---

## URL Structure Standard

### Pattern Format

```
/{mfe-name}/{resource-type}[/{resource-id}][/{sub-resource}]
```

### Examples by MFE

#### mfe-insights
```
/insights                                    # Home (analysis form + history)
/insights/analysis/:analysisId               # View specific analysis
/insights/compare                            # Comparison selector
/insights/compare/:analysisIdA/:analysisIdB  # Ad-hoc comparison (unsaved)
/insights/comparisons/:comparisonId          # View saved comparison
```

#### mfe-projects (Recommended)
```
/projects                                    # Project list
/projects/:projectId                         # Project detail
/projects/:projectId/prompts                 # Project prompts
/projects/:projectId/prompts/:promptId       # Specific prompt
/projects/:projectId/evaluations             # Project evaluations
/projects/new                                # Create new project (special route)
```

#### mfe-evaluations (Recommended)
```
/evaluations                                 # Evaluation dashboard
/evaluations/:evaluationId                   # Evaluation detail
/evaluations/:evaluationId/results           # Evaluation results
/evaluations/:evaluationId/traces            # Evaluation traces
/evaluations/new                             # Create new evaluation
```

#### mfe-traces (Recommended)
```
/traces                                      # Trace list
/traces/:traceId                             # Trace detail
/traces/:traceId/spans                       # Trace spans
/traces/search?query=error                   # Trace search (query params)
```

### URL Design Rules

1. **Use plural nouns** for resource collections (`/projects`, `/traces`)
2. **Use singular for singletons** (`/profile`, `/settings`)
3. **Keep URLs flat** (max 3 levels: `/resource/:id/sub-resource`)
4. **Special actions last** (`/projects/new`, not `/new/projects`)
5. **Use kebab-case** for multi-word segments (`/model-catalog`, not `/modelCatalog`)
6. **Avoid verbs** (use `/projects/new`, not `/projects/create`)
7. **Query params for filters** (`/projects?status=active&sort=name`)
8. **Path params for identity** (`/projects/:projectId`)

---

## Implementation Patterns

### 1. AppRouter.tsx - Route Definition

```tsx
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import MainPage from './components/MainPage';

/**
 * App Router for mfe-{name}
 *
 * IMPORTANT: Routes are relative to Shell's /{mfe-name}/* mounting point
 * Shell route: <Route path="{mfe-name}/*" element={<MfeApp />} />
 * Our "/" maps to "/{mfe-name}" in browser
 */
export const AppRouter: React.FC = () => {
  return (
    <Routes>
      {/* Index route - main landing page */}
      <Route index element={<MainPage />} />

      {/* Resource detail pages */}
      <Route path="resource/:resourceId" element={<MainPage />} />

      {/* Sub-resources */}
      <Route path="resource/:resourceId/sub" element={<MainPage />} />

      {/* Special actions */}
      <Route path="resource/new" element={<MainPage />} />

      {/* 404 fallback - redirect to MFE home */}
      <Route path="*" element={<Navigate to="/{mfe-name}" replace />} />
    </Routes>
  );
};
```

**Best Practices**:
- Document Shell mounting point in JSDoc
- Use `index` for root route (cleaner than `path="/"`)
- Always include 404 fallback with `Navigate`
- Group related routes together
- Use descriptive comments

---

### 2. Component - URL Parameter Extraction

```tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';

export const MainPage: React.FC = () => {
  // Extract route parameters
  const { resourceId, subResourceId } = useParams<{
    resourceId?: string;
    subResourceId?: string;
  }>();

  // Navigation function (programmatic navigation)
  const navigate = useNavigate();

  // Current location (detect pathname changes)
  const location = useLocation();

  // Local state for view mode
  const [viewMode, setViewMode] = useState<'list' | 'detail'>('list');

  // React to URL changes
  useEffect(() => {
    if (resourceId) {
      setViewMode('detail');
      loadResourceData(resourceId);
    } else if (location.pathname === '/mfe-name' || location.pathname === '/mfe-name/') {
      setViewMode('list');
    }
  }, [resourceId, location.pathname]);

  return (
    <div>
      {viewMode === 'list' && <ResourceList />}
      {viewMode === 'detail' && <ResourceDetail id={resourceId} />}
    </div>
  );
};
```

**Best Practices**:
- Always type `useParams` generic for TypeScript safety
- Use `useEffect` to react to URL changes (not local state)
- Check both params AND pathname for route detection
- Handle undefined params gracefully

---

### 3. Navigation - Programmatic Routing

```tsx
import { useNavigate } from 'react-router-dom';

export const SomeComponent: React.FC = () => {
  const navigate = useNavigate();

  const handleViewResource = (id: string) => {
    // ALWAYS use absolute paths from root
    navigate(`/mfe-name/resource/${id}`);
  };

  const handleCreateResource = () => {
    // Navigate to create page
    navigate('/mfe-name/resource/new');
  };

  const handleBack = () => {
    // Use navigate(-1) for browser back
    navigate(-1);

    // OR navigate to specific location
    navigate('/mfe-name');
  };

  const handleReplace = () => {
    // Replace current history entry (no back button)
    navigate('/mfe-name/resource/new', { replace: true });
  };

  return (
    <div>
      <button onClick={() => handleViewResource('abc-123')}>
        View Resource
      </button>
    </div>
  );
};
```

**Navigation Rules**:
1. **ALWAYS use absolute paths** - `/mfe-name/resource/${id}`, NOT `resource/${id}`
2. **NEVER use relative paths** - Causes routing bugs in nested components
3. **Use `navigate(-1)` for back** - Respects browser history
4. **Use `replace: true`** when redirecting without history entry
5. **Include URL in all click handlers** - Even if callback prop exists

---

### 4. History/List Components - Deep Link Generation

```tsx
import { useNavigate } from 'react-router-dom';

export const ResourceList: React.FC = () => {
  const navigate = useNavigate();

  const handleRowClick = (resourceId: string) => {
    // Update URL to enable deep linking
    navigate(`/mfe-name/resource/${resourceId}`);
  };

  return (
    <table>
      <tbody>
        {resources.map(resource => (
          <tr
            key={resource.id}
            onClick={() => handleRowClick(resource.id)}
            className="cursor-pointer hover:bg-neutral-50"
          >
            <td>{resource.name}</td>
            <td>
              {/* Button also navigates (redundant but explicit) */}
              <button
                onClick={(e) => {
                  e.stopPropagation(); // Prevent row click
                  navigate(`/mfe-name/resource/${resource.id}`);
                }}
                className="text-[#FF385C] hover:underline"
              >
                View
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
```

**Best Practices**:
- Make entire row clickable for better UX
- Use `cursor-pointer` class on clickable rows
- Use `e.stopPropagation()` for nested clickable elements
- Always navigate via `navigate()`, NOT callbacks

---

### 5. Callbacks vs navigate() - When to Use Each

#### ❌ ANTI-PATTERN: Callback-only navigation
```tsx
// BAD - URL doesn't update, not bookmarkable
<ResourceList onSelectResource={(id) => setSelectedId(id)} />
```

#### ✅ CORRECT: navigate() with optional callback
```tsx
// GOOD - URL updates, bookmarkable, AND callback can fire
<ResourceList
  onSelectResource={(id) => {
    navigate(`/mfe-name/resource/${id}`); // Updates URL
    trackAnalytics('resource_viewed', { id }); // Side effect
  }}
/>
```

#### Decision Matrix

| Scenario | Use navigate() | Use Callback | Use Both |
|----------|---------------|--------------|----------|
| Navigate to different route | ✅ | ❌ | Optional |
| Open modal (state only) | ❌ | ✅ | ❌ |
| Navigate + analytics | ✅ | ❌ | ✅ |
| Navigate + parent state | ✅ | ❌ | ✅ |
| Filter/sort (local state) | ❌ | ✅ | ❌ |
| Filter/sort (URL state) | ✅ | ❌ | Optional |

**Rule of Thumb**: If it should be **bookmarkable**, use `navigate()`. If it's **transient UI state** (modals, dropdowns), use local state.

---

## Router Configuration

### Shell Configuration

#### shell/public/index.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- CRITICAL: Base href enables absolute URL resolution -->
  <base href="/">
  <title>PromptForge</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>
```

**Why `<base href="/">`?**
- Enables MFEs to use absolute paths like `/insights/analysis/123`
- Without it, MFEs would need relative paths (error-prone)
- Required for Module Federation to load chunks correctly

#### shell/src/App.tsx
```tsx
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

const InsightsApp = React.lazy(() => import('insights/App'));
const ProjectsApp = React.lazy(() => import('projects/App'));

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Home route */}
        <Route path="/" element={<LandingPage />} />

        {/* MFE routes - note the trailing /* */}
        <Route path="insights/*" element={
          <React.Suspense fallback={<LoadingSpinner />}>
            <InsightsApp />
          </React.Suspense>
        } />

        <Route path="projects/*" element={
          <React.Suspense fallback={<LoadingSpinner />}>
            <ProjectsApp />
          </React.Suspense>
        } />

        {/* 404 fallback */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
};
```

**Critical Points**:
1. **Only Shell has BrowserRouter** - MFEs must NOT add another
2. **Use `path="mfe-name/*"`** - Trailing `/*` passes sub-routes to MFE
3. **Wrap lazy-loaded MFEs in Suspense** - Shows loading state
4. **Add 404 fallback** - Catches unmatched routes

---

### MFE Configuration

#### mfe-{name}/webpack.config.js
```javascript
module.exports = {
  entry: './src/index.tsx',
  output: {
    // CRITICAL: Auto-detects public path for chunk loading
    publicPath: 'auto',
  },
  devServer: {
    port: 3007,
    // CRITICAL: Enables client-side routing (returns index.html for all routes)
    historyApiFallback: true,
    hot: true,
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  },
  plugins: [
    new ModuleFederationPlugin({
      name: 'insights',
      filename: 'remoteEntry.js',
      exposes: {
        './App': './src/bootstrap',
      },
      shared: {
        'react': { singleton: true },
        'react-dom': { singleton: true },
        // CRITICAL: Share React Router to prevent duplicate contexts
        'react-router-dom': { singleton: true },
      },
    }),
  ],
};
```

**Critical Configurations**:
1. **`output.publicPath: 'auto'`** - Dynamic base URL detection
2. **`historyApiFallback: true`** - Returns index.html for deep links
3. **`'react-router-dom': { singleton: true }`** - Shared router instance

#### mfe-{name}/src/bootstrap.tsx
```tsx
import React from 'react';
import { AppRouter } from './AppRouter';

/**
 * Bootstrap file for Module Federation
 *
 * IMPORTANT: Do NOT wrap in BrowserRouter here
 * Shell already provides BrowserRouter context
 */
export default function Bootstrap() {
  return <AppRouter />;
}
```

**Why no BrowserRouter?**
- Shell already provides `<BrowserRouter>` context
- Adding another causes "You cannot render a <Router> inside another <Router>" error
- MFE uses `<Routes>` to define sub-routes

---

## Navigation Best Practices

### 1. Always Use Absolute Paths

```tsx
// ✅ CORRECT
navigate('/insights/analysis/123');

// ❌ WRONG - Breaks in nested routes
navigate('analysis/123');
navigate('../analysis/123');
```

### 2. Update URL Before API Calls

```tsx
// ✅ CORRECT - URL updates immediately, data loads after
const handleViewAnalysis = (id: string) => {
  navigate(`/insights/analysis/${id}`);
  // useEffect will trigger data fetch
};

// ❌ WRONG - Data loads, THEN URL updates (feels slow)
const handleViewAnalysis = async (id: string) => {
  await fetchAnalysis(id);
  navigate(`/insights/analysis/${id}`);
};
```

### 3. Use useEffect to Respond to URL Changes

```tsx
// ✅ CORRECT - Reactive to URL changes
useEffect(() => {
  if (analysisId) {
    loadAnalysisData(analysisId);
  }
}, [analysisId]);

// ❌ WRONG - Only runs on mount, misses URL changes
const handleLoad = () => {
  if (analysisId) {
    loadAnalysisData(analysisId);
  }
};
```

### 4. Handle Loading and Error States

```tsx
const { analysisId } = useParams();
const [data, setData] = useState(null);
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState(null);

useEffect(() => {
  if (!analysisId) return;

  setIsLoading(true);
  setError(null);

  fetchAnalysis(analysisId)
    .then(setData)
    .catch(setError)
    .finally(() => setIsLoading(false));
}, [analysisId]);

if (isLoading) return <LoadingSpinner />;
if (error) return <ErrorMessage error={error} />;
if (!data) return <EmptyState />;

return <DataView data={data} />;
```

### 5. Navigate vs Link Component

```tsx
// Use navigate() for programmatic navigation (event handlers)
<button onClick={() => navigate('/insights/analysis/123')}>
  View Analysis
</button>

// Use <Link> for anchor tags (better SEO, right-click context menu)
import { Link } from 'react-router-dom';
<Link to="/insights/analysis/123" className="text-[#FF385C] hover:underline">
  View Analysis
</Link>
```

**When to use each**:
- `<Link>` - Primary CTA, navigation links, breadcrumbs
- `navigate()` - Table row clicks, form submissions, conditional navigation

---

## Common Pitfalls

### 1. Duplicate BrowserRouter

**Error**: "You cannot render a `<Router>` inside another `<Router>`"

**Cause**:
```tsx
// ❌ WRONG - MFE adds its own BrowserRouter
export default function Bootstrap() {
  return (
    <BrowserRouter>  {/* Shell already provides this */}
      <AppRouter />
    </BrowserRouter>
  );
}
```

**Fix**:
```tsx
// ✅ CORRECT - Use Shell's BrowserRouter
export default function Bootstrap() {
  return <AppRouter />;
}
```

---

### 2. Relative Path Navigation

**Problem**: Breaks in nested routes

```tsx
// Current URL: /insights/analysis/123

// ❌ WRONG - Navigates to /insights/analysis/456 (incorrect)
navigate('compare/456');

// ✅ CORRECT - Navigates to /insights/compare/456
navigate('/insights/compare/456');
```

---

### 3. Missing historyApiFallback

**Problem**: Deep links return 404 on page refresh

**Cause**: Dev server doesn't know `/insights/analysis/123` is a client-side route

**Fix**: Add to webpack.config.js
```javascript
devServer: {
  historyApiFallback: true,  // Returns index.html for all routes
}
```

---

### 4. Missing publicPath: 'auto'

**Problem**: Module Federation chunks fail to load

**Cause**: Webpack doesn't know the base URL for chunk loading

**Fix**: Add to webpack.config.js
```javascript
output: {
  publicPath: 'auto',  // Auto-detects base URL
}
```

---

### 5. Not Sharing react-router-dom

**Problem**: "useNavigate() may be used only in the context of a <Router> component"

**Cause**: MFE has its own copy of react-router-dom

**Fix**: Add to Module Federation shared config
```javascript
shared: {
  'react-router-dom': { singleton: true },  // Share with Shell
}
```

---

### 6. Callback-Only Navigation

**Problem**: URLs don't update, links not bookmarkable

```tsx
// ❌ WRONG - Callback updates local state, URL unchanged
<HistorySection onSelectAnalysis={setSelectedId} />

// ✅ CORRECT - navigate() updates URL
<HistorySection onSelectAnalysis={(id) => navigate(`/insights/analysis/${id}`)} />
```

---

### 7. Missing 404 Fallback

**Problem**: Unmatched routes show blank page

```tsx
// ❌ WRONG - No fallback
<Routes>
  <Route index element={<HomePage />} />
  <Route path="resource/:id" element={<DetailPage />} />
</Routes>

// ✅ CORRECT - Redirect to home
<Routes>
  <Route index element={<HomePage />} />
  <Route path="resource/:id" element={<DetailPage />} />
  <Route path="*" element={<Navigate to="/mfe-name" replace />} />
</Routes>
```

---

## Code Examples

### Example 1: mfe-insights AppRouter

**File**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-insights/src/AppRouter.tsx`

```tsx
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import InsightsPage from './components/InsightsPage';

export const AppRouter: React.FC = () => {
  return (
    <Routes>
      {/* Main insights page - handles all views via internal state */}
      <Route index element={<InsightsPage />} />

      {/* Deep link routes - handled by InsightsPage with URL params */}
      <Route path="analysis/:analysisId" element={<InsightsPage />} />
      <Route path="compare" element={<InsightsPage />} />
      <Route path="compare/:analysisIdA/:analysisIdB" element={<InsightsPage />} />
      <Route path="comparisons/:comparisonId" element={<InsightsPage />} />

      {/* 404 fallback - redirect to insights home */}
      <Route path="*" element={<Navigate to="/insights" replace />} />
    </Routes>
  );
};
```

---

### Example 2: InsightsPage URL Detection

**File**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-insights/src/components/InsightsPage.tsx`

```tsx
export const InsightsPage: React.FC = () => {
  const { analysisId, analysisIdA, analysisIdB, comparisonId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const [viewMode, setViewMode] = useState<'analysis' | 'comparison'>('analysis');

  // Handle deep linking via URL params
  useEffect(() => {
    if (analysisId) {
      handleLoadAnalysis(analysisId);
      setViewMode('analysis');
      return;
    }

    if (comparisonId) {
      setComparisonToView(comparisonId);
      setViewMode('comparison');
      return;
    }

    if (analysisIdA && analysisIdB) {
      setPreselectedAnalysisA(analysisIdA);
      setPreselectedAnalysisB(analysisIdB);
      setViewMode('comparison');
      return;
    }

    if (location.pathname.includes('/compare')) {
      setViewMode('comparison');
      return;
    }

    if (location.pathname === '/insights' || location.pathname === '/insights/') {
      setViewMode('analysis');
    }
  }, [analysisId, analysisIdA, analysisIdB, comparisonId, location.pathname]);

  return (
    <div>
      {viewMode === 'analysis' && <AnalysisView />}
      {viewMode === 'comparison' && <ComparisonView />}
    </div>
  );
};
```

**Key Techniques**:
1. Use `useParams` to extract route parameters
2. Use `location.pathname` to detect pathname changes
3. Use `useEffect` with dependencies to react to URL changes
4. Handle all possible route combinations
5. Set view mode based on URL state

---

### Example 3: HistorySection Navigation

**File**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-insights/src/components/sections/HistorySection.tsx`

```tsx
export const HistorySection: React.FC<Props> = ({ onSelectAnalysis, onCompareAnalyses }) => {
  const navigate = useNavigate();

  return (
    <table>
      <tbody>
        {history.map((item) => (
          <tr key={item.id}>
            <td>{item.transcript_title}</td>
            <td>
              <button
                onClick={() => navigate(`/insights/analysis/${item.id}`)}
                className="text-[#FF385C] hover:underline"
              >
                View
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
```

**Key Points**:
- Use `navigate()` directly in click handler
- Use absolute paths (`/insights/analysis/${id}`)
- No callback prop needed (optional for analytics)

---

### Example 4: ComparisonHistory Navigation

**File**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-insights/src/components/comparison/ComparisonHistory.tsx`

```tsx
export const ComparisonHistory: React.FC<Props> = ({ onViewComparison }) => {
  const navigate = useNavigate();

  return (
    <table>
      <tbody>
        {comparisons.map((comparison) => (
          <tr key={comparison.id}>
            <td>{comparison.model_a_summary} vs {comparison.model_b_summary}</td>
            <td>
              <button
                onClick={() => navigate(`/insights/comparisons/${comparison.id}`)}
                title="View comparison"
              >
                <Eye className="h-4 w-4 text-blue-600" />
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
```

---

### Example 5: ComparisonPage Sub-Navigation

**File**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-insights/src/components/pages/ComparisonPage.tsx`

```tsx
export const ComparisonPage: React.FC<Props> = ({
  comparisonId,
  preselectedAnalysisAId,
  preselectedAnalysisBId,
  onBack,
}) => {
  const navigate = useNavigate();

  const handleComparisonCreated = (comparisonId: string) => {
    // Navigate to the comparison deep link
    navigate(`/insights/comparisons/${comparisonId}`);
  };

  const handleBackToList = () => {
    // Navigate back to comparison history
    navigate('/insights/compare');
  };

  return (
    <div>
      <button onClick={handleBackToList}>
        Back to History
      </button>

      {comparisonId ? (
        <ComparisonResults comparisonId={comparisonId} />
      ) : (
        <ComparisonSelector
          onComparisonCreated={handleComparisonCreated}
          preselectedAnalysisAId={preselectedAnalysisAId}
          preselectedAnalysisBId={preselectedAnalysisBId}
        />
      )}
    </div>
  );
};
```

**Key Techniques**:
1. Accept props for deep linking (`comparisonId`)
2. Use `navigate()` in event handlers
3. Provide `onBack` callback for parent navigation
4. Use absolute paths for all navigation

---

## Testing Checklist

Use this checklist to verify deep linking implementation:

### Functional Testing

- [ ] **Direct URL Access**: Enter deep link URL directly in browser → Page loads correctly
- [ ] **Page Refresh**: Navigate to deep link, refresh page → State persists
- [ ] **Bookmark**: Bookmark a deep link, close browser, reopen bookmark → Page loads correctly
- [ ] **Browser Back**: Navigate between pages, press back button → Previous page loads
- [ ] **Browser Forward**: Press back, then forward → Next page loads
- [ ] **Share Link**: Copy URL, paste in new tab → Same page loads
- [ ] **404 Handling**: Enter invalid URL → Redirects to MFE home or 404 page

### Technical Testing

- [ ] **URL Updates**: Click navigation elements → Browser URL changes immediately
- [ ] **No Duplicate Router**: Console has no "nested Router" errors
- [ ] **No Relative Paths**: All `navigate()` calls use absolute paths (`/mfe-name/...`)
- [ ] **historyApiFallback**: Dev server returns index.html for deep links
- [ ] **publicPath Auto**: Module Federation chunks load correctly
- [ ] **Shared Router**: react-router-dom is singleton shared dependency
- [ ] **Base Href**: Shell index.html has `<base href="/">`

### User Experience Testing

- [ ] **Loading States**: Deep links show loading spinner while fetching data
- [ ] **Error States**: Invalid IDs in URL show error message (not blank page)
- [ ] **Empty States**: Missing data shows helpful empty state
- [ ] **Accessibility**: All navigation is keyboard accessible
- [ ] **Screen Reader**: Screen reader announces route changes

### Edge Cases

- [ ] **Missing ID**: `/insights/analysis/` (no ID) → Redirects to home
- [ ] **Invalid ID**: `/insights/analysis/invalid-uuid` → Shows error message
- [ ] **Concurrent Navigation**: Rapid clicks don't break routing
- [ ] **Query Params**: `/insights?search=test` → Query params preserved
- [ ] **Hash Links**: `/insights#section` → Hash navigation works
- [ ] **External Links**: Links to other MFEs work (`/projects`, `/evaluations`)

---

## Summary

### Must-Have Patterns

1. **Shell owns BrowserRouter, MFE uses Routes**
2. **Always use absolute paths in navigate()**
3. **Use useEffect to react to URL changes**
4. **Update URL before API calls**
5. **Include 404 fallback route**
6. **Configure historyApiFallback and publicPath: 'auto'**
7. **Share react-router-dom as singleton**

### Anti-Patterns to Avoid

1. ❌ Adding BrowserRouter in MFE
2. ❌ Using relative paths in navigate()
3. ❌ Callback-only navigation (no URL update)
4. ❌ Updating URL after data loads
5. ❌ Missing error/loading states for deep links
6. ❌ Not handling URL parameter changes in useEffect
7. ❌ Missing 404 fallback route

### Reference Implementation

**mfe-insights** is the **gold standard** for deep linking patterns. When implementing routing in other MFEs, refer to:
- `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-insights/src/AppRouter.tsx`
- `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-insights/src/components/InsightsPage.tsx`
- `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-insights/src/components/sections/HistorySection.tsx`
- `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-insights/src/components/comparison/ComparisonHistory.tsx`

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-12
**Maintained By**: UX Specialist Agent
**Next Review**: 2026-01-12
