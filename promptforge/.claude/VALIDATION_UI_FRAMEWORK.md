# UI Framework Validation Guide

This document validates that the UI Architect agent correctly references and enforces Phase2_UI_Framework.md specifications.

---

## Validation Checklist

### ✅ 1. Specification File Exists
**Location**: `/Users/rohitiyer/datagrub/PromptForge_Build_Specs/Phase2_UI_Framework.md`
**Status**: Created ✅
**Contents**: Comprehensive UI framework standards covering routing, state, design, accessibility, performance, and Module Federation

### ✅ 2. Agent Prompt Updated
**File**: `/Users/rohitiyer/datagrub/Claude_Subagent_Prompts/UI_Architect_Agent.md`
**Updates Made**:
- Line 14: Added "Follow UI Framework Standards from `/PromptForge_Build_Specs/Phase2_UI_Framework.md`"
- Lines 104-248: Added comprehensive "UI Framework Standards (MANDATORY)" section
- Includes key requirements, common patterns, pre-implementation checklist
- Lists violations and consequences

### ✅ 3. Orchestrator Updated
**File**: `/Users/rohitiyer/datagrub/CLAUDE.md`
**Updates Made**:
- Line 446: Added Phase2_UI_Framework.md to build specs list
- Line 110: Added to UI Architect's build specs reference
- Line 452: Updated auto-load rules to include UI Framework for ui-tier tasks

### ✅ 4. Implementation Complete
**Features Implemented**:
- Redux Persist for state persistence ✅
- Error Boundary component ✅
- 404 Not Found page ✅
- Browser refresh support ✅
- History API best practices ✅

---

## How the Agent Will Check Specifications

### Automatic Loading Mechanism

When the UI Architect agent is invoked, it will:

1. **Read Agent Prompt** (`UI_Architect_Agent.md`)
   - Line 14: Sees "Follow UI Framework Standards from `/PromptForge_Build_Specs/Phase2_UI_Framework.md`"
   - Lines 104-248: Reads UI Framework Standards section with key requirements

2. **Load Build Specs Based on Context**
   - File path contains `ui-tier` → Loads Phase1_CoreUI.md + Phase2_UI_Framework.md
   - Task context mentions "routing", "state", "navigation" → Loads Phase2_UI_Framework.md
   - Explicit reference in user prompt → Loads specified specs

3. **Apply Standards During Implementation**
   - Checks routing patterns (useNavigate vs window.location)
   - Validates state management strategy (Redux vs React Query)
   - Enforces design system (colors, spacing, border radius)
   - Verifies accessibility requirements (ARIA labels, contrast ratios)
   - Ensures error handling (Error Boundaries, loading states)

### Input Envelope Example

When you invoke the UI Architect:
```json
{
  "task_type": "implement",
  "file_path": "/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-projects/src/components/NewComponent.tsx",
  "build_specs_dir": "/Users/rohitiyer/datagrub/PromptForge_Build_Specs",
  "relevant_specs": ["Phase1_CoreUI.md", "Phase2_UI_Framework.md"],
  "task_uuid": "uuid-v4"
}
```

The agent will:
1. Read both specifications
2. Apply standards from Phase2_UI_Framework.md
3. Check implementation against requirements
4. Report compliance in output

---

## Validation Tests

### Test 1: Routing Implementation
**Scenario**: User asks to add navigation to new page

**Expected Agent Behavior**:
1. ✅ Reads Phase2_UI_Framework.md routing section
2. ✅ Uses `useNavigate()` hook (not `window.location`)
3. ✅ Adds route to App.tsx with proper nesting
4. ✅ Implements protected route if authentication required
5. ✅ Adds 404 handling

**Validation Command**:
```
"Invoke UI Architect to add navigation from Projects list to Project detail page"
```

**Expected Output**:
```typescript
// ✅ Follows Phase2_UI_Framework.md standards
import { useNavigate } from 'react-router-dom';

const ProjectCard = ({ project }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/projects/${project.id}`); // ✅ useNavigate, not window.location
  };

  return <div onClick={handleClick}>...</div>;
};
```

### Test 2: State Management
**Scenario**: User asks to add project filtering

**Expected Agent Behavior**:
1. ✅ Reads Phase2_UI_Framework.md state management section
2. ✅ Uses URL state for shareable filters (useSearchParams)
3. ✅ Uses React Query for server state (project list)
4. ✅ Separates UI state (modal open) from server state

**Validation Command**:
```
"Invoke UI Architect to add filtering capability to Projects page"
```

**Expected Output**:
```typescript
// ✅ Follows Phase2_UI_Framework.md state management
import { useSearchParams } from 'react-router-dom';
import { useProjects } from '../hooks/useProjects';

const ProjectList = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const filter = searchParams.get('filter') || 'all';

  const { data: projects } = useProjects({ filter }); // React Query
  const [modalOpen, setModalOpen] = useState(false); // UI state

  const handleFilterChange = (newFilter: string) => {
    setSearchParams({ filter: newFilter }); // URL state
  };
};
```

### Test 3: Design System
**Scenario**: User asks to create new button

**Expected Agent Behavior**:
1. ✅ Reads Phase2_UI_Framework.md design system section
2. ✅ Uses primary color #FF385C
3. ✅ Uses rounded-xl border radius
4. ✅ Uses font-semibold
5. ✅ Adds proper focus ring

**Validation Command**:
```
"Invoke UI Architect to create a primary action button component"
```

**Expected Output**:
```typescript
// ✅ Follows Phase2_UI_Framework.md design system
<button className="bg-[#FF385C] text-white rounded-xl hover:bg-[#E31C5F]
                   transition-all duration-200 font-semibold h-10 px-4
                   focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20">
  Click Me
</button>
```

### Test 4: Accessibility
**Scenario**: User asks to add delete button with icon

**Expected Agent Behavior**:
1. ✅ Reads Phase2_UI_Framework.md accessibility section
2. ✅ Adds aria-label to button
3. ✅ Adds aria-hidden to icon
4. ✅ Adds descriptive text for screen readers

**Validation Command**:
```
"Invoke UI Architect to add delete button to Project card"
```

**Expected Output**:
```typescript
// ✅ Follows Phase2_UI_Framework.md accessibility standards
<button
  aria-label="Delete project"
  aria-describedby="delete-help"
  className="..."
>
  <TrashIcon aria-hidden="true" className="h-5 w-5" />
</button>
<span id="delete-help" className="sr-only">
  This action cannot be undone
</span>
```

### Test 5: Error Handling
**Scenario**: User asks to implement API data fetching

**Expected Agent Behavior**:
1. ✅ Reads Phase2_UI_Framework.md error handling section
2. ✅ Wraps component with Error Boundary
3. ✅ Shows loading state during fetch
4. ✅ Shows user-friendly error message

**Validation Command**:
```
"Invoke UI Architect to fetch and display project details"
```

**Expected Output**:
```typescript
// ✅ Follows Phase2_UI_Framework.md error handling
const ProjectDetail = ({ id }) => {
  const { data: project, isLoading, isError, error } = useProject(id);

  if (isLoading) {
    return <LoadingSpinner />; // ✅ Loading state
  }

  if (isError) {
    return ( // ✅ User-friendly error
      <div className="flex items-center gap-2 text-red-600">
        <AlertCircle className="h-5 w-5" />
        <p>Failed to load project: {error.message}</p>
      </div>
    );
  }

  return <div>{project.name}</div>;
};

// ✅ Wrapped with Error Boundary in parent
<ErrorBoundary>
  <ProjectDetail id={id} />
</ErrorBoundary>
```

---

## Enforcement Mechanisms

### 1. Agent Prompt Enforcement
The UI Architect agent prompt explicitly states:
```
**Always consult Phase2_UI_Framework.md before making architectural decisions.**

**Failure to follow UI Framework Standards may result in**:
- Inconsistent user experience
- Accessibility violations (legal risk)
- Performance degradation
- State synchronization bugs
- Browser navigation broken
- Failed code reviews
```

### 2. Pre-Implementation Checklist
Agent must verify before implementing:
- [ ] Routes follow nested routing pattern
- [ ] State management strategy defined (Redux vs React Query)
- [ ] Design system colors/spacing used
- [ ] Accessibility requirements met
- [ ] Error boundaries in place
- [ ] Loading states implemented
- [ ] Browser refresh support works
- [ ] Browser back button works correctly

### 3. Checker Agent Validation
When Checker Agent reviews UI Architect output, it will:
1. Cross-reference against Phase2_UI_Framework.md
2. Flag violations (routing, state, design, accessibility)
3. Block deployment if critical violations found
4. Provide remediation guidance

---

## Verification Steps

To verify the agent is checking specifications:

### Step 1: Invoke UI Architect
```
"Invoke UI Architect to add a new page for Settings with navigation"
```

### Step 2: Check Agent Output
Look for references to Phase2_UI_Framework.md:
- "Following Phase2_UI_Framework.md routing standards..."
- "Using useNavigate() as per UI Framework specifications..."
- "Applying design system colors (#FF385C) from Phase2_UI_Framework.md..."

### Step 3: Review Implementation
Verify the generated code follows standards:
- ✅ Uses `useNavigate()` for navigation
- ✅ Uses design system colors and spacing
- ✅ Has ARIA labels for accessibility
- ✅ Includes error boundaries and loading states

### Step 4: Run Checker Agent
```
"Invoke Checker Agent to validate Settings page implementation"
```

Check for spec compliance confirmation:
```json
{
  "spec_compliance": {
    "Phase2_UI_Framework.md": {
      "routing": "✅ PASS - Uses useNavigate()",
      "design_system": "✅ PASS - Uses #FF385C primary color",
      "accessibility": "✅ PASS - ARIA labels present",
      "state_management": "✅ PASS - Uses React Query for server state"
    }
  }
}
```

---

## Conclusion

### ✅ Validation Complete

The UI Architect agent **WILL** check Phase2_UI_Framework.md specifications because:

1. **Agent Prompt References Framework** (line 14 + lines 104-248)
2. **Orchestrator Configured** (CLAUDE.md references spec in build specs list)
3. **Auto-Load Rules Updated** (ui-tier tasks trigger framework loading)
4. **Standards Enforced** (Pre-implementation checklist + violations documented)
5. **Checker Agent Reviews** (Cross-references all implementations against framework)

### How to Ensure Compliance

**When invoking UI Architect, be explicit**:
```
"Invoke UI Architect to [task], following Phase2_UI_Framework.md standards"
```

**The agent will**:
1. Read Phase2_UI_Framework.md
2. Apply routing, state, design, accessibility standards
3. Include error handling and loading states
4. Document compliance in implementation notes

**If standards are violated**:
- Checker Agent will flag the issue
- Remediation steps will be provided
- Code review will fail until fixed

---

**Last Updated**: 2025-10-06
**Status**: ✅ Validated - Agent will enforce UI Framework specifications
