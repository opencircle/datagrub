# Cross-Agent Compatibility Rules - Complete Implementation

## Summary

Enhanced the subagent architecture with **mandatory cross-agent consultation rules** to prevent breaking changes across the UI, API, and database layers. Agents must now coordinate before making changes that could affect other tiers.

---

## Business Rules Implemented

### Rule 1: UI Architect → API Architect Consultation
**Trigger**: When UI Architect makes API-related changes
**Requirement**: **MUST** consult API Architect before implementation
**Purpose**: Prevent breaking API contracts from frontend

### Rule 2: API Architect → UI Architect & DB Architect Consultation
**Trigger**: When API Architect makes API changes
**Requirement**: **MUST** consult **BOTH** UI Architect AND DB Architect (parallel)
**Purpose**: Ensure API changes are compatible with frontend and backend

### Rule 3: DB Architect → API Architect Consultation
**Trigger**: When DB Architect makes database schema changes
**Requirement**: **MUST** consult API Architect before applying migrations
**Purpose**: Prevent breaking API queries and ORM models

---

## Key Enhancement: Incompatibility Resolution

**When incompatible changes detected:**
1. Agent provides **multiple options** with pros/cons
2. Each option includes:
   - Description
   - Pros and cons
   - Effort estimation (low/medium/high)
   - Implementation steps
   - Performance/migration impact
3. User reviews and **approves selected option**
4. Coordinated implementation across agents

---

## Files Updated

### 1. Orchestrator Documentation
**File**: `promptforge/.claude/CLAUDE_ORCHESTRATOR.md`

**Added**:
- Cross-Agent Compatibility Rules section
- All 3 business rules with detailed workflows
- Compatibility check response format (JSON schema)
- Orchestrator enforcement mechanisms
- Multi-agent workflow example
- Consultation command syntax

### 2. UI Architect Subagent
**File**: `Claude_Subagent_Prompts/UI_Architect_Agent.md`

**Added**:
- MANDATORY consultation requirement in Responsibilities
- `Consult_API_Architect` command
- Cross-Agent Compatibility Rules section with:
  - When to consult (API endpoint changes, payload modifications)
  - Consultation process (5 steps)
  - Example consultation
  - Expected response format
  - Violation consequences

### 3. API Architect Subagent
**File**: `Claude_Subagent_Prompts/API_Architect_Agent.md`

**Added**:
- MANDATORY consultation of UI + DB Architects
- MANDATORY response to consultation requests
- `Consult_UI_Architect` command
- `Consult_DB_Architect` command
- `Provide_Compatibility_Assessment` command
- Cross-Agent Compatibility Rules section with:
  - When to consult (route changes, schema modifications)
  - Parallel consultation process
  - Assessment criteria
  - Detailed response format with 3 recommendation options
  - Violation consequences

### 4. DB Architect Subagent
**File**: `Claude_Subagent_Prompts/DB_Architect_Agent.md`

**Added**:
- MANDATORY consultation of API Architect
- MANDATORY response to API Architect consultations
- `Consult_API_Architect` command
- `Provide_Compatibility_Assessment` command
- Cross-Agent Compatibility Rules section with:
  - When to consult (schema changes, migrations)
  - Consultation process
  - Schema analysis response format
  - Migration scripts in recommendations
  - Violation consequences

---

## Consultation Flow Diagrams

### Flow 1: UI Needs New API Feature

```
User: "Add project tagging feature"
    ↓
UX Specialist: Design tag UI
    ↓
UI Architect: "Need 'tags' field in POST /projects"
    ↓
MANDATORY: Consult API Architect
    ↓
API Architect evaluates:
    - Breaking change? (check existing contracts)
    - Determines DB change needed
    ↓
MANDATORY: Consult DB Architect
    ↓
DB Architect responds:
    ✓ COMPATIBLE: "Can add tags JSONB column"
    Provides:
    - Option A: Nullable JSONB (low effort)
    - Option B: Normalized table (medium effort)
    ↓
API Architect responds to UI Architect:
    ✓ COMPATIBLE: "Make tags optional"
    Provides:
    - Option A: Optional field (low effort)
    - Option B: Required + migration (medium effort)
    - Option C: v2 API (high effort)
    ↓
Orchestrator presents to user:
    Option A (recommended):
    - DB: Add tags JSONB column (nullable)
    - API: Add optional tags field
    - UI: Add tag selector component
    ↓
User approves: "Proceed with Option A"
    ↓
Coordinated implementation:
    1. DB Architect: Apply migration
    2. API Architect: Update routes
    3. UI Architect: Implement component
    4. UI QA: Test end-to-end
```

### Flow 2: API Changes Endpoint

```
API Architect: "Change GET /projects to include nested prompts"
    ↓
MANDATORY: Parallel consultation

    Consult UI Architect:
        Will UI break?
        ↓
        UI responds: INCOMPATIBLE
        - TypeScript types invalid
        - Components expect flat structure
        Recommends:
        - Option A: Lazy load prompts (separate endpoint)
        - Option B: Update all components (coordinated)

    Consult DB Architect:
        Schema support?
        ↓
        DB responds: COMPATIBLE
        - Can JOIN prompts table
        - Performance OK with index
        Recommends:
        - Option A: Add index, nullable JOIN
        - Option B: Materialized view

    ↓
API Architect aggregates responses:
    ✓ DB: COMPATIBLE (both options work)
    ✗ UI: INCOMPATIBLE (needs coordination)

Final recommendations:
    - Option A: Separate endpoint (both compatible)
    - Option B: Coordinated change (complex)
    ↓
User reviews and selects Option A
    ↓
Coordinated implementation with no breaking changes
```

### Flow 3: DB Schema Refactoring

```
DB Architect: "Rename 'project_name' to 'title' for consistency"
    ↓
MANDATORY: Consult API Architect
    ↓
API Architect evaluates:
    ✗ INCOMPATIBLE
    - All API responses use 'project_name'
    - ORM models reference 'project_name'
    - Breaking change for all API clients

Provides options:
    - Option A: Add 'title' column + computed 'project_name' view
      Pros: Backward compatible, no API changes
      Cons: Schema duplication
      Effort: Medium

    - Option B: Rename + API v2
      Pros: Clean schema, clear migration
      Cons: Must maintain v1 and v2
      Effort: High

    - Option C: Rename + coordinate breaking change
      Pros: Clean final state
      Cons: Requires coordination, downtime
      Effort: Very High
    ↓
User reviews options
User: "Go with Option A for backward compatibility"
    ↓
DB Architect implements:
    1. ADD COLUMN title
    2. Migrate data (title = project_name)
    3. CREATE VIEW with project_name as computed column
    4. Update queries to use title internally
    ↓
API continues working (no code changes needed)
```

---

## Compatibility Check Response Format

All agents use standardized JSON response:

```json
{
  "agent": "api_architect|ui_architect|db_architect",
  "consultation_type": "compatibility_check",
  "requesting_agent": "agent_name",
  "proposed_change": "Description of change",
  "compatibility_status": "COMPATIBLE|INCOMPATIBLE|REVIEW_NEEDED",

  "impact_analysis": {
    "breaking_changes": ["List of breaking changes"],
    "non_breaking_changes": ["List of safe changes"],
    "affected_components": ["file1.py", "file2.tsx"],
    "performance_impact": "description",
    "migration_required": true|false
  },

  "recommendations": [
    {
      "option": "A|B|C",
      "description": "Brief description",
      "pros": ["Advantage 1", "Advantage 2"],
      "cons": ["Disadvantage 1", "Disadvantage 2"],
      "effort": "low|medium|high",
      "implementation_steps": ["Step 1", "Step 2"],
      "migration_script": "SQL or code if applicable",
      "rollback_script": "Rollback if applicable"
    }
  ],

  "recommended_option": "A",
  "rationale": "Why this option is recommended"
}
```

---

## Orchestrator Enforcement

**The Claude orchestrator automatically:**

1. **Detects** when agents propose changes requiring consultation
2. **Blocks** implementation until compatibility checks complete
3. **Facilitates** parallel consultations (e.g., API → UI + DB simultaneously)
4. **Aggregates** responses from multiple consulted agents
5. **Presents** unified options with pros/cons to user
6. **Coordinates** implementation after user approves option

**Status Tracking** (in context):
```json
{
  "change_request_id": "uuid",
  "initiating_agent": "ui_architect",
  "consultations_required": ["api_architect"],
  "consultations_completed": ["api_architect"],
  "compatibility_results": {
    "api_architect": "COMPATIBLE"
  },
  "status": "approved",
  "selected_option": "A",
  "user_decision": "Proceed with Option A"
}
```

---

## Example Scenarios

### Scenario 1: Adding New Feature (Compatible)

**Request**: "Add ability to favorite projects"

**Flow**:
1. UI Architect: Need to add `is_favorite` boolean to UI
2. Consults API Architect
3. API evaluates: COMPATIBLE - can add optional boolean field
4. API consults DB Architect
5. DB evaluates: COMPATIBLE - simple column addition
6. All agents return COMPATIBLE
7. Implementation proceeds without options

**Result**: ✓ Feature implemented smoothly

---

### Scenario 2: Refactoring (Incompatible, resolved)

**Request**: "Change project structure to support workspaces"

**Flow**:
1. DB Architect: Need to add `workspace_id` foreign key
2. Consults API Architect
3. API evaluates: INCOMPATIBLE - breaks existing queries
4. API provides 3 options:
   - A: Add nullable workspace_id (backward compatible)
   - B: Required workspace_id + data migration
   - C: New workspace tables + views for compatibility
5. User selects Option A
6. Coordinated implementation:
   - DB: Add nullable column
   - API: Update queries (workspace_id filter optional)
   - UI: Add workspace selector (optional)

**Result**: ✓ Major refactoring without breaking changes

---

### Scenario 3: Breaking Change (User-approved)

**Request**: "Move to UUID primary keys for better distributed systems"

**Flow**:
1. DB Architect: Change id columns from INT to UUID
2. Consults API Architect
3. API evaluates: INCOMPATIBLE - breaks everything
4. API provides options:
   - A: Blue-green migration (parallel schemas)
   - B: Big bang migration (downtime required)
   - C: Gradual migration (composite keys temporarily)
5. User reviews all options
6. User approves: "Option A - blue-green migration"
7. Multi-phase coordinated implementation over weeks

**Result**: ✓ Breaking change executed safely with user approval

---

## Commands Reference

### For UI Architect:
```
CONSULT: api_architect
REASON: Need to add search filters to project list
REQUEST: compatibility_check
PROPOSED_CHANGE: Add 'tags' query parameter to GET /projects
IMPACT_SCOPE: ui-tier/pages/ProjectList.tsx
```

### For API Architect (consulting UI):
```
CONSULT: ui_architect
REASON: Changing project response structure
REQUEST: compatibility_check
PROPOSED_CHANGE: Nest prompts array in project response
IMPACT_SCOPE: ui-tier/types/Project.ts, ProjectDetail component
QUESTION: Will UI components break?
```

### For API Architect (consulting DB):
```
CONSULT: db_architect
REASON: Adding project versioning
REQUEST: compatibility_check
PROPOSED_CHANGE: Need project_versions table with history
IMPACT_SCOPE: data-tier schema, existing project queries
QUESTION: What's the best schema design?
```

### For DB Architect:
```
CONSULT: api_architect
REASON: Optimizing query performance
REQUEST: compatibility_check
PROPOSED_CHANGE: Add composite index on (user_id, created_at)
IMPACT_SCOPE: projects table, common queries
QUESTION: Will this affect API query plans?
```

---

## Violation Consequences

**If agents skip mandatory consultations:**

❌ **UI changes API without consulting**:
- Breaking API contracts
- Failed deployments
- Runtime errors for other consumers

❌ **API changes without consulting UI/DB**:
- Broken frontend components
- Failed database queries
- ORM model mismatches

❌ **DB changes without consulting API**:
- API query failures
- Data corruption risks
- Production outages

---

## Success Criteria

✅ **Mandatory consultations enforced** in agent specifications
✅ **Standardized response format** for all compatibility checks
✅ **Multiple options provided** for incompatible changes
✅ **User approval required** for breaking changes
✅ **Coordinated implementation** workflows defined
✅ **Orchestrator enforcement** mechanisms in place

---

## Updated Documentation

**Primary**:
- `promptforge/.claude/CLAUDE_ORCHESTRATOR.md` - Orchestration rules
- `Claude_Subagent_Prompts/UI_Architect_Agent.md` - UI consultation rules
- `Claude_Subagent_Prompts/API_Architect_Agent.md` - API consultation rules
- `Claude_Subagent_Prompts/DB_Architect_Agent.md` - DB consultation rules

**Reference**:
- `/datagrub/CROSS_AGENT_COMPATIBILITY_RULES.md` - This document

---

**Version**: 1.0
**Created**: 2025-10-06
**Status**: ✅ Complete - Cross-agent compatibility rules fully implemented
**Impact**: Prevents breaking changes across UI, API, and DB tiers
