# Phase 2: UI Framework Standards & Best Practices

**Version**: 2.0
**Last Updated**: 2025-10-08
**Status**: Active
**Owner**: UI Architect Agent
**Related Documents**:
- `/ui-tier/DESIGN_SYSTEM.md` (Complete Claude.ai-inspired design specifications)
- `/ui-tier/FORM_FIELD_SPECS.md` (Form field spacing and layout specifications)

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [Client-Side Routing](#client-side-routing)
4. [State Management](#state-management)
5. [Design System](#design-system)
6. [Performance & Optimization](#performance--optimization)
7. [Accessibility](#accessibility)
8. [Security](#security)
9. [Testing Standards](#testing-standards)
10. [Module Federation Patterns](#module-federation-patterns)

---

## Overview

PromptForge UI Framework defines standards for building scalable, performant, and accessible micro-frontend applications using React, TypeScript, and Webpack Module Federation.

### Tech Stack

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Core** | React | ^18.2.0 | UI library |
| | TypeScript | ^5.3.3 | Type safety |
| | React Router | ^6.20.0 | Client-side routing |
| **State** | Redux Toolkit | ^2.0.1 | Global state |
| | React Query | ^5.12.0 | Server state |
| | Redux Persist | ^6.0.0 | State persistence |
| **Styling** | Tailwind CSS | ^3.4.0 | Utility-first CSS |
| | Framer Motion | ^11.0.0 | Animations |
| **Build** | Webpack | ^5.102.0 | Module bundler |
| | Module Federation | 5.x | Micro-frontends |
| **Testing** | Playwright | Latest | E2E tests |
| | Vitest | Latest | Unit tests |

---

## Architecture Principles

### 1. Micro-Frontend Architecture

**Structure**:
```
ui-tier/
├── shell/              # Host application (port 3000)
├── mfe-projects/       # Projects MFE (port 3001)
├── mfe-evaluations/    # Evaluations MFE (port 3002)
├── mfe-playground/     # Playground MFE (port 3003)
├── mfe-traces/         # Traces MFE (port 3004)
├── mfe-policy/         # Policy MFE (port 3005)
├── mfe-models/         # Models MFE (port 3006)
└── shared/             # Shared utilities (per MFE)
```

**Principles**:
- ✅ **Independent Deployment**: Each MFE can be deployed separately
- ✅ **Technology Agnostic**: MFEs can use different versions (with singleton constraints)
- ✅ **Shared Context**: React Query and authentication shared via Module Federation
- ✅ **Clear Boundaries**: Each MFE owns a specific domain

### 2. Component Hierarchy

```
App (Shell)
├── BrowserRouter (client-side routing)
├── Redux Provider (global state)
├── React Query Provider (server state)
└── Routes
    ├── Public Routes (login)
    └── Protected Routes (authenticated)
        ├── MainLayout (navigation, sidebar)
        └── Remote MFE Components
            └── MFE Internal Routing
```

### 3. Separation of Concerns

| Layer | Responsibility | Example |
|-------|---------------|---------|
| **UI Components** | Presentation only | `<Button>`, `<Card>`, `<Modal>` |
| **Container Components** | Logic, state, API calls | `<ProjectListContainer>` |
| **Services** | API integration | `projectService.ts` |
| **Hooks** | Reusable logic | `useProjects()`, `useAuth()` |
| **State** | Global/server state | Redux (UI), React Query (server) |

---

## Client-Side Routing

### 1. Routing Architecture

**Shell Router** (`/ui-tier/shell/src/App.tsx`):
```typescript
<BrowserRouter>
  <Routes>
    <Route path="/login" element={<LoginReal />} />
    <Route path="/" element={<PrivateRoute><MainLayout /></PrivateRoute>}>
      <Route index element={<Navigate to="/dashboard" />} />
      <Route path="dashboard" element={<Dashboard />} />
      <Route path="projects/*" element={<ProjectsApp />} />
      <Route path="evaluations/*" element={<EvaluationsApp />} />
      <Route path="playground/*" element={<PlaygroundApp />} />
      <Route path="traces/*" element={<TracesApp />} />
      <Route path="policy/*" element={<PolicyApp />} />
      <Route path="models/*" element={<ModelsApp />} />
    </Route>
  </Routes>
</BrowserRouter>
```

**MFE Router** (e.g., `/ui-tier/mfe-projects/src/AppRouter.tsx`):
```typescript
<Routes>
  <Route path="/" element={<ProjectList />} />
  <Route path="/:projectId" element={<ProjectDetail />} />
  <Route path="/prompt/:promptId" element={<PromptDetail />} />
  <Route path="*" element={<Navigate to="/" replace />} />
</Routes>
```

### 2. Browser Refresh Support ✅

**Requirement**: Page refresh should render the same page, not redirect to login.

**Implementation**:

#### Authentication Persistence
```typescript
// shell/src/App.tsx
useEffect(() => {
  const checkAuth = async () => {
    if (authService.isAuthenticated()) {
      try {
        const user = await authService.getCurrentUser();
        dispatch(loginSuccess(user));
      } catch (error) {
        authService.logout();
      }
    }
  };
  checkAuth();
}, [dispatch]);
```

#### Token Storage
```typescript
// shared/services/authService.ts
export const authService = {
  login(tokens) {
    localStorage.setItem('promptforge_access_token', tokens.access_token);
    localStorage.setItem('promptforge_refresh_token', tokens.refresh_token);
  },

  isAuthenticated() {
    return !!localStorage.getItem('promptforge_access_token');
  },

  logout() {
    localStorage.removeItem('promptforge_access_token');
    localStorage.removeItem('promptforge_refresh_token');
  }
};
```

### 3. History API Best Practices

#### Use `useNavigate` Hook
```typescript
import { useNavigate } from 'react-router-dom';

const MyComponent = () => {
  const navigate = useNavigate();

  const handleClick = () => {
    // Programmatic navigation
    navigate('/projects/123');

    // With state
    navigate('/projects/123', { state: { from: 'dashboard' } });

    // Replace (no history entry)
    navigate('/login', { replace: true });

    // Go back
    navigate(-1);
  };
};
```

#### Link Components
```typescript
import { Link, NavLink } from 'react-router-dom';

// Standard link
<Link to="/projects">Projects</Link>

// NavLink with active styling
<NavLink
  to="/projects"
  className={({ isActive }) => isActive ? 'active' : ''}
>
  Projects
</NavLink>
```

#### Preserve Scroll Position
```typescript
// App.tsx
<BrowserRouter>
  <ScrollRestoration />
  <Routes>...</Routes>
</BrowserRouter>

// Or custom scroll management
useEffect(() => {
  window.scrollTo(0, 0);
}, [location.pathname]);
```

### 4. URL State Management

#### Query Parameters
```typescript
import { useSearchParams } from 'react-router-dom';

const ProjectList = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const page = searchParams.get('page') || '1';
  const filter = searchParams.get('filter') || 'all';

  const updateFilter = (newFilter: string) => {
    setSearchParams({ page, filter: newFilter });
  };

  // URL: /projects?page=1&filter=active
};
```

#### Location State (Transient)
```typescript
import { useLocation } from 'react-router-dom';

// Sender
navigate('/project/123', { state: { previousPage: 'dashboard' } });

// Receiver
const location = useLocation();
const previousPage = location.state?.previousPage;
```

### 5. Protected Routes

```typescript
const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  const location = useLocation();

  if (!isAuthenticated) {
    // Redirect to login with return path
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

// Login component redirects back after auth
const LoginReal = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const from = location.state?.from?.pathname || '/dashboard';

  const handleLoginSuccess = () => {
    navigate(from, { replace: true });
  };
};
```

### 6. Route Guards

```typescript
// Role-based route guard
const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useSelector((state: RootState) => state.auth);

  if (user?.role !== 'admin') {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};

// Usage
<Route path="/admin/*" element={<AdminRoute><AdminPanel /></AdminRoute>} />
```

### 7. 404 Handling

```typescript
<Routes>
  {/* All defined routes */}
  <Route path="*" element={<NotFoundPage />} />
</Routes>

const NotFoundPage = () => {
  const navigate = useNavigate();

  return (
    <div>
      <h1>404 - Page Not Found</h1>
      <button onClick={() => navigate(-1)}>Go Back</button>
      <button onClick={() => navigate('/dashboard')}>Go to Dashboard</button>
    </div>
  );
};
```

---

## State Management

### 1. State Categories

| State Type | Tool | Purpose | Example |
|------------|------|---------|---------|
| **UI State** | React useState | Component-local state | Modal open/closed |
| **Global UI State** | Redux | Cross-component UI state | Theme, sidebar collapsed |
| **Server State** | React Query | API data, cache | Projects list, user profile |
| **Form State** | React Hook Form | Form inputs, validation | Login form, project creation |
| **URL State** | React Router | Shareable state | Page number, filters |

### 2. Redux Best Practices

#### Redux Persist Configuration
```typescript
import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';

const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['auth', 'theme'], // Only persist auth and theme
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
});

export const persistor = persistStore(store);
```

#### Redux Slice Pattern
```typescript
// authSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
}

const authSlice = createSlice({
  name: 'auth',
  initialState: { user: null, isAuthenticated: false },
  reducers: {
    loginSuccess: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
    },
  },
});

export const { loginSuccess, logout } = authSlice.actions;
export default authSlice.reducer;
```

### 3. React Query Best Practices

#### Centralized Hooks (REACT-QUERY-001)
```typescript
// shared/hooks/useProjects.ts
export const projectKeys = {
  all: ['projects'] as const,
  lists: () => [...projectKeys.all, 'list'] as const,
  detail: (id: string) => [...projectKeys.all, 'detail', id] as const,
};

export function useProjects() {
  return useQuery({
    queryKey: projectKeys.lists(),
    queryFn: projectService.getProjects,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: projectService.createProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
    },
  });
}
```

#### Optimistic Updates
```typescript
export function useUpdateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: projectService.updateProject,
    onMutate: async (updatedProject) => {
      await queryClient.cancelQueries({ queryKey: projectKeys.detail(updatedProject.id) });

      const previousProject = queryClient.getQueryData(projectKeys.detail(updatedProject.id));

      queryClient.setQueryData(projectKeys.detail(updatedProject.id), updatedProject);

      return { previousProject };
    },
    onError: (err, updatedProject, context) => {
      if (context?.previousProject) {
        queryClient.setQueryData(
          projectKeys.detail(updatedProject.id),
          context.previousProject
        );
      }
    },
    onSettled: (data, error, variables) => {
      queryClient.invalidateQueries({ queryKey: projectKeys.detail(variables.id) });
    },
  });
}
```

---

## Design System

> **📘 Complete Documentation**: See `/ui-tier/DESIGN_SYSTEM.md` for full Claude.ai-inspired design specifications with component examples, before/after comparisons, and accessibility guidelines.

### Design Principles

PromptForge follows the Claude.ai modern dashboard aesthetic:

1. **Clean Minimalism** - Generous whitespace, neutral backgrounds, strategic primary color usage
2. **Generous Spacing** - 8px grid system, larger padding (p-6 to p-8), increased gaps (gap-6)
3. **Soft Visual Style** - Rounded corners (rounded-xl/2xl), soft shadows, gentle transitions
4. **Clear Visual Hierarchy** - Bold headings (text-3xl), descriptive subtext (neutral-500)
5. **Accessible by Default** - WCAG AAA, large touch targets (h-11/h-12), high contrast
6. **Progressive Disclosure** - Hover reveals, subtle animations, clear empty states

### 1. Color Palette

#### Primary Colors
```jsx
--primary: #FF385C              /* Primary action color */
--primary-dark: #E31C5F         /* Hover state */

// Tailwind usage:
bg-[#FF385C]                    // Primary background
hover:bg-[#E31C5F]              // Primary hover
text-[#FF385C]                  // Primary text
border-[#FF385C]                // Primary border
ring-[#FF385C]/10               // Primary focus ring (10% opacity)
bg-[#FF385C]/5                  // Subtle primary background (5% opacity)
```

#### Neutral Colors (Warm Gray Scale)
```jsx
--neutral-50: #FAFAFA           /* Page background */
--neutral-100: #F5F5F5          /* Card hover, dividers */
--neutral-200: #E5E5E5          /* Borders */
--neutral-400: #A3A3A3          /* Placeholder text, icons */
--neutral-500: #737373          /* Secondary text */
--neutral-600: #525252          /* Less important text */
--neutral-700: #404040          /* Body text (lighter) */
--neutral-800: #262626          /* Headings */

// Tailwind usage:
bg-neutral-50                   // Page background (NOT white!)
bg-neutral-100                  // Hover backgrounds
border-neutral-100              // Very subtle borders
border-neutral-200              // Standard borders
text-neutral-400                // Placeholder
text-neutral-500                // Secondary text
text-neutral-700                // Body text
text-neutral-800                // Headings
```

#### Semantic Colors
```jsx
// Success
--success: #00A699
bg-[#00A699]/10 text-[#008489]  // Success badge

// Warning
--warning: #FFB400
bg-[#FFB400]/10 text-[#E6A200]  // Warning badge

// Error
--error: #C13515
bg-[#C13515]/5 text-[#C13515]   // Error background
```

### 2. Typography Scale

| Size | Class | Rem | Px | Usage |
|------|-------|-----|-----|-------|
| **XS** | `text-xs` | 0.75rem | 12px | Tags, meta info |
| **SM** | `text-sm` | 0.875rem | 14px | Secondary text, badges |
| **Base** | `text-base` | 1rem | 16px | Body text, inputs |
| **LG** | `text-lg` | 1.125rem | 18px | Card titles |
| **XL** | `text-xl` | 1.25rem | 20px | Modal titles |
| **3XL** | `text-3xl` | 1.875rem | 30px | **Page headings** |

**Font Weights:**
- `font-medium` (500): Less important labels
- `font-semibold` (600): Buttons, badges, navigation
- `font-bold` (700): Page headings, card titles

**Common Patterns:**
```jsx
// Page Heading
<h1 className="text-3xl font-bold text-neutral-800">Projects</h1>
<p className="text-neutral-500 mt-2 text-base">Manage your AI prompt projects</p>

// Card Title
<h3 className="text-lg font-bold text-neutral-800 mb-2 leading-snug">Card Title</h3>

// Label
<label className="text-sm font-semibold text-neutral-700 mb-2">Field Label</label>

// Secondary Text
<p className="text-sm text-neutral-500">Description text</p>
```

### 3. Spacing System (8px Grid)

**Tailwind Spacing Scale:**
```jsx
gap-2   // 8px   - Between tags/chips
gap-3   // 12px  - Between tabs
gap-4   // 16px  - Between form fields
gap-6   // 24px  - Between cards in grids

p-4     // 16px  - Small container padding
p-6     // 24px  - Standard card padding
p-8     // 32px  - Large container padding

space-y-4  // 16px vertical spacing
space-y-6  // 24px vertical spacing
space-y-8  // 32px vertical spacing (sections)

mb-2    // 8px   - Label to input gap
mb-3    // 12px  - Heading to description
mt-2    // 8px   - Description after heading
```

### 4. Border Radius

```jsx
rounded-lg     // 8px   - Small elements, tags
rounded-xl     // 12px  - Inputs, buttons, small cards
rounded-2xl    // 16px  - Large cards, sections
rounded-full   // 9999px - Avatars, pills
```

### 5. Shadows

**Use soft shadows only** (no hard edges):
```jsx
shadow-sm      // Subtle elevation
shadow-lg      // Card hover state
hover:shadow-lg // Hover effect
```

### 6. Component Standards

#### Button Component (h-11 = 44px touch target)
```jsx
<button className="h-11 px-4 py-2.5 rounded-xl font-semibold text-sm
  bg-[#FF385C] text-white hover:bg-[#E31C5F]
  focus:outline-none focus:ring-4 focus:ring-[#FF385C]/10
  transition-all duration-200">
  Button Text
</button>

// Secondary variant
<button className="h-11 px-4 py-2.5 rounded-xl font-semibold text-sm
  bg-neutral-100 text-neutral-700 hover:bg-neutral-200
  border border-neutral-200
  focus:outline-none focus:ring-4 focus:ring-neutral-300/20
  transition-all duration-200">
  Secondary
</button>
```

#### Input Component (h-12 = 48px touch target)
```jsx
<input className="w-full h-12 px-4 rounded-xl border border-neutral-200
  text-neutral-700 text-base bg-white
  focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10
  transition-all duration-200
  placeholder:text-neutral-400" />
```

#### Search Input with Icon (pl-14 for proper spacing)
```jsx
<div className="relative">
  <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400" />
  <input className="w-full h-12 pl-14 pr-4 rounded-xl border border-neutral-200
    text-neutral-700 text-base bg-white
    focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10
    transition-all duration-200
    placeholder:text-neutral-400"
    placeholder="Search..." />
</div>

// Formula: pl-14 = left-4 (16px icon position) + 20px (icon width) + 20px (gap) = 56px
```

#### Card Component
```jsx
<div className="bg-white border border-neutral-100 rounded-2xl p-6
  hover:shadow-lg hover:border-neutral-200
  transition-all duration-200 cursor-pointer">
  <h3 className="text-lg font-bold text-neutral-800 mb-2">Card Title</h3>
  <p className="text-sm text-neutral-500">Card description</p>
</div>
```

#### Metric/Stat Card
```jsx
<div className="bg-white border border-neutral-100 rounded-2xl p-6">
  <div className="flex items-center justify-between">
    <div>
      <p className="text-sm font-medium text-neutral-500 mb-2">Label</p>
      <p className="text-3xl font-bold text-neutral-800">1,234</p>
    </div>
    <div className="bg-neutral-50 p-3 rounded-xl">
      <Icon className="h-6 w-6 text-neutral-600" />
    </div>
  </div>
</div>
```

#### Tab Navigation (h-11 for 44px touch targets)
```jsx
<nav className="border-b border-neutral-200 flex gap-3">
  <button className="h-11 px-4 py-2.5 border-b-2 font-semibold text-sm
    flex items-center gap-2 transition-all duration-200
    border-[#FF385C] text-[#FF385C]">  {/* Active state */}
    <Icon className="h-5 w-5" />
    Active Tab
  </button>

  <button className="h-11 px-4 py-2.5 border-b-2 font-semibold text-sm
    flex items-center gap-2 transition-all duration-200
    border-transparent text-neutral-600
    hover:text-neutral-800 hover:border-neutral-300">  {/* Inactive state */}
    <Icon className="h-5 w-5" />
    Inactive Tab
  </button>
</nav>
```

#### Empty State
```jsx
<div className="flex flex-col items-center justify-center p-12 text-center">
  <div className="bg-neutral-100 rounded-2xl p-6 mb-4">
    <Icon className="h-12 w-12 text-neutral-400" />
  </div>
  <h3 className="text-lg font-semibold text-neutral-800 mb-2">No items yet</h3>
  <p className="text-sm text-neutral-500 mb-6 max-w-sm">
    Get started by creating your first item
  </p>
  <button className="h-11 px-4 rounded-xl bg-[#FF385C] text-white">
    Create Item
  </button>
</div>
```

---

## Performance & Optimization

### 1. Code Splitting

#### Route-Based Splitting
```typescript
import { lazy, Suspense } from 'react';

const ProjectsApp = lazy(() => import('./components/RemoteComponents/ProjectsApp'));

<Suspense fallback={<LoadingSpinner />}>
  <ProjectsApp />
</Suspense>
```

#### Component Splitting
```typescript
const HeavyComponent = lazy(() => import('./HeavyComponent'));

<Suspense fallback={<div>Loading...</div>}>
  {showHeavy && <HeavyComponent />}
</Suspense>
```

### 2. Memoization

#### React.memo
```typescript
export const ProjectCard = React.memo<ProjectCardProps>(({ project }) => {
  return <div>{project.name}</div>;
}, (prevProps, nextProps) => {
  return prevProps.project.id === nextProps.project.id;
});
```

#### useMemo & useCallback
```typescript
const filteredProjects = useMemo(() => {
  return projects.filter(p => p.name.includes(searchTerm));
}, [projects, searchTerm]);

const handleClick = useCallback(() => {
  navigate(`/projects/${projectId}`);
}, [projectId, navigate]);
```

### 3. Module Federation Optimization

```javascript
// webpack.config.js
new ModuleFederationPlugin({
  shared: {
    'react': { singleton: true, requiredVersion: '^18.2.0', eager: true },
    'react-dom': { singleton: true, requiredVersion: '^18.2.0', eager: true },
    '@tanstack/react-query': { singleton: true, requiredVersion: '^5.12.0' },
  },
});
```

### 4. Image Optimization

```typescript
<img
  src={project.image}
  alt={project.name}
  loading="lazy"
  width={300}
  height={200}
  srcSet={`${project.image}?w=300 300w, ${project.image}?w=600 600w`}
/>
```

---

## Accessibility (WCAG 2.1 AAA)

### 1. Contrast Ratios

- **Normal text (< 18px)**: 7:1 minimum
- **Large text (≥ 18px or 14px bold)**: 4.5:1 minimum
- **UI components**: 3:1 minimum

### 2. Keyboard Navigation

```typescript
const Modal = ({ isOpen, onClose, children }) => {
  useEffect(() => {
    if (!isOpen) return;

    // Trap focus
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'Tab') {
        // Focus trap logic
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  return (
    <div role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <h2 id="modal-title">{children}</h2>
    </div>
  );
};
```

### 3. ARIA Attributes

```typescript
<button
  aria-label="Delete project"
  aria-describedby="delete-help"
  aria-pressed={isSelected}
  disabled={isDeleting}
>
  <TrashIcon aria-hidden="true" />
</button>
<span id="delete-help" className="sr-only">
  This action cannot be undone
</span>
```

### 4. Screen Reader Support

```typescript
// Live region for dynamic updates
<div aria-live="polite" aria-atomic="true" className="sr-only">
  {`${projects.length} projects loaded`}
</div>

// Skip to content link
<a href="#main-content" className="sr-only focus:not-sr-only">
  Skip to main content
</a>
```

---

## Security

### 1. XSS Prevention

```typescript
// ✅ Good - React escapes by default
<div>{userInput}</div>

// ❌ Dangerous - Avoid dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{ __html: userInput }} />

// ✅ If needed, sanitize first
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userInput) }} />
```

### 2. Token Storage

```typescript
// ✅ httpOnly cookies (preferred for refresh tokens)
// Set by backend: Set-Cookie: refresh_token=...; HttpOnly; Secure; SameSite=Strict

// ✅ localStorage for access tokens (short-lived)
localStorage.setItem('promptforge_access_token', token);

// ❌ Never store sensitive data in localStorage without encryption
```

### 3. CSRF Protection

```typescript
// Include CSRF token in requests
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

fetch('/api/projects', {
  method: 'POST',
  headers: {
    'X-CSRF-Token': csrfToken,
    'Content-Type': 'application/json',
  },
});
```

---

## Testing Standards

### 1. Unit Tests (Vitest)

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### 2. E2E Tests (Playwright)

```typescript
import { test, expect } from '@playwright/test';

test('create project flow', async ({ page }) => {
  await page.goto('http://localhost:3000');

  // Login
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password');
  await page.click('button[type="submit"]');

  // Navigate to projects
  await page.click('text=Projects');
  await expect(page).toHaveURL(/.*projects/);

  // Create project
  await page.click('text=New Project');
  await page.fill('input[name="name"]', 'Test Project');
  await page.click('button:has-text("Create")');

  // Verify
  await expect(page.locator('text=Test Project')).toBeVisible();
});
```

---

## Module Federation Patterns

### 1. Bootstrap Pattern (MODULE-FEDERATION-002)

**Problem**: Remote MFEs need access to React Query context from shell.

**Solution**: Wrap MFE App with context providers before exposing.

```typescript
// mfe-playground/src/bootstrap.tsx
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import PlaygroundEnhanced from './PlaygroundEnhanced';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 5 * 60 * 1000, retry: 1 },
  },
});

export const WrappedApp: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <PlaygroundEnhanced />
    </QueryClientProvider>
  );
};

export default WrappedApp;
```

```javascript
// webpack.config.js
new ModuleFederationPlugin({
  name: 'playground',
  filename: 'remoteEntry.js',
  exposes: {
    './App': './src/bootstrap', // Expose bootstrap, not App directly
  },
});
```

### 2. Shared State Pattern

```javascript
// Shell provides shared state
shared: {
  'react': { singleton: true, eager: true },
  'react-dom': { singleton: true, eager: true },
  '@tanstack/react-query': { singleton: true, requiredVersion: '^5.12.0' },
  'react-redux': { singleton: true },
}
```

---

## Shared Components Library

### Location
All shared components are located in `/ui-tier/shared/components/` and are available to all MFEs.

### Component Structure
```
shared/components/
├── core/              # Base UI components
│   ├── Button.tsx
│   ├── Badge.tsx
│   └── Card.tsx
├── forms/             # Form-related components
│   ├── Input.tsx
│   ├── Textarea.tsx
│   ├── Select.tsx
│   └── EvaluationSelector.tsx  ⭐ NEW
└── charts/            # Data visualization
    └── (future components)
```

### EvaluationSelector Component ⭐ NEW

**Purpose**: Unified evaluation selection dropdown with filters, used across Playground and Insights pages.

**Location**: `/ui-tier/shared/components/forms/EvaluationSelector.tsx`

**Features**:
- **Dropdown Table View**: Shows evaluations in structured table with Name, Description, Category, Source, Tags, Type columns
- **Multi-Select**: Checkbox-based selection with visual feedback
- **Filters**: Category, Source, Tags filter controls
- **Selected Badges**: Shows selected evaluations as removable badges
- **Click-Outside Behavior**: Dropdown closes and filters reset when clicking outside
- **Loading States**: Spinner during data fetch
- **Empty States**: Clear messaging when no evaluations available or match filters
- **Accessibility**: Full keyboard navigation, ARIA labels, screen reader support

**Usage**:
```typescript
import { EvaluationSelector } from '../../../shared/components/forms/EvaluationSelector';

const MyComponent = () => {
  const [selectedEvaluationIds, setSelectedEvaluationIds] = useState<string[]>([]);

  return (
    <EvaluationSelector
      selectedEvaluationIds={selectedEvaluationIds}
      onSelectionChange={setSelectedEvaluationIds}
    />
  );
};
```

**Implementation Details**:
- Uses React Query to fetch evaluations from `evaluationCatalogService`
- Filters are applied client-side with `useMemo` for performance
- Click-outside detection via `useRef` + `useEffect` pattern
- Filters reset to initial view when dropdown closes
- Consistent styling with design system (neutral-* colors, rounded-xl, h-10 inputs)

**Styling Standards**:
```jsx
// Filter Controls
<select className="h-10 px-3 rounded-xl border border-neutral-200 text-sm
  bg-white hover:border-[#FF385C]
  focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10" />

// Dropdown Trigger
<button className="w-full h-10 px-3 rounded-xl border border-neutral-200
  bg-white hover:border-[#FF385C]
  focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10" />

// Selected Badges
<div className="bg-[#FF385C]/10 text-[#FF385C] border border-[#FF385C]/20
  text-xs px-2 py-1 rounded-lg" />

// Table Row (Selected)
<tr className="bg-[#FF385C]/5 hover:bg-neutral-50" />

// Checkbox (Selected)
<div className="bg-[#FF385C] border-[#FF385C]">
  <Check className="h-3 w-3 text-white" />
</div>
```

**Migration Pattern**:

**Before** (Insights with checkbox grid):
```jsx
<div className="grid grid-cols-2 gap-3">
  {evaluations.map(evaluation => (
    <label key={evaluation.id}>
      <input type="checkbox" />
      <div>{evaluation.name}</div>
    </label>
  ))}
</div>
```

**After** (Shared dropdown component):
```jsx
<EvaluationSelector
  selectedEvaluationIds={formState.selectedEvaluations}
  onSelectionChange={handleEvaluationChange}
/>
```

**Benefits**:
- ✅ Consistent UX across Playground and Insights
- ✅ Single source of truth for evaluation selection
- ✅ Easier to maintain and enhance
- ✅ Better filtering and search capabilities
- ✅ Improved accessibility

### Best Practices for Shared Components

1. **Export from Index**: Always export from `/shared/components/[category]/index.ts`
   ```typescript
   // shared/components/forms/index.ts
   export { EvaluationSelector } from './EvaluationSelector';
   export type { EvaluationSelectorProps } from './EvaluationSelector';
   ```

2. **Typed Props**: Export prop interfaces for type safety
   ```typescript
   export interface EvaluationSelectorProps {
     selectedEvaluationIds: string[];
     onSelectionChange: (ids: string[]) => void;
   }
   ```

3. **Self-Contained**: Components should manage their own data fetching when possible
   ```typescript
   // Fetch data inside component
   const { data: evaluations } = useQuery({
     queryKey: ['evaluation-catalog'],
     queryFn: evaluationCatalogService.getCatalog,
   });
   ```

4. **Design System Compliance**: All shared components must follow design system standards
   - Use neutral-* color palette (NOT gray-*)
   - Follow 8px spacing grid
   - WCAG AAA contrast ratios
   - Minimum h-11 (44px) touch targets
   - Ring-4 focus states with 10% opacity

5. **Documentation**: Include JSDoc comments with usage examples
   ```typescript
   /**
    * EvaluationSelector - Unified evaluation selection dropdown
    *
    * @example
    * <EvaluationSelector
    *   selectedEvaluationIds={ids}
    *   onSelectionChange={setIds}
    * />
    */
   ```

---

## Recommendations for Enhancement

### 1. Add Redux Persist ⭐ High Priority

**Why**: State (auth, theme) should survive page refresh.

```bash
npm install redux-persist
```

**Implementation**: See [State Management > Redux Persist](#redux-persist-configuration)

### 2. Add Scroll Restoration ⭐ Medium Priority

**Why**: Browser back button should restore scroll position.

```typescript
import { ScrollRestoration } from 'react-router-dom';

<BrowserRouter>
  <ScrollRestoration />
  <Routes>...</Routes>
</BrowserRouter>
```

### 3. Add Error Boundaries ⭐ High Priority

**Why**: Graceful error handling prevents white screen of death.

```typescript
class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback onReset={() => this.setState({ hasError: false })} />;
    }
    return this.props.children;
  }
}
```

### 4. Add Loading States ⭐ Medium Priority

**Why**: Better UX during async operations.

```typescript
import { Suspense } from 'react';
import { Outlet } from 'react-router-dom';

<Suspense fallback={<PageLoader />}>
  <Outlet />
</Suspense>
```

### 5. Add Offline Support 🔮 Future

**Why**: Progressive Web App capabilities.

```typescript
// service-worker.js
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
```

### 6. Add Analytics Integration 🔮 Future

**Why**: Track user behavior, errors, performance.

```typescript
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

export const usePageTracking = () => {
  const location = useLocation();

  useEffect(() => {
    // Track page view
    analytics.page(location.pathname);
  }, [location]);
};
```

### 7. Add Internationalization (i18n) 🔮 Future

**Why**: Multi-language support.

```typescript
import { useTranslation } from 'react-i18next';

const MyComponent = () => {
  const { t } = useTranslation();
  return <h1>{t('welcome.title')}</h1>;
};
```

---

## Migration Checklist

### Current State ✅
- [x] React Router v6 configured
- [x] BrowserRouter in shell
- [x] Protected routes with PrivateRoute
- [x] Authentication persistence via localStorage
- [x] Redux for global state
- [x] React Query for server state
- [x] Module Federation for micro-frontends
- [x] Tailwind CSS design system

### Recommended Additions 🚀

#### High Priority
- [ ] Add Redux Persist for state persistence
- [ ] Add Error Boundaries for error handling
- [ ] Add loading states/suspense boundaries
- [ ] Document scroll restoration behavior
- [ ] Add 404 page component

#### Medium Priority
- [ ] Add scroll restoration configuration
- [ ] Add route transition animations
- [ ] Add breadcrumb navigation
- [ ] Add route metadata (titles, descriptions)

#### Low Priority
- [ ] Add offline support / PWA
- [ ] Add analytics tracking
- [ ] Add internationalization (i18n)
- [ ] Add A/B testing framework

---

## UI Architect Integration

### Agent Responsibilities

When making UI changes, the UI Architect Agent must:

1. **Route Changes**
   - Follow History API best practices
   - Use `useNavigate` instead of `window.location`
   - Preserve state across navigations
   - Handle authentication redirects properly

2. **State Management**
   - Use Redux only for global UI state
   - Use React Query for server state
   - Use URL state for shareable state
   - Document any new state additions

3. **Design System**
   - Follow color palette (primary #FF385C)
   - Use 8px spacing grid
   - Maintain AAA contrast ratios
   - Use consistent border radius (rounded-xl)

4. **Accessibility**
   - Add proper ARIA labels
   - Ensure keyboard navigation works
   - Test with screen readers
   - Maintain focus management in modals

5. **Performance**
   - Lazy load heavy components
   - Use React.memo for expensive renders
   - Optimize images with lazy loading
   - Minimize bundle size

### Review Checklist

Before submitting changes, verify:

- [ ] Routes follow nested routing pattern
- [ ] Authentication state persists on refresh
- [ ] Browser back button works correctly
- [ ] URL state is shareable (can copy/paste URL)
- [ ] Loading states are shown during async operations
- [ ] Error states are handled gracefully
- [ ] Accessibility requirements met (WCAG AAA)
- [ ] Design system consistency maintained
- [ ] Performance optimization applied
- [ ] Tests updated (unit + E2E)

---

## Conclusion

This UI Framework establishes standards for building scalable, performant, and accessible micro-frontend applications. All UI development should follow these patterns to ensure consistency and quality.

**Next Steps**:
1. Implement Redux Persist
2. Add Error Boundaries
3. Document scroll restoration
4. Create 404 page component
5. Add comprehensive E2E tests

**Questions? Feedback?**
Contact: UI Architect Agent

---

**Version History**:
- v2.0 (2025-10-08): Added Claude.ai-inspired design system, shared components (EvaluationSelector), comprehensive component specifications
- v1.0 (2025-10-06): Initial framework specification with routing, state management, design system
