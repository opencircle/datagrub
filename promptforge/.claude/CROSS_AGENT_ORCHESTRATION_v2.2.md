# Cross-Agent Orchestration System v2.2.0

**Version**: 2.2.0
**Created**: 2025-10-11
**Status**: Implementation Ready
**Purpose**: Full cross-agent consultation and auto-invocation system

---

## 🎯 Overview

This system implements **automatic cross-agent consultations** where agents automatically request reviews from other agents when their changes impact cross-tier boundaries.

### Key Principle
**No tier changes in isolation** - All cross-tier changes require consultation and approval from affected tier architects.

---

## 📋 Pydantic Schema Purpose

**Location**: `api-tier/app/schemas/`

**Purpose**:
1. **API Contract Definition** - Defines request/response structures
2. **Automatic Validation** - FastAPI validates incoming data
3. **OpenAPI Generation** - Auto-generates Swagger documentation
4. **Type Safety** - Ensures Python type correctness
5. **UI TypeScript Generation** - Source of truth for UI types

**Why Auto-Review Matters**:
- Changes to Pydantic schemas = API contract changes
- UI TypeScript types must be regenerated
- Database models must align with schema fields
- Existing tests must be updated
- OpenAPI docs automatically updated

**Example Impact**:
```python
# api-tier/app/schemas/project.py
class ProjectCreate(BaseModel):
    name: str
    description: str
    tags: List[str]  # ← NEW FIELD ADDED

# This change triggers:
# 1. API Architect review (contract change)
# 2. UI Architect consultation (TypeScript types need update)
# 3. DB Architect consultation (does projects table have tags column?)
# 4. API QA testing (do tests cover new field?)
```

---

## 🔄 Auto-Trigger Matrix

| File Pattern | Primary Agent | Auto-Consultations | Reason |
|--------------|---------------|-------------------|--------|
| `api-tier/routes/**/*.py` | API Architect | UI Architect, DB Architect, API QA | Route changes affect UI + DB |
| `api-tier/schemas/**/*.py` | API Architect | UI Architect, DB Architect, API QA | Pydantic = API contract = UI types |
| `api-tier/services/**/*.py` | API Architect | DB Architect, API QA | Business logic may affect DB queries |
| `api-tier/models/**/*.py` | API Architect | DB Architect | ORM models must align with DB schema |
| `data-tier/models/**/*.py` | DB Architect | API Architect | DB schema affects API ORM models |
| `data-tier/migrations/**/*.py` | DB Architect | API Architect, API QA | Schema changes affect API + tests |
| `database-tier/seed_data/**/*.py` | DB Architect | API Architect | Seed data must match current schema |
| `ui-tier/components/**/*.tsx` | UI Architect | UX Specialist | Components must follow design system |
| `ui-tier/pages/**/*.tsx` | UI Architect | UX Specialist, API Architect | Pages consume APIs + need UX review |
| `ui-tier/services/**/*.ts` | UI Architect | API Architect | API client code must match API contracts |

---

## 🏗️ Consultation Workflows

### Workflow 1: API Schema Change (Pydantic)

```
User edits: api-tier/app/schemas/project.py

1. Post-tool-use hook detects change
   ↓
2. AUTO-INVOKE: API Architect
   ↓
3. API Architect reviews:
   - Pydantic field changes
   - Validation rules
   - API contract changes
   ↓
4. API Architect detects:
   - NEW FIELD: tags (List[str])
   - Breaking change: Response structure modified
   ↓
5. API Architect returns consultation_requests:
   {
     "ui_architect": {
       "needed": true,
       "reason": "New 'tags' field requires TypeScript type update"
     },
     "db_architect": {
       "needed": true,
       "reason": "DB projects table needs 'tags' column migration"
     },
     "api_qa": {
       "needed": true,
       "reason": "Tests must cover new tags field validation"
     }
   }
   ↓
6. Orchestrator AUTO-INVOKES consultations IN PARALLEL:
   - UI Architect: "Review compatibility of new tags field"
   - DB Architect: "Check if projects table supports tags column"
   - API QA: "Run tests for schema changes"
   ↓
7. Agents respond with compatibility status:

   UI Architect:
   {
     "status": "INCOMPATIBLE",
     "issue": "ui-tier/types/Project.ts missing tags field",
     "fix": "Regenerate TypeScript types from updated schema",
     "breaking": true
   }

   DB Architect:
   {
     "status": "INCOMPATIBLE",
     "issue": "projects table has no tags column",
     "fix": "Create migration: ALTER TABLE projects ADD COLUMN tags JSONB[]",
     "migration_needed": true
   }

   API QA:
   {
     "status": "TESTS_FAILING",
     "failing_tests": ["test_create_project", "test_project_schema"],
     "fix": "Update test fixtures to include tags field"
   }
   ↓
8. Orchestrator presents consolidated review:

   **API Architect Review**: 🚫 CROSS-TIER IMPACTS DETECTED

   Schema Change: Added 'tags' field to ProjectCreate

   Required Actions:

   1. DB Migration (DB Architect)
      - Create migration for tags column
      - Type: JSONB[] or TEXT[]
      - Default: empty array

   2. UI Type Update (UI Architect)
      - Regenerate TypeScript types
      - Update ProjectForm component
      - Add tags input field

   3. Test Updates (API QA)
      - Fix: test_create_project
      - Fix: test_project_schema
      - Add: test_tags_validation

   Options:
   a) Make 'tags' optional (backward compatible)
   b) Version API to v2 (breaking change, maintain v1)
   c) Cancel change

   Which would you like to do?
```

---

### Workflow 2: Database Migration

```
User edits: data-tier/migrations/add_tags_column.py

1. Post-tool-use hook detects migration
   ↓
2. AUTO-INVOKE: DB Architect
   ↓
3. DB Architect reviews:
   - SQL syntax
   - Rollback script present?
   - Indexes needed?
   - Data migration safe?
   ↓
4. DB Architect detects:
   - NEW COLUMN: tags JSONB[]
   - Affects: projects table
   ↓
5. DB Architect returns consultation_requests:
   {
     "api_architect": {
       "needed": true,
       "reason": "API ORM models need tags field added"
     }
   }
   ↓
6. Orchestrator AUTO-INVOKES: API Architect
   ↓
7. API Architect checks:
   - Does Project model have tags field? NO
   - Does ProjectCreate schema have tags? NO
   - Will existing queries break? NO (new column, nullable)
   ↓
8. API Architect responds:
   {
     "status": "INCOMPATIBLE",
     "issue": "API models don't include tags field",
     "fix": "Add tags field to Project model and ProjectCreate schema",
     "breaking": false
   }
   ↓
9. Orchestrator presents plan:

   **DB Architect Review**: ⚠️ API SYNC NEEDED

   Migration: Add tags column to projects table

   Required Actions:
   1. Run migration (DB)
   2. Add tags to api-tier/models/project.py
   3. Add tags to api-tier/schemas/project.py
   4. Regenerate UI TypeScript types

   Proceed with migration?
```

---

### Workflow 3: UI Component Change

```
User edits: ui-tier/components/ProjectCard.tsx

1. Post-tool-use hook detects component
   ↓
2. AUTO-INVOKE: UI Architect
   ↓
3. UI Architect reviews:
   - Component structure
   - React best practices
   - Accessibility (ARIA labels, keyboard nav)
   - State management
   ↓
4. UI Architect detects:
   - NEW BUTTON: Delete action
   - API CALL: DELETE /projects/{id}
   - STYLING: Custom colors used
   ↓
5. UI Architect returns consultation_requests:
   {
     "ux_specialist": {
       "needed": true,
       "reason": "Custom colors may violate design system"
     },
     "api_architect": {
       "needed": false,
       "reason": "DELETE endpoint already exists"
     }
   }
   ↓
6. Orchestrator AUTO-INVOKES: UX Specialist
   ↓
7. UX Specialist checks:
   - Button color: #FF0000 (custom red)
   - Design system primary: #FF385C
   - Spacing: 12px (should be 8px grid)
   ↓
8. UX Specialist responds:
   {
     "status": "DESIGN_VIOLATION",
     "violations": [
       {
         "issue": "Custom button color #FF0000",
         "fix": "Use design system: bg-[#FF385C]",
         "severity": "medium"
       },
       {
         "issue": "Spacing 12px not on 8px grid",
         "fix": "Use p-3 (12px) or p-4 (16px)",
         "severity": "low"
       }
     ]
   }
   ↓
9. Orchestrator presents review:

   **UI Architect Review**: ⚠️ DESIGN SYSTEM VIOLATIONS

   Component: ProjectCard.tsx

   UX Specialist Findings:
   1. Custom red color detected
      - Current: #FF0000
      - Should be: #FF385C (design system primary)

   2. Non-standard spacing
      - Current: 12px
      - Should be: 16px (p-4) on 8px grid

   Recommendations:
   - Replace custom color with Tailwind class
   - Use design system spacing utilities

   Apply fixes automatically?
```

---

## 🤖 Updated Agent Responsibilities

### API Architect (Auto-Triggered)

**Auto-Trigger Patterns**:
- `api-tier/routes/**/*.py`
- `api-tier/services/**/*.py`
- `api-tier/schemas/**/*.py` ⭐ PYDANTIC
- `api-tier/models/**/*.py`

**Mandatory Consultations**:
- **UI Architect**: If Pydantic schema changes (API contract = UI types)
- **DB Architect**: If ORM model changes or new DB queries
- **API QA**: If breaking changes or new endpoints

**Output Includes**:
```json
{
  "consultation_requests": {
    "ui_architect": {"needed": true, "reason": "..."},
    "db_architect": {"needed": true, "reason": "..."},
    "api_qa": {"needed": true, "reason": "..."}
  }
}
```

---

### DB Architect (Auto-Triggered)

**Auto-Trigger Patterns**:
- `data-tier/models/**/*.py`
- `data-tier/migrations/**/*.py` ⭐ MIGRATIONS
- `database-tier/seed_data/**/*.py`

**Mandatory Consultations**:
- **API Architect**: ALWAYS (DB changes affect API ORM models)

**Output Includes**:
```json
{
  "consultation_requests": {
    "api_architect": {"needed": true, "reason": "Schema change affects ORM"}
  }
}
```

---

### UI Architect (Auto-Triggered)

**Auto-Trigger Patterns**:
- `ui-tier/components/**/*.tsx` ⭐ COMPONENTS
- `ui-tier/pages/**/*.tsx`
- `ui-tier/hooks/**/*.ts`
- `ui-tier/services/**/*.ts`

**Mandatory Consultations**:
- **UX Specialist**: ALWAYS (all UI must follow design system)
- **API Architect**: If API service calls changed

**Output Includes**:
```json
{
  "consultation_requests": {
    "ux_specialist": {"needed": true, "reason": "Design system compliance"},
    "api_architect": {"needed": false, "reason": "No API changes"}
  }
}
```

---

## 📊 Consultation Response Format

All agents responding to consultations must use:

```json
{
  "agent": "ui_architect",
  "consultation_type": "compatibility_check",
  "requesting_agent": "api_architect",
  "proposed_change": "Add tags field to ProjectCreate schema",

  "compatibility_status": "COMPATIBLE|INCOMPATIBLE|REVIEW_NEEDED|BLOCKED",

  "impact_analysis": {
    "breaking_changes": [
      "TypeScript types need regeneration"
    ],
    "non_breaking_changes": [
      "If tags is optional, backward compatible"
    ],
    "affected_files": [
      "ui-tier/types/Project.ts",
      "ui-tier/components/ProjectForm.tsx"
    ]
  },

  "recommendations": [
    {
      "option": "A",
      "description": "Make tags optional with default empty array",
      "pros": ["Backward compatible", "No breaking changes"],
      "cons": ["Existing projects won't have tags"],
      "effort": "low",
      "changes_required": [
        "Add tags?: string[] to Project type",
        "Add default [] in form"
      ]
    },
    {
      "option": "B",
      "description": "Make tags required",
      "pros": ["Enforces data quality"],
      "cons": ["Breaking change", "Existing data migration needed"],
      "effort": "high",
      "changes_required": [
        "Add tags: string[] (required)",
        "Migrate existing projects",
        "Update all forms"
      ]
    }
  ],

  "recommended_option": "A",
  "rationale": "Backward compatibility preferred for non-critical feature",

  "requires_user_decision": true
}
```

---

## 🎯 Implementation Status

### ✅ Completed
1. Hook detects API, DB, UI file changes
2. API Architect auto-invocation for API files
3. Consultation request format defined
4. Cross-agent workflow designed

### 🔄 In Progress
1. DB Architect prompt template with API consultation
2. UI Architect prompt template with UX consultation
3. Orchestrator logic to process consultation_requests
4. Parallel consultation invocation

### ⏭️ Next Steps
1. Update hook with DB/UI architect prompts
2. Implement consultation request handler
3. Add consultation response aggregator
4. Update orchestrator documentation
5. Create workflow examples
6. Test end-to-end flows

---

## 🧪 Testing Plan

### Test 1: Pydantic Schema Change
```bash
# Edit Pydantic schema
vim api-tier/app/schemas/project.py
# Add: tags: List[str]

# Expected:
# 1. API Architect review
# 2. UI Architect consultation (types)
# 3. DB Architect consultation (column)
# 4. API QA consultation (tests)
# 5. Consolidated report with options
```

### Test 2: Database Migration
```bash
# Create migration
vim data-tier/migrations/add_tags.py

# Expected:
# 1. DB Architect review
# 2. API Architect consultation (ORM)
# 3. Migration validation
# 4. Sync plan presented
```

### Test 3: UI Component
```bash
# Edit component
vim ui-tier/components/ProjectCard.tsx

# Expected:
# 1. UI Architect review
# 2. UX Specialist consultation (design)
# 3. Design violations flagged
# 4. Auto-fix suggestions
```

---

## 📚 Documentation Updates

Files to update:
- [x] `.claude/hooks/post-tool-use.sh` (detection + prompts)
- [ ] `.claude/CLAUDE.md` (orchestrator rules)
- [ ] `.claude/agents/01_architecture/API_Architect_Agent.md` (consultation protocol)
- [ ] `.claude/agents/01_architecture/DB_Architect_Agent.md` (consultation protocol)
- [ ] `.claude/agents/01_architecture/UI_Architect_Agent.md` (consultation protocol)
- [ ] `.claude/agents/01_architecture/UX_Specialist_Agent.md` (consultation protocol)
- [ ] `.claude/agents/02_quality/API_QA_Agent.md` (auto-invocation from API Architect)

---

**Status**: Design Complete - Ready for Full Implementation
**Version**: 2.2.0
**Coverage**: API + DB + UI + UX + QA cross-agent orchestration
