# PromptForge Site Map

**Version**: 1.0.0
**Date**: 2025-10-12
**Status**: PROPOSED (Target State)
**Current Implementation**: 5% complete (3 routes only)

---

## Navigation Hierarchy

```
PromptForge Application
├── Public Routes
│   └── /login
│       └── Login page (email/password authentication)
│
└── Authenticated Routes
    ├── / (Root)
    │   └── Redirect → /dashboard
    │
    ├── /dashboard
    │   └── Overview dashboard with quick actions
    │
    ├── /projects (mfe-projects)
    │   ├── / (Project List)
    │   │   ├── Query Params: ?search=<query>&status=<active|draft|archived>&page=<num>
    │   │   └── Actions: Create project, search, filter
    │   │
    │   ├── /:projectId (Project Detail)
    │   │   ├── Project metadata, prompts list
    │   │   └── Actions: Edit project, delete project, create prompt
    │   │
    │   ├── /:projectId/prompts (Prompts List) [NEW]
    │   │   ├── Query Params: ?search=<query>&category=<category>&page=<num>
    │   │   └── Actions: Create prompt, filter, search
    │   │
    │   ├── /:projectId/prompts/:promptId (Prompt Detail)
    │   │   ├── Prompt versions, variables, configurations
    │   │   └── Actions: Edit prompt, create version, run evaluation
    │   │
    │   ├── /:projectId/prompts/:promptId/versions (Version History) [NEW]
    │   │   ├── Version comparison, changelog
    │   │   └── Actions: Compare versions, rollback, create new version
    │   │
    │   └── /:projectId/prompts/:promptId/evaluate [NEW]
    │       ├── Run evaluation on prompt
    │       └── Actions: Select evaluations, run, view results
    │
    ├── /insights (mfe-insights)
    │   ├── / (Main Analysis Page)
    │   │   ├── Transcript input, parameter config, results
    │   │   └── Actions: Analyze transcript, view history, compare analyses
    │   │
    │   ├── /new (New Analysis) [NEW]
    │   │   ├── Query Params: ?transcript=<encoded>&model=<model>
    │   │   └── Actions: Submit analysis, configure parameters
    │   │
    │   ├── /analysis/:analysisId (Analysis Detail) [NEW]
    │   │   ├── Summary, insights, facts, traces, evaluations
    │   │   └── Actions: Edit title, compare, re-run, export
    │   │
    │   ├── /history (Analysis History) [NEW]
    │   │   ├── Query Params: ?search=<query>&filter=<last7days|last30days>&sort=<date|title|cost>&page=<num>
    │   │   └── Actions: View analysis, compare, delete, filter, search
    │   │
    │   ├── /compare (Comparison Selector) [NEW]
    │   │   ├── Query Params: ?analysisA=<id>&analysisB=<id>
    │   │   └── Actions: Select analyses, run comparison, view saved comparisons
    │   │
    │   ├── /compare/:analysisIdA/:analysisIdB (Ad-hoc Comparison) [NEW]
    │   │   ├── Side-by-side comparison of two analyses
    │   │   └── Actions: Save comparison, export, view analysis details
    │   │
    │   ├── /comparisons (Saved Comparisons) [NEW]
    │   │   ├── Query Params: ?search=<query>&sort=<date|title>&page=<num>
    │   │   └── Actions: View comparison, delete, filter
    │   │
    │   └── /comparisons/:comparisonId (Comparison Detail) [NEW]
    │       ├── Saved comparison results with blind judge verdict
    │       └── Actions: View analyses, re-run comparison, export
    │
    ├── /playground (mfe-playground)
    │   ├── / (Main Playground)
    │   │   ├── Query Params: ?model=<model>&temp=<temp>&max=<tokens>&promptId=<id>
    │   │   ├── Prompt editor, parameter sliders, response
    │   │   └── Actions: Run prompt, adjust parameters, view history
    │   │
    │   ├── /session/:sessionId (Session Detail) [NEW]
    │   │   ├── Specific playground session with prompt, parameters, response
    │   │   └── Actions: Re-run, edit parameters, compare sessions
    │   │
    │   ├── /history (Session History) [NEW]
    │   │   ├── Query Params: ?model=<model>&search=<query>&page=<num>
    │   │   └── Actions: View session, filter, search, delete
    │   │
    │   └── /compare/:sessionIdA/:sessionIdB (Compare Sessions) [NEW]
    │       ├── Side-by-side comparison of two sessions
    │       └── Actions: View differences, export
    │
    ├── /evaluations (mfe-evaluations)
    │   ├── / (Evaluation Dashboard)
    │   │   ├── Default view: Results tab
    │   │   └── Redirect → /evaluations/results
    │   │
    │   ├── /results (Evaluation Results) [NEW]
    │   │   ├── Query Params: ?search=<query>&filter=<passed|failed>&sort=<date|score>&page=<num>
    │   │   ├── Results table with filters, search, pagination
    │   │   └── Actions: View result, filter, search, run new evaluation
    │   │
    │   ├── /results/:evaluationId (Evaluation Result Detail) [NEW]
    │   │   ├── Detailed evaluation result with metrics, trace
    │   │   └── Actions: Re-run, export, view prompt, view trace
    │   │
    │   ├── /catalog (Evaluation Catalog) [NEW]
    │   │   ├── Query Params: ?category=<category>&search=<query>
    │   │   ├── Browse pre-built evaluations
    │   │   └── Actions: Select evaluation, view details, run evaluation
    │   │
    │   ├── /catalog/:category (Category View) [NEW]
    │   │   ├── Evaluations filtered by category (factual, security, quality, etc.)
    │   │   └── Actions: Select evaluation, view details
    │   │
    │   ├── /catalog/:evaluationId (Evaluation Detail) [NEW]
    │   │   ├── Evaluation description, parameters, examples
    │   │   └── Actions: Run evaluation, customize, add to favorites
    │   │
    │   ├── /create (Create Custom Evaluation) [NEW]
    │   │   ├── Query Params: ?type=<custom|template>
    │   │   ├── Form to create custom evaluation
    │   │   └── Actions: Save, test, cancel
    │   │
    │   ├── /custom (Custom Evaluations) [NEW]
    │   │   ├── List of user-created custom evaluations
    │   │   └── Actions: View, edit, delete, duplicate
    │   │
    │   └── /custom/:evaluationId (Custom Evaluation Detail) [NEW]
    │       ├── Custom evaluation configuration
    │       └── Actions: Edit, test, delete, run
    │
    ├── /traces (mfe-traces)
    │   ├── / (Traces List)
    │   │   ├── Query Params: ?search=<query>&model=<model>&source=<source>&status=<status>&page=<num>&sort=<field>&order=<asc|desc>
    │   │   ├── Traces table with multi-level filters
    │   │   └── Actions: View trace, filter, search, export
    │   │
    │   ├── /:traceId (Trace Detail) [NEW]
    │   │   ├── Trace overview, request/response, metadata
    │   │   └── Actions: View spans, view evaluations, export, re-run
    │   │
    │   ├── /:traceId/spans (Span Visualization) [NEW]
    │   │   ├── Detailed span timeline, waterfall chart
    │   │   └── Actions: View span details, export
    │   │
    │   ├── /:traceId/evaluations (Trace Evaluations) [NEW]
    │   │   ├── Evaluation results for this trace
    │   │   └── Actions: View evaluation details, re-run
    │   │
    │   └── /:traceId/parent-child (Parent-Child Visualization) [NEW]
    │       ├── Parent-child trace relationships
    │       └── Actions: Navigate to parent/child traces
    │
    ├── /models (mfe-models)
    │   ├── / (Model Dashboard)
    │   │   ├── Default view: Providers tab
    │   │   └── Redirect → /models/providers
    │   │
    │   ├── /providers (Providers List) [NEW]
    │   │   ├── List of configured model providers
    │   │   └── Actions: Add provider, edit, delete, test connection
    │   │
    │   ├── /providers/new (Add Provider) [NEW]
    │   │   ├── Form to add new provider configuration
    │   │   └── Actions: Save, test connection, cancel
    │   │
    │   ├── /providers/:providerId (Provider Detail) [NEW]
    │   │   ├── Provider configuration, API key, models
    │   │   └── Actions: Edit, delete, test connection, view models
    │   │
    │   ├── /providers/:providerId/edit (Edit Provider) [NEW]
    │   │   ├── Form to edit provider configuration
    │   │   └── Actions: Save, test connection, cancel
    │   │
    │   ├── /analytics (Model Analytics) [NEW]
    │   │   ├── Query Params: ?provider=<provider>&model=<model>&timeframe=<7d|30d|90d>
    │   │   ├── Analytics dashboard with usage, costs, performance
    │   │   └── Actions: Filter by provider/model, export data
    │   │
    │   └── /analytics/:provider/:model (Model-Specific Analytics) [NEW]
    │       ├── Detailed analytics for specific model
    │       └── Actions: View traces, export data
    │
    └── /policy (mfe-policy)
        ├── / (Policy Dashboard)
        │   ├── Default view: Policies tab
        │   └── Redirect → /policy/policies
        │
        ├── /policies (Policies List) [NEW]
        │   ├── Query Params: ?search=<query>&category=<category>&severity=<severity>
        │   ├── List of governance policies
        │   └── Actions: Create policy, view, edit, delete, enable/disable
        │
        ├── /policies/new (Create Policy) [NEW]
        │   ├── Form to create new policy
        │   └── Actions: Save, test, cancel
        │
        ├── /policies/:policyId (Policy Detail) [NEW]
        │   ├── Policy configuration, rules, actions, violations
        │   └── Actions: Edit, delete, enable/disable, view violations
        │
        ├── /policies/:policyId/edit (Edit Policy) [NEW]
        │   ├── Form to edit policy
        │   └── Actions: Save, test, cancel
        │
        ├── /violations (Violations List) [NEW]
        │   ├── Query Params: ?search=<query>&severity=<severity>&status=<active|resolved>&page=<num>
        │   ├── List of policy violations
        │   └── Actions: View violation, resolve, filter, search
        │
        └── /violations/:violationId (Violation Detail) [NEW]
            ├── Violation details, policy, resource, resolution
            └── Actions: Resolve, view policy, view resource
```

---

## Route Summary by MFE

### Shell (Host)
| Route | Purpose | Auth | Implementation |
|-------|---------|------|----------------|
| `/login` | User authentication | Public | ✅ Implemented |
| `/` | Root redirect | Private | ✅ Implemented |
| `/dashboard` | Overview dashboard | Private | ✅ Implemented |
| `*` | 404 Not Found | Public | ✅ Implemented |

**Total**: 4 routes, 100% implemented

---

### mfe-projects
| Route | Purpose | Auth | Implementation |
|-------|---------|------|----------------|
| `/projects` | Project list | Private | ✅ Implemented |
| `/projects?search=<query>` | Search projects | Private | ❌ Missing (state only) |
| `/projects?status=<status>` | Filter by status | Private | ❌ Missing (state only) |
| `/projects?page=<num>` | Pagination | Private | ❌ Missing |
| `/projects/:projectId` | Project detail | Private | ✅ Implemented |
| `/projects/:projectId/prompts` | Prompts list | Private | ❌ Missing |
| `/projects/:projectId/prompts?search=<query>` | Search prompts | Private | ❌ Missing |
| `/projects/prompt/:promptId` | Prompt detail | Private | ✅ Implemented (inconsistent path) |
| `/projects/:projectId/prompts/:promptId/versions` | Version history | Private | ❌ Missing |
| `/projects/:projectId/prompts/:promptId/evaluate` | Run evaluation | Private | ❌ Missing |

**Total**: 10 routes, 30% implemented

---

### mfe-insights
| Route | Purpose | Auth | Implementation |
|-------|---------|------|----------------|
| `/insights` | Main analysis page | Private | ✅ Implemented (no routing) |
| `/insights/new` | New analysis form | Private | ❌ Missing |
| `/insights/analysis/:analysisId` | Analysis detail | Private | ❌ Missing (CRITICAL) |
| `/insights/history` | Analysis history | Private | ❌ Missing (embedded in main page) |
| `/insights/history?search=<query>` | Search history | Private | ❌ Missing |
| `/insights/history?filter=<filter>` | Filter history | Private | ❌ Missing |
| `/insights/history?sort=<field>` | Sort history | Private | ❌ Missing |
| `/insights/compare` | Comparison selector | Private | ❌ Missing |
| `/insights/compare/:idA/:idB` | Ad-hoc comparison | Private | ❌ Missing (CRITICAL) |
| `/insights/comparisons` | Saved comparisons | Private | ❌ Missing |
| `/insights/comparisons/:comparisonId` | Comparison detail | Private | ❌ Missing (CRITICAL) |

**Total**: 11 routes, 9% implemented (1 route with no URL state)

---

### mfe-playground
| Route | Purpose | Auth | Implementation |
|-------|---------|------|----------------|
| `/playground` | Main playground | Private | ✅ Implemented (no routing) |
| `/playground?model=<model>` | Pre-select model | Private | ❌ Missing |
| `/playground?temp=<temp>` | Pre-set temperature | Private | ❌ Missing |
| `/playground?promptId=<id>` | Load prompt | Private | ❌ Missing |
| `/playground/session/:sessionId` | Session detail | Private | ❌ Missing (CRITICAL) |
| `/playground/history` | Session history | Private | ❌ Missing (toggle only) |
| `/playground/history?model=<model>` | Filter history | Private | ❌ Missing |
| `/playground/compare/:idA/:idB` | Compare sessions | Private | ❌ Missing |

**Total**: 8 routes, 13% implemented (1 route with no URL state)

---

### mfe-evaluations
| Route | Purpose | Auth | Implementation |
|-------|---------|------|----------------|
| `/evaluations` | Evaluation dashboard | Private | ✅ Implemented (no routing) |
| `/evaluations/results` | Results list | Private | ❌ Missing (tab state) |
| `/evaluations/results?search=<query>` | Search results | Private | ❌ Missing |
| `/evaluations/results?filter=<status>` | Filter results | Private | ❌ Missing |
| `/evaluations/results/:evaluationId` | Result detail | Private | ❌ Missing (CRITICAL) |
| `/evaluations/catalog` | Evaluation catalog | Private | ❌ Missing (tab state) |
| `/evaluations/catalog?category=<category>` | Filter catalog | Private | ❌ Missing |
| `/evaluations/catalog/:evaluationId` | Evaluation detail | Private | ❌ Missing |
| `/evaluations/create` | Create custom evaluation | Private | ❌ Missing (tab state) |
| `/evaluations/custom` | Custom evaluations | Private | ❌ Missing |
| `/evaluations/custom/:evaluationId` | Custom evaluation detail | Private | ❌ Missing |

**Total**: 11 routes, 9% implemented (1 route with no URL state)

---

### mfe-traces
| Route | Purpose | Auth | Implementation |
|-------|---------|------|----------------|
| `/traces` | Traces list | Private | ✅ Implemented (no routing) |
| `/traces?search=<query>` | Search traces | Private | ❌ Missing (state only) |
| `/traces?model=<model>` | Filter by model | Private | ❌ Missing (state only) |
| `/traces?status=<status>` | Filter by status | Private | ❌ Missing (state only) |
| `/traces?page=<num>` | Pagination | Private | ❌ Missing (state only) |
| `/traces?sort=<field>&order=<asc|desc>` | Sort traces | Private | ❌ Missing (state only) |
| `/traces/:traceId` | Trace detail | Private | ❌ Missing (CRITICAL - modal only) |
| `/traces/:traceId/spans` | Span visualization | Private | ❌ Missing |
| `/traces/:traceId/evaluations` | Trace evaluations | Private | ❌ Missing |
| `/traces/:traceId/parent-child` | Parent-child relationships | Private | ❌ Missing |

**Total**: 10 routes, 10% implemented (1 route with no URL state)

---

### mfe-models
| Route | Purpose | Auth | Implementation |
|-------|---------|------|----------------|
| `/models` | Model dashboard | Private | ✅ Implemented (no routing) |
| `/models/providers` | Providers list | Private | ❌ Missing (tab state) |
| `/models/providers/new` | Add provider | Private | ❌ Missing (modal) |
| `/models/providers/:providerId` | Provider detail | Private | ❌ Missing (modal) |
| `/models/providers/:providerId/edit` | Edit provider | Private | ❌ Missing (modal) |
| `/models/analytics` | Model analytics | Private | ❌ Missing (tab state) |
| `/models/analytics?provider=<provider>` | Filter analytics | Private | ❌ Missing |
| `/models/analytics/:provider/:model` | Model-specific analytics | Private | ❌ Missing |

**Total**: 8 routes, 13% implemented (1 route with no URL state)

---

### mfe-policy
| Route | Purpose | Auth | Implementation |
|-------|---------|------|----------------|
| `/policy` | Policy dashboard | Private | ✅ Implemented (no routing) |
| `/policy/policies` | Policies list | Private | ❌ Missing (tab state) |
| `/policy/policies?search=<query>` | Search policies | Private | ❌ Missing |
| `/policy/policies/new` | Create policy | Private | ❌ Missing |
| `/policy/policies/:policyId` | Policy detail | Private | ❌ Missing |
| `/policy/policies/:policyId/edit` | Edit policy | Private | ❌ Missing |
| `/policy/violations` | Violations list | Private | ❌ Missing (tab state) |
| `/policy/violations?severity=<severity>` | Filter violations | Private | ❌ Missing |
| `/policy/violations/:violationId` | Violation detail | Private | ❌ Missing |

**Total**: 9 routes, 11% implemented (1 route with no URL state)

---

## Overall Site Map Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Routes (Proposed)** | 81 | 100% |
| **Implemented Routes** | 3 | 5% |
| **Missing Routes** | 78 | 95% |
| **Critical Missing Routes** | 12 | 15% |
| **MFEs with Routing** | 1 / 7 | 14% |
| **MFEs without Routing** | 6 / 7 | 86% |

---

## Route Patterns & Conventions

### URL Structure

```
/[mfe]/[resource]/[id]/[sub-resource]/[sub-id]?[query-params]

Examples:
- /projects/:projectId/prompts/:promptId
- /traces/:traceId/spans
- /evaluations/results/:evaluationId
- /insights/analysis/:analysisId
```

### Query Parameters

**Pagination**:
```
?page=<num>&page_size=<num>
```

**Filtering**:
```
?filter=<value>&category=<value>&status=<value>
```

**Searching**:
```
?search=<query>
```

**Sorting**:
```
?sort=<field>&order=<asc|desc>
```

**Combined Example**:
```
/traces?search=error&model=gpt-4&status=failed&sort=duration&order=desc&page=2
```

### Authentication & Authorization

**All routes** except `/login` require authentication (Bearer token).

**Authorization** is enforced at API level via organization-scoped access control.

---

## Breadcrumb Navigation

Every route should display breadcrumbs showing the navigation hierarchy.

**Examples**:

```
Home > Projects
Home > Projects > Customer Support
Home > Projects > Customer Support > Prompts
Home > Projects > Customer Support > Prompts > Welcome Email > Versions

Home > Insights > Analysis > Analysis-12345
Home > Insights > Comparisons > Comparison-67890

Home > Traces > Trace-abc123 > Spans
Home > Traces > Trace-abc123 > Evaluations

Home > Evaluations > Catalog > Factual Accuracy
Home > Evaluations > Results > Result-456

Home > Models > Providers > OpenAI
Home > Models > Analytics > OpenAI > GPT-4
```

**Breadcrumb Rules**:
1. Always start with "Home" (links to `/dashboard`)
2. Each segment is clickable (links to parent route)
3. Last segment (current page) is not clickable
4. Use chevron separator (>)
5. Truncate long titles (max 30 chars)

---

## Deep Linking Examples

### Shareable URLs

**Specific Analysis**:
```
https://promptforge.ai/insights/analysis/550e8400-e29b-41d4-a716-446655440000
```

**Comparison of Two Analyses**:
```
https://promptforge.ai/insights/compare/550e8400-e29b-41d4-a716-446655440001/550e8400-e29b-41d4-a716-446655440002
```

**Filtered Traces**:
```
https://promptforge.ai/traces?search=error&model=gpt-4&status=failed&sort=duration&order=desc
```

**Specific Trace Detail**:
```
https://promptforge.ai/traces/trace-abc123
```

**Playground Session**:
```
https://promptforge.ai/playground/session/session-xyz789
```

**Playground with Pre-configured Parameters**:
```
https://promptforge.ai/playground?model=gpt-4&temp=0.7&max=1000&promptId=prompt-123
```

**Evaluation Result**:
```
https://promptforge.ai/evaluations/results/eval-result-456
```

**Project Prompt Detail**:
```
https://promptforge.ai/projects/proj-123/prompts/prompt-456
```

### Bookmarkable States

**Analysis History (Last 7 Days, Sorted by Date)**:
```
https://promptforge.ai/insights/history?filter=last7days&sort=date&order=desc
```

**Traces (Page 3, Filtered by GPT-4 Errors)**:
```
https://promptforge.ai/traces?model=gpt-4&status=error&page=3
```

**Evaluation Catalog (Security Category)**:
```
https://promptforge.ai/evaluations/catalog/security
```

**Projects (Search "customer", Page 2)**:
```
https://promptforge.ai/projects?search=customer&page=2
```

---

## Next Steps

See:
- [DEEP_LINKING_IMPLEMENTATION_PLAN.md](./DEEP_LINKING_IMPLEMENTATION_PLAN.md) for implementation details
- [NAVIGATION_ARCHITECTURE.md](./NAVIGATION_ARCHITECTURE.md) for breadcrumb and navigation patterns
- [ROUTING_BEST_PRACTICES.md](./ROUTING_BEST_PRACTICES.md) for coding guidelines

---

**End of Site Map**
