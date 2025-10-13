# Routing Best Practices for PromptForge

**Version**: 1.0.0
**Date**: 2025-10-12
**Audience**: UI Developers
**Status**: REQUIRED READING

---

## Overview

This document provides **coding guidelines and best practices** for implementing routing in PromptForge micro-frontends. Following these patterns ensures consistent behavior, prevents duplicate API calls, and maintains a high-quality user experience.

---

## Core Principles

### 1. Use React Router v6 ONLY

**DO**:
```typescript
import { useNavigate, Link, useSearchParams } from 'react-router-dom';

const navigate = useNavigate();
navigate('/projects/123');
```

**DON'T**:
```typescript
// ❌ NEVER use window.location (breaks SPA behavior)
window.location.href = '/projects/123';

// ❌ NEVER use <a href="..."> (full page reload)
<a href="/projects/123">View Project</a>

// ❌ NEVER use history.push (deprecated in v6)
history.push('/projects/123');
```

---

### 2. Store ALL UI State in URL

**DO**: Use URL query parameters for transient state
```typescript
// ✅ Filters in URL
/traces?model=gpt-4&status=error&page=2

// ✅ Search in URL
/projects?search=customer

// ✅ Sort in URL
/insights/history?sort=date&order=desc

// ✅ Tab state in URL
/evaluations?tab=catalog
```

**DON'T**: Use React state for shareable state
```typescript
// ❌ State lost on refresh
const [searchQuery, setSearchQuery] = useState('');
const [currentPage, setCurrentPage] = useState(1);
```

**WHY**: URL state is bookmarkable, shareable, and preserved on refresh.

---

### 3. Use Routes for Pages, Modals for Actions

**DO**: Detail views as routes
```typescript
// ✅ Bookmarkable detail page
<Route path="/traces/:traceId" element={<TraceDetailPage />} />
```

**DON'T**: Detail views as modals
```typescript
// ❌ Not bookmarkable
const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);

{selectedTraceId && (
  <Modal onClose={() => setSelectedTraceId(null)}>
    <TraceDetail id={selectedTraceId} />
  </Modal>
)}
```

**EXCEPTION**: Modals are OK for:
- Confirmations (Delete Project?)
- Quick edits (Rename File)
- Notifications (Success Toast)

---

### 4. React Query + URL State = No Duplicate API Calls

**Pattern**: React Query caches by URL parameters automatically.

**DO**:
```typescript
import { useSearchParams } from 'react-router-dom';
import { useTraces } from '../hooks/useTraces';

const [searchParams] = useSearchParams();
const model = searchParams.get('model') || '';
const page = parseInt(searchParams.get('page') || '1');

// React Query key includes URL params
const { data } = useTraces({
  model: model || undefined,
  page,
  page_size: 20,
});
```

**React Query Hook**:
```typescript
export const traceKeys = {
  all: ['traces'] as const,
  list: (filters: TraceFilters) => [...traceKeys.all, 'list', filters] as const,
};

export function useTraces(filters: TraceFilters) {
  return useQuery({
    queryKey: traceKeys.list(filters), // Cache key includes filters
    queryFn: () => fetchTraces(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

**Result**: Changing URL params triggers cache lookup first, avoids duplicate API calls.

---

### 5. Navigate Programmatically with useNavigate()

**DO**:
```typescript
import { useNavigate } from 'react-router-dom';

const navigate = useNavigate();

const handleRowClick = (traceId: string) => {
  navigate(`/traces/${traceId}`);
};
```

**DON'T**:
```typescript
// ❌ Don't use onClick handlers on divs
<div onClick={() => handleRowClick(trace.id)}>
  {trace.request_id}
</div>
```

**BETTER**: Use Link component (supports right-click "Open in new tab")
```typescript
import { Link } from 'react-router-dom';

<Link to={`/traces/${trace.id}`} className="...">
  {trace.request_id}
</Link>
```

---

### 6. Handle 404 Errors

**DO**: Add catch-all route in every MFE
```typescript
<Routes>
  <Route path="/" element={<HomePage />} />
  <Route path="/detail/:id" element={<DetailPage />} />

  {/* 404 catch-all - MUST be last */}
  <Route path="*" element={<Navigate to="/" replace />} />
</Routes>
```

**Alternatively**: Custom 404 page
```typescript
<Route path="*" element={<NotFoundPage />} />
```

---

### 7. Use Semantic Route Paths

**DO**: Descriptive, hierarchical paths
```typescript
// ✅ GOOD
/projects/:projectId/prompts/:promptId
/insights/analysis/:analysisId
/insights/compare/:idA/:idB
/traces/:traceId/spans

// ✅ GOOD query params
/traces?search=error&model=gpt-4&page=2
```

**DON'T**: Generic or flat paths
```typescript
// ❌ BAD
/page1
/item/:id
/view?type=detail&id=123
```

---

### 8. Update URL State Correctly

**Pattern**: Read from URL, write to URL

**DO**:
```typescript
import { useSearchParams } from 'react-router-dom';

const [searchParams, setSearchParams] = useSearchParams();

// Read
const search = searchParams.get('search') || '';

// Write (update single param)
const handleSearchChange = (value: string) => {
  const newParams = new URLSearchParams(searchParams);
  if (value) {
    newParams.set('search', value);
  } else {
    newParams.delete('search');
  }
  newParams.set('page', '1'); // Reset pagination on search
  setSearchParams(newParams);
};
```

**DON'T**: Mix state and URL
```typescript
// ❌ State and URL out of sync
const [search, setSearch] = useState('');
const [searchParams, setSearchParams] = useSearchParams();

const handleSearchChange = (value: string) => {
  setSearch(value); // Updates state
  setSearchParams({ search: value }); // Updates URL
  // Now state and URL are out of sync!
};
```

---

### 9. Preserve Context on Navigation

**Pattern**: Keep filters when navigating to detail and back.

**DO**:
```typescript
// User filters traces: /traces?model=gpt-4&page=2
// User clicks trace: /traces/trace-123
// User clicks back: /traces?model=gpt-4&page=2 (PRESERVED)
```

**Implementation**: React Router preserves URL params automatically when using `navigate()`.

**DON'T**: Clear params on navigation
```typescript
// ❌ Loses filters
const handleRowClick = (traceId: string) => {
  navigate(`/traces/${traceId}`);
  // When user goes back, filters are lost
};
```

---

### 10. Use Nested Routes for Hierarchy

**DO**: Nested routing reflects hierarchy
```typescript
<Routes>
  <Route path="/projects" element={<ProjectList />} />
  <Route path="/projects/:projectId" element={<ProjectDetail />} />
  <Route path="/projects/:projectId/prompts" element={<PromptsList />} />
  <Route path="/projects/:projectId/prompts/:promptId" element={<PromptDetail />} />
</Routes>
```

**Result**:
```
/projects
/projects/proj-123
/projects/proj-123/prompts
/projects/proj-123/prompts/prompt-456
```

---

## Common Patterns

### Pattern 1: List with Filters

**File**: TracesListPage.tsx

```typescript
import React from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useTraces } from '../hooks/useTraces';

export const TracesListPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  // Extract state from URL
  const search = searchParams.get('search') || '';
  const model = searchParams.get('model') || '';
  const page = parseInt(searchParams.get('page') || '1');

  // Fetch data (React Query caches by URL params)
  const { data, isLoading } = useTraces({
    search: search || undefined,
    model: model || undefined,
    page,
    page_size: 20,
  });

  // Update URL on filter change
  const handleSearchChange = (value: string) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
      newParams.set('search', value);
    } else {
      newParams.delete('search');
    }
    newParams.set('page', '1'); // Reset to page 1
    setSearchParams(newParams);
  };

  // Navigate to detail
  const handleRowClick = (traceId: string) => {
    navigate(`/traces/${traceId}`);
  };

  return (
    <div>
      <input
        value={search}
        onChange={(e) => handleSearchChange(e.target.value)}
        placeholder="Search traces..."
      />

      {data?.traces.map((trace) => (
        <div key={trace.id} onClick={() => handleRowClick(trace.id)}>
          {trace.request_id}
        </div>
      ))}
    </div>
  );
};
```

---

### Pattern 2: Detail Page with Back Navigation

**File**: TraceDetailPage.tsx

```typescript
import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useTraceDetail } from '../hooks/useTraces';
import { Breadcrumb } from '../../../shared/components/navigation/Breadcrumb';

export const TraceDetailPage: React.FC = () => {
  const { traceId } = useParams<{ traceId: string }>();
  const navigate = useNavigate();

  const { data: trace, isLoading, error } = useTraceDetail(traceId);

  // Update page title
  useEffect(() => {
    if (trace) {
      document.title = `Trace ${trace.request_id} - PromptForge`;
    }
  }, [trace]);

  if (isLoading) return <div>Loading...</div>;
  if (error || !trace) return <div>Trace not found</div>;

  return (
    <div>
      {/* Breadcrumbs */}
      <Breadcrumb
        items={[
          { label: 'Traces', href: '/traces' },
          { label: `Trace ${trace.request_id}` },
        ]}
      />

      {/* Back button */}
      <button
        onClick={() => navigate('/traces')}
        className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Traces
      </button>

      {/* Trace details */}
      <h1>{trace.request_id}</h1>
      <p>Duration: {trace.duration_ms}ms</p>
    </div>
  );
};
```

---

### Pattern 3: Tabs with URL State

**File**: EvaluationsPage.tsx

```typescript
import React from 'react';
import { useSearchParams } from 'react-router-dom';
import { LineChart, BookOpen, Plus } from 'lucide-react';

export const EvaluationsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') || 'results';

  const tabs = [
    { id: 'results', label: 'Results', icon: LineChart },
    { id: 'catalog', label: 'Catalog', icon: BookOpen },
    { id: 'create', label: 'Create', icon: Plus },
  ];

  return (
    <div>
      {/* Tab Navigation */}
      <div className="border-b border-neutral-200">
        <nav className="flex gap-3">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setSearchParams({ tab: tab.id })}
                className={`
                  h-11 px-4 py-2.5 border-b-2 font-semibold text-sm flex items-center gap-2
                  ${activeTab === tab.id
                    ? 'border-[#FF385C] text-[#FF385C]'
                    : 'border-transparent text-neutral-600'
                  }
                `}
              >
                <Icon className="h-5 w-5" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'results' && <ResultsTab />}
      {activeTab === 'catalog' && <CatalogTab />}
      {activeTab === 'create' && <CreateTab />}
    </div>
  );
};
```

---

### Pattern 4: Pre-filled Forms from URL

**Use Case**: Share link to playground with pre-configured parameters.

**URL**: `/playground?model=gpt-4&temp=0.7&max=1000&promptId=prompt-123`

**Implementation**:
```typescript
import React, { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

export const PlaygroundPage: React.FC = () => {
  const [searchParams] = useSearchParams();

  // Extract params from URL
  const presetModel = searchParams.get('model') || 'gpt-4o-mini';
  const presetTemp = parseFloat(searchParams.get('temp') || '0.7');
  const presetMax = parseInt(searchParams.get('max') || '500');
  const promptId = searchParams.get('promptId');

  const [model, setModel] = useState(presetModel);
  const [temperature, setTemperature] = useState(presetTemp);
  const [maxTokens, setMaxTokens] = useState(presetMax);
  const [prompt, setPrompt] = useState('');

  // Load prompt if promptId provided
  useEffect(() => {
    if (promptId) {
      fetchPrompt(promptId).then((data) => {
        setPrompt(data.template);
      });
    }
  }, [promptId]);

  return (
    <div>
      <select value={model} onChange={(e) => setModel(e.target.value)}>
        <option value="gpt-4o-mini">GPT-4o Mini</option>
        <option value="gpt-4">GPT-4</option>
      </select>

      <input
        type="range"
        value={temperature}
        onChange={(e) => setTemperature(parseFloat(e.target.value))}
        min="0"
        max="1"
        step="0.1"
      />

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter your prompt..."
      />
    </div>
  );
};
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Mixing Routing Libraries

**DON'T**:
```typescript
// ❌ NEVER mix React Router with other routing libraries
import { useHistory } from 'react-router-dom'; // v5
import { useNavigate } from 'react-router-dom'; // v6
```

**Result**: Conflicts, unexpected behavior.

---

### Anti-Pattern 2: Programmatic Navigation on Mount

**DON'T**:
```typescript
// ❌ NEVER navigate immediately on component mount
useEffect(() => {
  if (someCondition) {
    navigate('/other-page');
  }
}, []);
```

**Result**: Flashing screens, poor UX, infinite loops.

**BETTER**: Use redirects or conditional rendering
```typescript
if (someCondition) {
  return <Navigate to="/other-page" replace />;
}
```

---

### Anti-Pattern 3: Nested Navigate Calls

**DON'T**:
```typescript
// ❌ NEVER navigate multiple times in sequence
const handleSubmit = async () => {
  await saveData();
  navigate('/intermediate-page');
  navigate('/final-page'); // Only last navigate fires
};
```

**Result**: Only last `navigate()` executes.

---

### Anti-Pattern 4: Not Handling Loading States

**DON'T**:
```typescript
// ❌ NEVER show content before data loads
const { data } = useAnalysis(analysisId);

return <div>{data.title}</div>; // Crashes if data is undefined
```

**DO**:
```typescript
const { data, isLoading, error } = useAnalysis(analysisId);

if (isLoading) return <div>Loading...</div>;
if (error || !data) return <div>Not found</div>;

return <div>{data.title}</div>;
```

---

### Anti-Pattern 5: Hardcoded Routes in Components

**DON'T**:
```typescript
// ❌ NEVER hardcode routes
<Link to="/projects/proj-123">View Project</Link>
```

**DO**: Use dynamic paths
```typescript
<Link to={`/projects/${project.id}`}>View Project</Link>
```

---

## Testing Best Practices

### Unit Testing Routes

```typescript
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

describe('Routing', () => {
  it('should render detail page with ID from URL', () => {
    render(
      <MemoryRouter initialEntries={['/traces/trace-123']}>
        <Routes>
          <Route path="/traces/:traceId" element={<TraceDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText(/Trace trace-123/i)).toBeInTheDocument();
  });
});
```

---

### Testing URL State

```typescript
describe('URL State Management', () => {
  it('should update URL when filter changes', () => {
    const { getByPlaceholderText } = render(
      <MemoryRouter initialEntries={['/traces']}>
        <Routes>
          <Route path="/traces" element={<TracesListPage />} />
        </Routes>
      </MemoryRouter>
    );

    const searchInput = getByPlaceholderText('Search traces...');
    fireEvent.change(searchInput, { target: { value: 'error' } });

    expect(window.location.search).toContain('search=error');
  });
});
```

---

### E2E Testing Deep Links

```typescript
describe('Deep Linking', () => {
  it('should directly access analysis detail page', () => {
    cy.visit('/insights/analysis/550e8400-e29b-41d4-a716-446655440000');
    cy.contains('Analysis Detail').should('be.visible');
  });

  it('should preserve filters on refresh', () => {
    cy.visit('/traces?model=gpt-4&page=2');
    cy.reload();
    cy.url().should('include', 'model=gpt-4');
    cy.url().should('include', 'page=2');
  });
});
```

---

## Checklist: Before Merging Routing PR

- [ ] All routes defined in AppRouter.tsx
- [ ] URL state used for all filters, search, pagination, tabs
- [ ] React Query hooks use URL params in query keys
- [ ] No `window.location` usage
- [ ] All detail pages use routes (not modals)
- [ ] 404 catch-all route added
- [ ] Breadcrumbs implemented on all pages
- [ ] Back button works correctly
- [ ] Unit tests for routes added
- [ ] E2E tests for deep links added
- [ ] Keyboard shortcuts tested
- [ ] Accessibility (WCAG AAA) verified

---

## Quick Reference

### Import Statements

```typescript
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate, useSearchParams, useParams } from 'react-router-dom';
```

### Common Hooks

```typescript
// Navigation
const navigate = useNavigate();
navigate('/path');
navigate(-1); // Go back

// URL params (/traces/:traceId)
const { traceId } = useParams<{ traceId: string }>();

// Query params (/traces?search=error)
const [searchParams, setSearchParams] = useSearchParams();
const search = searchParams.get('search') || '';
setSearchParams({ search: 'new value' });
```

### Component Patterns

```typescript
// Link (supports right-click)
<Link to="/path">Go to Page</Link>

// Programmatic navigation
<button onClick={() => navigate('/path')}>Go</button>

// Conditional redirect
if (condition) return <Navigate to="/path" replace />;

// 404 catch-all
<Route path="*" element={<Navigate to="/" replace />} />
```

---

## Resources

**Official Docs**:
- React Router v6: https://reactrouter.com/en/main
- React Query: https://tanstack.com/query/latest

**PromptForge Docs**:
- [ROUTING_AUDIT_REPORT.md](./ROUTING_AUDIT_REPORT.md) - Current state analysis
- [PROMPTFORGE_SITE_MAP.md](./PROMPTFORGE_SITE_MAP.md) - Complete site map
- [DEEP_LINKING_IMPLEMENTATION_PLAN.md](./DEEP_LINKING_IMPLEMENTATION_PLAN.md) - Implementation guide
- [NAVIGATION_ARCHITECTURE.md](./NAVIGATION_ARCHITECTURE.md) - Navigation patterns

---

**End of Routing Best Practices**
