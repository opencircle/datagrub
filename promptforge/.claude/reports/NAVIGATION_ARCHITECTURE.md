# Navigation Architecture Document

**Version**: 1.0.0
**Date**: 2025-10-12
**Status**: PROPOSED
**Priority**: P1 (HIGH)

---

## Overview

This document defines the **unified navigation structure** for PromptForge, including breadcrumb navigation, sidebar navigation, quick actions, and navigation best practices to ensure consistent user experience across all micro-frontends.

---

## Navigation Hierarchy

### Primary Navigation (Sidebar)

**Location**: Left sidebar, visible on all authenticated pages

**Structure**:
```
PromptForge
├── 🏠 Dashboard
├── 📁 Projects
├── 🧠 Insights
├── 🎮 Playground
├── ✅ Evaluations
├── 📊 Traces
├── 🤖 Models
└── 🛡️ Policy
```

**Implementation**: Already exists in Shell (`MainLayout.tsx`)

---

### Secondary Navigation (Breadcrumbs)

**Location**: Top of page content area, below any page-level actions

**Purpose**: Show current location in hierarchy, enable quick navigation up levels

**Design Pattern**:
```
Home > Parent > Child > Current Page
  ↑       ↑       ↑           ↑
Link    Link    Link    Non-clickable (current)
```

**Visual Design**:
- **Separator**: ChevronRight icon (>) with neutral-400 color
- **Links**: Neutral-600 text, hover:neutral-900
- **Current**: Neutral-900 font-medium (not clickable)
- **Home**: Home icon + "Home" text, links to /dashboard
- **Spacing**: gap-2 between items
- **Font**: text-sm (14px)

---

## Breadcrumb Implementation

### Component

**File**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/shared/components/navigation/Breadcrumb.tsx`

```typescript
import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export interface BreadcrumbItem {
  label: string;
  href?: string;
  truncate?: boolean; // Truncate long labels
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ items }) => {
  return (
    <nav
      className="flex items-center gap-2 text-sm text-neutral-600 mb-6"
      aria-label="Breadcrumb"
    >
      {/* Home link */}
      <Link
        to="/dashboard"
        className="flex items-center gap-1 hover:text-neutral-900 transition-colors"
        aria-label="Home"
      >
        <Home className="h-4 w-4" />
        <span>Home</span>
      </Link>

      {/* Breadcrumb items */}
      {items.map((item, index) => {
        const isLast = index === items.length - 1;

        return (
          <React.Fragment key={index}>
            <ChevronRight className="h-4 w-4 text-neutral-400" aria-hidden="true" />

            {isLast || !item.href ? (
              <span
                className={`text-neutral-900 font-medium ${
                  item.truncate ? 'truncate max-w-[200px]' : ''
                }`}
                aria-current="page"
              >
                {item.label}
              </span>
            ) : (
              <Link
                to={item.href}
                className={`hover:text-neutral-900 transition-colors ${
                  item.truncate ? 'truncate max-w-[200px]' : ''
                }`}
              >
                {item.label}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};
```

---

### Usage Examples

#### Example 1: Projects > Project Detail

**Page**: `/projects/:projectId`

```typescript
import { Breadcrumb } from '../../../shared/components/navigation/Breadcrumb';

// In ProjectDetailPage
<Breadcrumb
  items={[
    { label: 'Projects', href: '/projects' },
    { label: project.name, truncate: true },
  ]}
/>
```

**Renders**:
```
Home > Projects > Customer Support Project
```

---

#### Example 2: Projects > Project > Prompts > Prompt Detail

**Page**: `/projects/:projectId/prompts/:promptId`

```typescript
<Breadcrumb
  items={[
    { label: 'Projects', href: '/projects' },
    { label: project.name, href: `/projects/${project.id}`, truncate: true },
    { label: 'Prompts', href: `/projects/${project.id}/prompts` },
    { label: prompt.name, truncate: true },
  ]}
/>
```

**Renders**:
```
Home > Projects > Customer Support > Prompts > Welcome Email Template
```

---

#### Example 3: Insights > Analysis Detail

**Page**: `/insights/analysis/:analysisId`

```typescript
<Breadcrumb
  items={[
    { label: 'Insights', href: '/insights' },
    { label: 'Analysis', href: '/insights/history' },
    { label: analysis.transcript_title || 'Untitled Analysis', truncate: true },
  ]}
/>
```

**Renders**:
```
Home > Insights > Analysis > Customer Support Call - Oct 12
```

---

#### Example 4: Traces > Trace Detail > Spans

**Page**: `/traces/:traceId/spans`

```typescript
<Breadcrumb
  items={[
    { label: 'Traces', href: '/traces' },
    { label: `Trace ${trace.request_id}`, href: `/traces/${trace.id}`, truncate: true },
    { label: 'Spans' },
  ]}
/>
```

**Renders**:
```
Home > Traces > Trace req-abc123 > Spans
```

---

#### Example 5: Evaluations > Catalog > Category > Evaluation Detail

**Page**: `/evaluations/catalog/:evaluationId`

```typescript
<Breadcrumb
  items={[
    { label: 'Evaluations', href: '/evaluations' },
    { label: 'Catalog', href: '/evaluations/catalog' },
    { label: evaluation.category, href: `/evaluations/catalog/${evaluation.category}` },
    { label: evaluation.name, truncate: true },
  ]}
/>
```

**Renders**:
```
Home > Evaluations > Catalog > Factual Accuracy > Factual Consistency Check
```

---

## Breadcrumb Best Practices

### DO:
- ✅ Always start with "Home" (links to /dashboard)
- ✅ Show full navigation hierarchy (up to 5 levels)
- ✅ Truncate long labels (max 200px, use `truncate: true`)
- ✅ Make all segments except current page clickable
- ✅ Use semantic HTML (`<nav>`, `aria-label="Breadcrumb"`, `aria-current="page"`)
- ✅ Position breadcrumbs consistently (top of content, below header)

### DON'T:
- ❌ Don't make current page clickable
- ❌ Don't show breadcrumbs on dashboard (no parent)
- ❌ Don't use breadcrumbs for peer navigation (use tabs instead)
- ❌ Don't exceed 5 levels (simplify hierarchy if needed)
- ❌ Don't use generic labels ("Page 1", "Item 2")

---

## Quick Actions

### Page-Level Actions

**Location**: Top right of page header, aligned with page title

**Examples**:

**Projects List**:
```
[+ New Project]
```

**Project Detail**:
```
[Edit] [Delete]
```

**Insights Analysis Detail**:
```
[Compare] [Export] [Re-run]
```

**Traces Detail**:
```
[View Spans] [Evaluations] [Export]
```

**Design**:
- **Primary Action**: `bg-[#FF385C] text-white` (Create, Save, Run)
- **Secondary Action**: `border-2 border-[#FF385C] text-[#FF385C]` (Compare, Edit)
- **Tertiary Action**: `bg-neutral-100 text-neutral-700` (Export, Cancel)
- **Destructive Action**: `bg-[#C13515] text-white` (Delete)

---

### Context Menu Actions

**Trigger**: Right-click or three-dot menu icon on list items

**Examples**:

**Project Card**:
```
Edit Project
Delete Project
---
Create Prompt
View Prompts
---
Duplicate Project
Export Project
```

**Trace Row**:
```
View Details
View Spans
View Evaluations
---
Copy Trace ID
Export Trace
---
Re-run Trace
```

**Implementation**:
```typescript
import { Menu } from '@headlessui/react';
import { MoreVertical, Edit2, Trash2, Copy, Download } from 'lucide-react';

<Menu as="div" className="relative">
  <Menu.Button className="p-2 hover:bg-neutral-100 rounded-lg transition-colors">
    <MoreVertical className="h-5 w-5 text-neutral-600" />
  </Menu.Button>

  <Menu.Items className="absolute right-0 mt-2 w-48 bg-white rounded-xl border border-neutral-200 shadow-lg py-2 z-50">
    <Menu.Item>
      {({ active }) => (
        <button
          onClick={handleEdit}
          className={`w-full flex items-center gap-2 px-4 py-2 text-sm ${
            active ? 'bg-neutral-50' : ''
          }`}
        >
          <Edit2 className="h-4 w-4 text-neutral-600" />
          Edit
        </button>
      )}
    </Menu.Item>

    <div className="border-t border-neutral-100 my-1" />

    <Menu.Item>
      {({ active }) => (
        <button
          onClick={handleDelete}
          className={`w-full flex items-center gap-2 px-4 py-2 text-sm text-[#C13515] ${
            active ? 'bg-[#C13515]/5' : ''
          }`}
        >
          <Trash2 className="h-4 w-4" />
          Delete
        </button>
      )}
    </Menu.Item>
  </Menu.Items>
</Menu>
```

---

## Tab Navigation

**When to Use**: For switching between related views on the same resource.

**Examples**:
- Evaluations: Results | Catalog | Create
- Models: Providers | Analytics
- Policy: Policies | Violations

**Implementation Pattern**:

```typescript
import { useSearchParams, useNavigate } from 'react-router-dom';

const [searchParams] = useSearchParams();
const navigate = useNavigate();
const activeTab = searchParams.get('tab') || 'results';

const tabs = [
  { id: 'results', label: 'Results', icon: LineChart },
  { id: 'catalog', label: 'Catalog', icon: BookOpen },
  { id: 'create', label: 'Create', icon: Plus },
];

<div className="border-b border-neutral-200">
  <nav className="flex gap-3">
    {tabs.map((tab) => {
      const Icon = tab.icon;
      return (
        <button
          key={tab.id}
          onClick={() => navigate(`?tab=${tab.id}`)}
          className={`
            h-11 px-4 py-2.5 border-b-2 font-semibold text-sm flex items-center gap-2 transition-all duration-200
            ${activeTab === tab.id
              ? 'border-[#FF385C] text-[#FF385C]'
              : 'border-transparent text-neutral-600 hover:text-neutral-800 hover:border-neutral-300'
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
```

**Best Practices**:
- Store active tab in URL query parameter: `?tab=results`
- Use semantic icons for each tab
- Highlight active tab with border-bottom and primary color
- Animate tab indicator with `transition-all duration-200`

---

## Back Navigation

### Browser Back Button

**Requirement**: MUST work correctly for all routes.

**Implementation**: Use React Router's `<Link>` and `useNavigate()` ONLY. Never use `window.location`.

**Testing**:
1. Navigate: Projects > Project Detail > Prompt Detail
2. Click browser back button
3. Should return to Project Detail (NOT dashboard)

---

### Explicit Back Button

**When to Use**: Detail pages, modals converted to routes

**Design**:
```typescript
<button
  onClick={() => navigate('/parent-route')}
  className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 mb-6 font-medium transition-colors"
>
  <ArrowLeft className="h-4 w-4" />
  Back to Parent
</button>
```

**Examples**:
- Analysis Detail: "Back to Insights"
- Trace Detail: "Back to Traces"
- Project Detail: "Back to Projects"

**Best Practice**: Place back button ABOVE breadcrumbs, aligned left.

---

## Keyboard Shortcuts

### Global Shortcuts

| Shortcut | Action | Context |
|----------|--------|---------|
| `Cmd/Ctrl + K` | Focus search | Any page with search |
| `g + i` | Go to Insights | Any page |
| `g + t` | Go to Traces | Any page |
| `g + p` | Go to Projects | Any page |
| `g + e` | Go to Evaluations | Any page |
| `g + d` | Go to Dashboard | Any page |
| `Esc` | Close modal/drawer | Any modal/drawer |
| `/` | Focus search | Any page with search |

### List Shortcuts

| Shortcut | Action | Context |
|----------|--------|---------|
| `↑` / `↓` | Navigate rows | Tables/lists |
| `Enter` | Open selected item | Tables/lists |
| `Cmd/Ctrl + A` | Select all | Multi-select lists |
| `Cmd/Ctrl + D` | Deselect all | Multi-select lists |

### Implementation

**File**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/shared/hooks/useKeyboardShortcuts.ts`

```typescript
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export function useKeyboardShortcuts() {
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if input/textarea focused
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      // Cmd/Ctrl + K: Focus search
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector<HTMLInputElement>('[data-search-input]');
        searchInput?.focus();
      }

      // /: Focus search
      if (e.key === '/' && !e.metaKey && !e.ctrlKey && !e.shiftKey) {
        e.preventDefault();
        const searchInput = document.querySelector<HTMLInputElement>('[data-search-input]');
        searchInput?.focus();
      }

      // g + [key]: Go to page (vim-style)
      if (e.key === 'g' && !e.metaKey && !e.ctrlKey) {
        const nextKeyPromise = new Promise<string>((resolve) => {
          const handler = (e: KeyboardEvent) => {
            resolve(e.key);
            document.removeEventListener('keydown', handler);
          };
          document.addEventListener('keydown', handler);
          setTimeout(() => resolve(''), 1000); // 1s timeout
        });

        nextKeyPromise.then((key) => {
          if (key === 'i') navigate('/insights');
          if (key === 't') navigate('/traces');
          if (key === 'p') navigate('/projects');
          if (key === 'e') navigate('/evaluations');
          if (key === 'd') navigate('/dashboard');
        });
      }

      // Esc: Close modal (handled by modal component)
      if (e.key === 'Escape') {
        // Dispatch custom event for modal components to listen
        window.dispatchEvent(new CustomEvent('closeModal'));
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [navigate]);
}
```

**Usage**:
```typescript
import { useKeyboardShortcuts } from '../../../shared/hooks/useKeyboardShortcuts';

export const App: React.FC = () => {
  useKeyboardShortcuts();

  return <AppRouter />;
};
```

---

## URL State Management

### Pattern: useSearchParams Hook

**Best Practice**: Store all transient UI state in URL query parameters.

**Examples**:
- Filters: `?model=gpt-4&status=error`
- Search: `?search=customer`
- Pagination: `?page=2&page_size=20`
- Sort: `?sort=date&order=desc`
- Tabs: `?tab=results`

**Implementation**:
```typescript
import { useSearchParams } from 'react-router-dom';

const [searchParams, setSearchParams] = useSearchParams();

// Read
const search = searchParams.get('search') || '';
const page = parseInt(searchParams.get('page') || '1');

// Write (replaces all params)
setSearchParams({ search: 'new query', page: '1' });

// Write (updates specific param)
const newParams = new URLSearchParams(searchParams);
newParams.set('page', '2');
setSearchParams(newParams);

// Delete param
const newParams = new URLSearchParams(searchParams);
newParams.delete('search');
setSearchParams(newParams);
```

**Benefits**:
- State preserved on refresh
- Bookmarkable URLs
- Shareable URLs
- Browser back/forward works
- React Query caches by URL params (no duplicate API calls)

---

## Navigation Testing

### Unit Tests

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

describe('Navigation', () => {
  it('should navigate to detail page on row click', () => {
    const { container } = render(
      <MemoryRouter initialEntries={['/traces']}>
        <Routes>
          <Route path="/traces" element={<TracesListPage />} />
          <Route path="/traces/:traceId" element={<TraceDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    fireEvent.click(screen.getByText('Trace-123'));
    expect(screen.getByText('Trace Detail')).toBeInTheDocument();
  });

  it('should preserve URL state on back navigation', () => {
    const { container } = render(
      <MemoryRouter initialEntries={['/traces?model=gpt-4&page=2']}>
        <Routes>
          <Route path="/traces" element={<TracesListPage />} />
          <Route path="/traces/:traceId" element={<TraceDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Navigate to detail
    fireEvent.click(screen.getByText('Trace-123'));

    // Navigate back
    fireEvent.click(screen.getByText('Back to Traces'));

    // Verify URL state preserved
    expect(window.location.search).toContain('model=gpt-4');
    expect(window.location.search).toContain('page=2');
  });
});
```

### E2E Tests

```typescript
describe('Navigation', () => {
  it('should support deep linking', () => {
    cy.visit('/insights/analysis/550e8400-e29b-41d4-a716-446655440000');
    cy.contains('Analysis Detail').should('be.visible');
  });

  it('should display breadcrumbs correctly', () => {
    cy.visit('/projects/proj-123/prompts/prompt-456');
    cy.contains('Home').should('be.visible');
    cy.contains('Projects').should('be.visible');
    cy.contains('Prompts').should('be.visible');
  });

  it('should navigate via keyboard shortcuts', () => {
    cy.visit('/dashboard');
    cy.type('gi'); // g + i
    cy.url().should('include', '/insights');
  });

  it('should work with browser back button', () => {
    cy.visit('/traces');
    cy.contains('Trace-123').click();
    cy.go('back');
    cy.url().should('eq', Cypress.config().baseUrl + '/traces');
  });
});
```

---

## Accessibility Requirements

### WCAG 2.1 AAA Compliance

**Navigation Components**:
- Breadcrumbs: `<nav aria-label="Breadcrumb">`
- Current page: `aria-current="page"`
- Skip links: Provide skip to main content link
- Keyboard navigation: All interactive elements accessible via Tab
- Focus indicators: Visible focus rings on all links/buttons

**Example**:
```typescript
<nav aria-label="Breadcrumb">
  <ol>
    <li>
      <Link to="/dashboard" aria-label="Home">Home</Link>
    </li>
    <li aria-current="page">Projects</li>
  </ol>
</nav>
```

**Keyboard Navigation Requirements**:
- Tab: Move to next focusable element
- Shift+Tab: Move to previous focusable element
- Enter: Activate link/button
- Space: Activate button
- Esc: Close modal/drawer

---

## Summary

**Key Navigation Principles**:
1. ✅ **Consistent Breadcrumbs**: Every page except dashboard
2. ✅ **URL State Management**: All filters, search, pagination in URL
3. ✅ **Browser Back Button**: Must work correctly
4. ✅ **Keyboard Shortcuts**: Global shortcuts for power users
5. ✅ **Deep Linking**: Every feature state must be bookmarkable
6. ✅ **Accessibility**: WCAG AAA compliance for all navigation

---

**End of Navigation Architecture Document**
