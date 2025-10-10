# PromptForge Architecture

## Overview

PromptForge is built using a **Micro-Frontend Architecture** powered by Webpack 5 Module Federation. This architecture enables independent development, deployment, and scaling of feature modules while maintaining a cohesive user experience.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser (Port 3000)                       │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Shell Application                       │  │
│  │  ├─ Router (React Router v6)                              │  │
│  │  ├─ Layout (Sidebar, Header)                              │  │
│  │  ├─ State (Redux Toolkit)                                 │  │
│  │  ├─ Auth (Mock Login)                                     │  │
│  │  └─ Theme (Light/Dark Mode)                               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                    │
│          ┌───────────────────┴───────────────────┐              │
│          │    Module Federation (Webpack 5)      │              │
│          └───────────────────┬───────────────────┘              │
│                              │                                    │
│  ┌───────┬─────────┬─────────┼─────────┬─────────┬─────────┐  │
│  │       │         │         │         │         │         │  │
│  ▼       ▼         ▼         ▼         ▼         ▼         ▼  │
│ ┌─────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐           │
│ │Proj │ │Eval│ │Play│ │Trac│ │Poli│ │Mode│ │Future MFEs│    │
│ │ects │ │uate│ │grnd│ │ es │ │cy  │ │ls  │ │ ...       │    │
│ │3001 │ │3002│ │3003│ │3004│ │3005│ │3006│ │           │    │
│ └─────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └───────────┘    │
└───────────────────────────────────────────────────────────────┘
```

## Core Principles

### 1. **Micro-Frontend Pattern**

Each feature module (MFE) is:
- **Independently developed** - Own repository, codebase, and team
- **Independently deployed** - Deploy without affecting other modules
- **Runtime integration** - Loaded dynamically via Module Federation
- **Technology agnostic** - Can use different frameworks (all use React in Phase 1)

### 2. **Module Federation**

Webpack 5's Module Federation enables:
- **Dynamic imports** - Load modules at runtime, not build time
- **Shared dependencies** - Single instance of React, Redux, etc.
- **Version management** - Control dependency versions per module
- **Build-time optimization** - Tree shaking, code splitting

### 3. **MVC Architecture**

Following classic MVC pattern:
- **Model (M):** Mock data, state management (Redux)
- **View (V):** React components, Tailwind CSS
- **Controller (C):** Event handlers, API calls, routing

## Component Architecture

### Shell Application (Host)

**Responsibilities:**
- Application shell and layout
- Global state management
- Authentication and authorization
- Routing and navigation
- Theme management
- Loading and error boundaries for MFEs

**Technology:**
- React 18.2 + TypeScript
- Redux Toolkit for state
- React Router for navigation
- Tailwind CSS for styling
- Framer Motion for animations

**Structure:**
```
shell/
├── src/
│   ├── components/
│   │   ├── Layout/
│   │   │   ├── Sidebar.tsx       # Navigation menu
│   │   │   ├── Header.tsx        # Top bar with user info
│   │   │   └── MainLayout.tsx    # Layout wrapper
│   │   └── RemoteComponents/
│   │       ├── ProjectsApp.tsx   # Projects MFE loader
│   │       ├── EvaluationsApp.tsx
│   │       └── ...               # Other MFE loaders
│   ├── pages/
│   │   ├── Login.tsx             # Login page
│   │   └── Dashboard.tsx         # Main dashboard
│   ├── store/
│   │   ├── index.ts              # Store configuration
│   │   └── slices/
│   │       ├── authSlice.ts      # Auth state
│   │       └── themeSlice.ts     # Theme state
│   ├── api/
│   │   └── mockAuth.ts           # Mock auth API
│   ├── App.tsx                   # Root component
│   └── index.tsx                 # Entry point
└── webpack.config.js             # Module Federation host config
```

### Micro-Frontends (Remotes)

Each MFE follows the same structure:

**Projects MFE (Port 3001)**
- Manage AI prompt projects
- Project CRUD operations
- Search and filtering
- Status tracking

**Evaluations MFE (Port 3002)**
- Run prompt evaluations
- Performance metrics
- Score tracking
- Test suite management

**Playground MFE (Port 3003)**
- Interactive prompt testing
- Multi-model support
- Parameter tuning
- Session history

**Traces MFE (Port 3004)**
- Request trace monitoring
- Multi-span visualization
- Error debugging
- Performance analysis

**Policy MFE (Port 3005)**
- Governance rule management
- Violation tracking
- Compliance monitoring
- Risk assessment

**Models MFE (Port 3006)**
- Model registry
- Provider management
- Pricing information
- Usage tracking

**Common MFE Structure:**
```
mfe-<name>/
├── src/
│   ├── App.tsx           # Main component
│   ├── index.tsx         # Entry point
│   ├── mockData.ts       # Mock data
│   └── index.css         # Styles
├── public/
│   └── index.html        # HTML template
├── webpack.config.js     # Module Federation remote config
├── package.json          # Dependencies
└── tsconfig.json         # TypeScript config
```

## State Management

### Global State (Redux Toolkit)

**Located in:** `shell/src/store/`

**Slices:**
1. **authSlice** - User authentication state
   ```typescript
   {
     user: User | null,
     isAuthenticated: boolean,
     loading: boolean
   }
   ```

2. **themeSlice** - UI theme state
   ```typescript
   {
     mode: 'light' | 'dark'
   }
   ```

**Why Redux?**
- Centralized state for cross-cutting concerns
- DevTools for debugging
- Time-travel debugging
- Middleware support

### Local State (React Hooks)

Each MFE manages its own local state using:
- `useState` - Component state
- `useEffect` - Side effects
- `useCallback` - Memoized callbacks
- `useMemo` - Memoized values

### Server State (TanStack Query)

**Currently configured, not yet used** (Phase 2)

Will manage:
- API data fetching
- Caching and invalidation
- Background refetching
- Optimistic updates

## Routing Architecture

### Shell-Level Routing

**React Router v6** handles top-level routes:

```typescript
<Routes>
  <Route path="/login" element={<Login />} />
  <Route path="/" element={<PrivateRoute><MainLayout /></PrivateRoute>}>
    <Route index element={<Navigate to="/dashboard" />} />
    <Route path="dashboard" element={<Dashboard />} />
    <Route path="projects" element={<ProjectsApp />} />
    <Route path="evaluations" element={<EvaluationsApp />} />
    <Route path="playground" element={<PlaygroundApp />} />
    <Route path="traces" element={<TracesApp />} />
    <Route path="policy" element={<PolicyApp />} />
    <Route path="models" element={<ModelsApp />} />
  </Route>
</Routes>
```

### Route Guards

**PrivateRoute Component:**
- Checks authentication status
- Redirects to login if not authenticated
- Preserves intended destination

### Navigation Flow

```
User clicks "Projects"
  → Router matches /projects route
  → Loads ProjectsApp component
  → Lazy loads projects/App module
  → Renders Projects MFE
```

## Module Federation Configuration

### Host Configuration (Shell)

```javascript
new ModuleFederationPlugin({
  name: 'shell',
  remotes: {
    projects: 'projects@http://localhost:3001/remoteEntry.js',
    evaluations: 'evaluations@http://localhost:3002/remoteEntry.js',
    playground: 'playground@http://localhost:3003/remoteEntry.js',
    traces: 'traces@http://localhost:3004/remoteEntry.js',
    policy: 'policy@http://localhost:3005/remoteEntry.js',
    models: 'models@http://localhost:3006/remoteEntry.js',
  },
  shared: {
    react: { singleton: true, requiredVersion: '^18.2.0' },
    'react-dom': { singleton: true, requiredVersion: '^18.2.0' },
    'react-router-dom': { singleton: true },
    '@reduxjs/toolkit': { singleton: true },
    'react-redux': { singleton: true },
  },
})
```

### Remote Configuration (MFE)

```javascript
new ModuleFederationPlugin({
  name: 'projects',
  filename: 'remoteEntry.js',
  exposes: {
    './App': './src/App',
  },
  shared: {
    react: { singleton: true, requiredVersion: '^18.2.0' },
    'react-dom': { singleton: true, requiredVersion: '^18.2.0' },
  },
})
```

## Data Flow

### Authentication Flow

```
1. User visits http://localhost:3000
2. App checks authSlice.isAuthenticated
3. If false, redirect to /login
4. User enters credentials
5. mockAuthAPI.login() validates (accepts any credentials)
6. Store token in localStorage
7. Dispatch loginSuccess(user) to Redux
8. Redirect to /projects
9. PrivateRoute allows access
10. Projects MFE loads
```

### MFE Loading Flow

```
1. User navigates to /projects
2. Router renders <ProjectsApp />
3. ProjectsApp lazy loads projects/App
4. Webpack fetches http://localhost:3001/remoteEntry.js
5. Module Federation resolves shared dependencies
6. Projects App.tsx renders
7. Mock data loaded from mockData.ts
8. UI renders with data
```

## Styling Architecture

### Tailwind CSS

**Configuration:**
- Shared design tokens via CSS variables
- Dark mode support via class strategy
- Responsive breakpoints
- Custom theme extensions

**CSS Variables (Shell):**
```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 222.2 47.4% 11.2%;
  --secondary: 210 40% 96.1%;
  /* ... */
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  /* ... */
}
```

### Component Styling

**Utility-First Approach:**
```tsx
<div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg">
  <h3 className="text-lg font-semibold mb-2">{project.name}</h3>
</div>
```

**Responsive Design:**
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
```

## Security Considerations

### Phase 1 (Current)

**Mock Security:**
- LocalStorage for session
- Accept any credentials
- No encryption
- No token validation

**⚠️ Not Production Ready**

### Phase 2+ (Planned)

**Real Security:**
- JWT tokens
- OAuth 2.0 / OIDC
- Secure HTTP-only cookies
- CSRF protection
- XSS sanitization
- Content Security Policy

## Performance Optimizations

### Code Splitting

- Route-based splitting via React.lazy()
- Dynamic imports for MFEs
- Webpack chunks for vendors

### Bundle Size

- Tree shaking enabled
- Shared dependencies (React singleton)
- Compression in production

### Runtime Performance

- React.memo for expensive components
- useMemo/useCallback for optimization
- Virtual scrolling (to be added)
- Lazy loading images

## Scalability

### Horizontal Scaling

**MFE Independence:**
- Each MFE can scale independently
- Different resource allocation per service
- Load balancing per MFE

**Future Architecture:**
```
          ┌──────────────┐
          │  Load Balancer│
          └───────┬───────┘
                  │
       ┏━━━━━━━━━┻━━━━━━━━━┓
       ▼                     ▼
  ┌─────────┐         ┌─────────┐
  │ Shell-1 │         │ Shell-2 │
  └─────────┘         └─────────┘
       │                     │
  ┌────┴─────┐         ┌────┴─────┐
  │ Projects │         │ Projects │
  │  Pod-1   │         │  Pod-2   │
  └──────────┘         └──────────┘
```

### Vertical Scaling

- Increase resources per service
- Optimize webpack builds
- CDN for static assets
- Caching strategies

## Testing Strategy

### Unit Tests (Planned)

- Jest for test runner
- React Testing Library for components
- Mock Service Worker for API

### Integration Tests (Planned)

- Cypress for E2E
- Test MFE integration
- Test routing flows

### Performance Tests (Planned)

- Lighthouse for metrics
- Bundle size tracking
- Load time monitoring

## Deployment Architecture

### Development

```
Local Machine
├── Shell (localhost:3000)
├── Projects MFE (localhost:3001)
├── Evaluations MFE (localhost:3002)
├── Playground MFE (localhost:3003)
├── Traces MFE (localhost:3004)
├── Policy MFE (localhost:3005)
└── Models MFE (localhost:3006)
```

### Production (Planned - Phase 4)

```
AWS Cloud
├── CloudFront CDN
│   ├── Shell (S3 + CloudFront)
│   ├── Projects MFE (S3 + CloudFront)
│   └── ... (other MFEs)
├── API Gateway
│   └── FastAPI Backend (ECS Fargate)
├── RDS PostgreSQL
└── ElastiCache Redis
```

## Future Enhancements

### Phase 2: Backend Integration

- FastAPI REST API
- PostgreSQL database
- Redis caching
- Real authentication

### Phase 3: Advanced Features

- WebSocket for real-time updates
- GraphQL for flexible queries
- Background jobs (Celery)
- File uploads (S3)

### Phase 4: Enterprise Features

- Multi-tenancy
- RBAC (Role-Based Access Control)
- SSO integration
- Audit logging
- SOC2 compliance

---

**PromptForge Architecture** - Built for scale, designed for simplicity.

*Phase 1 Complete - Micro-Frontend Foundation Established* 🏗️
