# Claude Code Orchestrator - Enhanced Init Script

This document configures Claude Code as a **multi-subagent orchestrator** with **persistent context**, **automated validation hooks**, and **build spec awareness** for the PromptForge project.

---

## Overview

**Key Enhancements for Claude Code:**
- Native integration with Claude Code's Task tool for subagent spawning
- PostToolUse hooks for automatic script/readme validation
- Build spec context injection for all validation tasks
- Persistent memory using .claude/context directory
- Resume-on-crash via checkpoint files

---

## Project Structure

```
/Users/rohitiyer/datagrub/
├── promptforge/                           # Main project (current workspace)
│   ├── .claude/                          # Claude Code configuration
│   │   ├── CLAUDE_ORCHESTRATOR.md       # This file
│   │   ├── hooks/                       # Event-driven hooks
│   │   │   └── post-tool-use.sh         # Validation trigger
│   │   ├── agents/                      # Subagent definitions
│   │   │   ├── script-validator.md      # Script validation agent
│   │   │   └── readme-validator.md      # Documentation validation agent
│   │   └── context/                     # Persistent agent memory
│   │       ├── ui_architect_context.json
│   │       ├── api_architect_context.json
│   │       ├── db_architect_context.json
│   │       ├── validator_context.json
│   │       └── resume_checkpoint.json
│   ├── ui-tier/
│   ├── api-tier/
│   ├── data-tier/
│   └── scripts/
├── PromptForge_Build_Specs/              # Product specifications
│   ├── Phase1_CoreUI.md
│   ├── Phase2_APIs.md
│   ├── Phase2_API_SecurityRequirements.md
│   ├── Phase2_API_PerformanceRequirements.md
│   ├── Phase2_Evaluation_Framework.md
│   ├── Phase2_Summarization_Insights_API_DTA.md  # Deep Insights API ⭐
│   ├── Phase2_Insights_History.md             # Deep Insights implementation ⭐
│   ├── Phase2_Trace_Dashboard.md
│   ├── Phase2_UI_Framework.md
│   ├── Phase3_Privacy_Framework.md
│   └── Phase3_SaaSRefinement.md
└── Claude_Subagent_Prompts/              # Subagent templates
    ├── UI_Architect_Agent.md
    ├── API_Architect_Agent.md
    ├── DB_Architect_Agent.md
    ├── API_QA_Agent.md
    ├── UI_QA_Agent.md
    └── Doc_Context_Tracker_Agent.md
```

---

## Claude Code Configuration

### Environment Context

All Claude Code sessions automatically have access to:
- **Working directory**: `/Users/rohitiyer/datagrub/promptforge`
- **Build specs**: `/Users/rohitiyer/datagrub/PromptForge_Build_Specs`
- **Subagent prompts**: `/Users/rohitiyer/datagrub/Claude_Subagent_Prompts`
- **Max tokens**: 200000 (configured in Claude Code settings)

### ⚠️ MANDATORY CHECKER APPROVAL POLICY ⚠️

**CRITICAL RULE**: All architect agent implementations (UI, API, DB, UX) **MUST** receive Checker Agent approval before presenting results to the user.

**Enforcement**:
1. After any architect agent completes work, invoke Checker Agent for Post_Check
2. Wait for Checker approval status (APPROVED, PASS_WITH_WARNINGS, BLOCKED)
3. If BLOCKED: Address issues and re-submit to Checker
4. If APPROVED or PASS_WITH_WARNINGS: Present results to user with Checker status
5. Always include Checker review summary in user-facing response

**Approval Status Format**:
```
✅ Checker Agent Status: APPROVED (Confidence: 98%)
📊 Quality Gates: 5/5 PASSED
⚠️  Warnings: 3 (testing infrastructure recommended)
📄 Full Report: .claude/reports/checker_review_[date]_[task].json
```

### Subagent Registry

| Agent Type | Trigger | Tool | Context File | Mandatory |
|------------|---------|------|--------------|-----------|
| **Script Validator** | Write/Edit to `scripts/**/*.{sh,py,js,ts}` | `Task (general-purpose)` | `validator_context.json` | Auto |
| **README Validator** | Write/Edit to `**/{README,SETUP,GUIDE}*.md` | `Task (general-purpose)` | `validator_context.json` | Auto |
| **Checker** | **MANDATORY Post-Check after all architect work** | `Task (general-purpose)` | `checker_context.json` | ✅ YES |
| **UX Specialist** | Manual (Priority: First for all UX decisions) | `Task (general-purpose)` | `ux_specialist_context.json` | No |
| **UI Architect** | Manual or PR to `ui-tier/**` | `Task (general-purpose)` | `ui_architect_context.json` | No |
| **API Architect** | Manual or PR to `api-tier/**` | `Task (general-purpose)` | `api_architect_context.json` | No |
| **DB Architect** | Manual or PR to `data-tier/**` | `Task (general-purpose)` | `db_architect_context.json` | No |
| **API QA** | Post-deployment or manual | `Task (general-purpose)` | `apiqa_context.json` | No |
| **UI QA** | Post-deployment or manual | `Task (general-purpose)` | `uiqa_context.json` | No |

**Priority Rules**:
1. **UX Specialist FIRST**: Consult for all UX/design/style decisions before implementation
2. **Checker LAST**: MANDATORY approval after all architect implementations before user presentation
3. **No user-facing response without Checker approval status**

---

## Automated Validation System

### Hook: PostToolUse (Script & README Validation)

**File**: `.claude/hooks/post-tool-use.sh`

**Triggers**: After any `Write` or `Edit` tool use on:
- Scripts: `scripts/**/*.{sh,bash,py,js,ts}`
- Documentation: `**/{README,SETUP,GUIDE,INSTALL,DEPLOY,ARCHITECTURE,TESTING}*.md`

**Behavior**:
1. Detects file type (script vs readme)
2. Invokes validation subagent via Claude Code Task tool
3. Subagent performs comprehensive validation
4. Auto-fixes issues when possible
5. Reports findings back to main session

**Validation Context Injection**:
```bash
BUILD_SPECS_DIR="/Users/rohitiyer/datagrub/PromptForge_Build_Specs"
PROJECT_DIR="/Users/rohitiyer/datagrub/promptforge"
```

Every validation task automatically receives:
- Full path to build specs
- Current project structure
- Relevant phase documentation
- Previous validation history from context files

---

## Subagent Communication Protocol

### Input Envelope (JSON)

When spawning a subagent via Task tool:

```json
{
  "task_type": "validate|review|implement|test",
  "file_path": "/absolute/path/to/file",
  "build_specs_dir": "/Users/rohitiyer/datagrub/PromptForge_Build_Specs",
  "relevant_specs": ["Phase2_APIs.md", "Phase2_Evaluation_Framework.md"],
  "context_file": "/Users/rohitiyer/datagrub/promptforge/.claude/context/validator_context.json",
  "changed_files": ["path1", "path2"],
  "task_uuid": "uuid-v4",
  "resume": false,
  "timestamp": "2025-10-05T20:00:00Z"
}
```

### Output Envelope (JSON)

Expected from subagents:

```json
{
  "agent": "script-validator",
  "status": "ok|warn|error|blocked",
  "summary": "Brief summary of validation results",
  "findings": [
    {
      "rule_id": "SHELL-001",
      "severity": "high|medium|low",
      "file": "scripts/deploy.sh",
      "line": 42,
      "issue": "Missing error handling for AWS CLI command",
      "fix_applied": true,
      "fix_description": "Added set -e and error trap"
    }
  ],
  "spec_compliance": {
    "aligned_specs": ["Phase2_APIs.md#deployment"],
    "violations": []
  },
  "artifacts": {
    "validation_report": "file:///.claude/reports/validation-2025-10-05.json"
  },
  "next_actions": ["Review deployment documentation", "Test script in dev environment"],
  "context_update": {
    "last_validated": "2025-10-05T20:00:00Z",
    "validation_count": 15,
    "common_issues": ["missing-shebangs", "hardcoded-paths"]
  }
}
```

---

## Validation Rules

### Script Validation (Shell/Python/JS/TS)

**Critical Checks**:
1. **Syntax validation**: shellcheck, pylint, eslint, tsc
2. **Build spec alignment**: Cross-reference with PromptForge_Build_Specs
3. **Security**: No hardcoded credentials, unsafe operations
4. **Dependencies**: All tools/packages exist or documented
5. **Error handling**: Proper exit codes, traps, try-catch
6. **Environment**: Required env vars match specs
7. **Paths**: Valid relative to project structure
8. **Permissions**: Correct shebang, executable flags

**Auto-fixes**:
- Add missing shebangs
- Fix indentation
- Add error handling scaffolding
- Update hardcoded paths to use variables
- Add missing documentation headers

### README/Documentation Validation

**Critical Checks**:
1. **Spec alignment**: Match build specs requirements
2. **Command accuracy**: All examples have correct syntax
3. **File references**: All paths exist
4. **Completeness**: Installation, usage, troubleshooting sections
5. **Code blocks**: Proper language tags (```bash, ```python, etc.)
6. **Links**: Valid internal/external references
7. **Architecture consistency**: Diagrams/descriptions match specs
8. **Examples**: Working, tested command sequences

**Auto-fixes**:
- Add missing code block language tags
- Fix broken internal links
- Update outdated paths
- Add missing sections (based on template)
- Fix markdown formatting

---

## UX Specialist Integration

### Role in Orchestration
The **UX Specialist** is the authoritative source for all design, style, and user experience decisions. The orchestrator should **prioritize UX Specialist consultation** for:

1. **New UI Component Design** (before UI Architect implements)
2. **Design System Changes** (colors, typography, spacing)
3. **Style and Tone Decisions** (branding, visual language)
4. **Accessibility Requirements** (WCAG AAA compliance)
5. **User Interaction Patterns** (hover states, transitions, feedback)

### Workflow Priority
```
UX Decision Needed
    ↓
1. Consult UX Specialist FIRST
    ↓
2. UX Specialist provides design specifications
    ↓
3. UI Architect implements per specs
    ↓
4. UI QA validates against UX specifications
```

### Design System Authority
The UX Specialist maintains the **design system** in `ux_specialist_context.json`:
- **Color palette** (Airbnb-style: primary #FF385C, neutral #222222)
- **Typography** (Inter, Cereal fonts with defined scales)
- **Spacing scale** (8px grid: 0, 8, 16, 24, 32, 48, 64, 96)
- **Shadows** (soft shadows only, no hard edges)
- **Border radius** (rounded corners: 8px-16px typical)
- **Accessibility standards** (WCAG 2.1 AAA)

### Collaboration Pattern

**UX Specialist → UI Architect**:
- UX provides: Design specs, component patterns, accessibility requirements
- UI implements: React components following UX guidelines
- UX reviews: Validates implementation matches specifications

**UX Specialist → UI QA**:
- UX defines: UX validation criteria, visual regression scenarios
- UI QA tests: Components match UX specs, accessibility compliance

**UX Specialist → API Architect**:
- UX advises: User-friendly error messages, loading state patterns
- API implements: Responses with UX-friendly messaging

### Invocation Examples

**New Component Design**:
```
"Invoke UX Specialist to design a search results card component for the evaluations page"
```

**Design System Update**:
```
"Have UX Specialist review and update color palette for better contrast"
```

**Accessibility Audit**:
```
"UX Specialist: audit the project creation form for WCAG AAA compliance"
```

**Component Review**:
```
"UX Specialist: review the Button component in ui-tier/components/Button.tsx"
```

---

## Checker Agent Integration (Quality Assurance Guardian)

### Role in Orchestration
The **Checker Agent** acts as a **quality gate** that runs before and after all architect implementations to ensure specification compliance, prevent regressions, and continuously improve output quality.

### Invocation Points

**1. Pre-Implementation Check (MANDATORY)**
```
User requests feature
    ↓
Orchestrator invokes Checker: Pre_Check
    ↓
Checker analyzes:
    - Relevant build specifications
    - Historical error patterns
    - Similar past implementations
    - Risk assessment
    ↓
Checker returns warnings and recommendations
    ↓
Architect implements with guidance
```

**2. Post-Implementation Check (MANDATORY)**
```
Architect completes implementation
    ↓
Orchestrator invokes Checker: Post_Check
    ↓
Checker validates:
    - Specification compliance
    - Regression tests
    - Error pattern avoidance
    - Test coverage
    - Documentation completeness
    ↓
Checker returns: PASS | FAIL | BLOCKED
    ↓
If PASS: Proceed to next step
If FAIL/BLOCKED: Architect fixes issues
```

### Checker Workflow

**Pre-Check Process**:
1. Load relevant build specs for the component
2. Query error pattern database for similar components
3. Identify high-risk areas from past failures
4. Provide preventive recommendations
5. Warn about common pitfalls

**Post-Check Process**:
1. Validate against all relevant specifications
2. Run regression test suite
3. Check for known error patterns
4. Verify cross-agent compatibility (if applicable)
5. Assess test coverage
6. Update error pattern database
7. Record quality metrics

### Quality Gates Enforced

**Gate 1: Specification Alignment** (BLOCK)
- All build spec requirements met
- No undocumented deviations

**Gate 2: Regression Prevention** (BLOCK)
- All regression tests pass
- No reintroduction of fixed bugs

**Gate 3: Error Pattern Avoidance** (WARNING/BLOCK)
- No repeated error patterns
- Preventive measures applied

**Gate 4: Test Coverage** (BLOCK)
- Unit tests >80%
- Integration tests for critical paths

**Gate 5: Documentation** (WARNING)
- Code comments present
- API docs updated
- Migration scripts documented

### Integration Examples

**Example 1: UI Component Development**
```
User: "Create ProjectCard component"
    ↓
Orchestrator: Invoke Checker Pre_Check
    ↓
Checker: {
  "risk_level": "medium",
  "warnings": ["Missing loading state seen 8x before"],
  "recommendations": [
    "Include loading skeleton",
    "Add error boundary",
    "Ensure WCAG AAA compliance"
  ]
}
    ↓
UX Specialist: Design component
UI Architect: Implement with recommendations
    ↓
Orchestrator: Invoke Checker Post_Check
    ↓
Checker: {
  "status": "PASS",
  "spec_compliance": "✓ All checks pass",
  "regressions": 0,
  "coverage": 0.85
}
    ↓
✓ Feature approved
```

**Example 2: API Endpoint Creation**
```
User: "Add DELETE /projects/{id} endpoint"
    ↓
Orchestrator: Invoke Checker Pre_Check
    ↓
Checker: {
  "risk_level": "high",
  "warnings": [
    "Past deletion endpoints missed cascade handling (3x)",
    "Permission checks forgotten (2x)"
  ],
  "recommendations": [
    "Implement soft delete (is_deleted flag)",
    "Add cascade delete for prompts/evaluations",
    "Require admin permission"
  ]
}
    ↓
API Architect: Implement with recommendations
DB Architect: Add schema support
    ↓
Orchestrator: Invoke Checker Post_Check
    ↓
Checker: {
  "status": "PASS_WITH_WARNINGS",
  "spec_compliance": "✓ Phase2_APIs.md requirements met",
  "warnings": ["Consider adding deletion audit log"],
  "regressions": 0
}
    ↓
✓ Feature approved with note
```

**Example 3: Regression Detected**
```
API Architect: Updates /projects/{id} response
    ↓
Orchestrator: Invoke Checker Post_Check
    ↓
Checker runs regression suite:
    ✗ REG-023: Response format regression detected
    ↓
Checker: {
  "status": "BLOCKED",
  "regression_detected": {
    "test_id": "REG-023",
    "description": "Response format changed",
    "impact": "UI ProjectDetail component will break",
    "last_fixed": "2025-09-15"
  },
  "options": [
    "A: Revert change (v1 compatibility)",
    "B: Create v2 endpoint",
    "C: Coordinate UI update"
  ]
}
    ↓
User selects option
    ↓
Coordinated fix
    ↓
Checker: Re-check passes
✓ Regression resolved
```

### Error Pattern Learning

**Checker maintains knowledge base**:
- API errors: async handling, validation, status codes
- UI errors: loading states, accessibility, responsiveness
- DB errors: indexes, migrations, constraints
- Integration errors: type mismatches, contract breaking

**Continuous improvement**:
- Tracks error frequency trends
- Recommends process improvements
- Suggests agent spec updates
- Identifies automation opportunities

### Checker Commands

**Pre_Check**: Risk assessment before implementation
**Post_Check**: Quality validation after implementation
**Record_Error**: Log error pattern for prevention
**Run_Regression_Suite**: Execute all regression tests
**Generate_Quality_Report**: Comprehensive quality metrics

---

## Cross-Agent Compatibility Rules

The orchestrator enforces **mandatory compatibility checks** to prevent breaking changes across the application stack.

### Business Rule 1: UI Architect → API Architect Consultation

**Trigger**: When UI Architect makes API-related changes (endpoints, payloads, headers)

**Requirement**: UI Architect **MUST** consult API Architect before implementing changes

**Process**:
```
1. UI Architect identifies API change needed
   ↓
2. Invoke API Architect with compatibility check request
   ↓
3. API Architect evaluates:
   - Does this break existing API contracts?
   - Are there versioning concerns?
   - Will other consumers be affected?
   ↓
4. API Architect responds with:
   - COMPATIBLE: Proceed with implementation
   - INCOMPATIBLE: Recommend options:
     * Option A: Use API versioning (e.g., /v2/endpoint)
     * Option B: Add new endpoint, deprecate old
     * Option C: Use backward-compatible payload extension
     * Option D: Coordinate breaking change with migration plan
   ↓
5. User approves selected option
   ↓
6. UI Architect implements with API Architect guidance
```

**Example Invocation**:
```
"UI Architect needs to add 'tags' field to project creation.
Consult API Architect for compatibility check."
```

---

### Business Rule 2: API Architect → UI Architect & DB Architect Consultation

**Trigger**: When API Architect makes API changes (routes, schemas, responses)

**Requirement**: API Architect **MUST** consult both UI Architect AND DB Architect

**Process**:
```
1. API Architect proposes API change
   ↓
2. PARALLEL CONSULTATION:

   2a. Invoke UI Architect:
       - Will UI components break?
       - Are UI contracts still valid?
       - Do frontend types need updates?

   2b. Invoke DB Architect:
       - Does database schema support this?
       - Are there migration needs?
       - Will queries perform efficiently?
   ↓
3. Both agents evaluate and respond:
   - UI Architect: COMPATIBLE | INCOMPATIBLE (with recommendations)
   - DB Architect: COMPATIBLE | INCOMPATIBLE (with recommendations)
   ↓
4. If INCOMPATIBLE from either:
   API Architect provides options:
   * Option A: Modify API to maintain compatibility
   * Option B: Add schema migration + UI updates (coordinated)
   * Option C: Version API (v1 unchanged, v2 with new behavior)
   * Option D: Phased rollout (DB first, then API, then UI)
   ↓
5. User approves selected option
   ↓
6. API Architect coordinates implementation with both agents
```

**Example Invocation**:
```
"API Architect wants to change 'project' response to include nested 'prompts' array.
Consult UI Architect and DB Architect for compatibility."
```

---

### Business Rule 3: DB Architect → API Architect Consultation

**Trigger**: When DB Architect makes database changes (schema, indexes, constraints)

**Requirement**: DB Architect **MUST** consult API Architect before applying changes

**Process**:
```
1. DB Architect identifies database change needed
   ↓
2. Invoke API Architect with compatibility check request
   ↓
3. API Architect evaluates:
   - Will existing API queries break?
   - Do ORM models need updates?
   - Are there performance implications?
   - Will API responses change?
   ↓
4. API Architect responds with:
   - COMPATIBLE: Proceed with migration
   - INCOMPATIBLE: Recommend options:
     * Option A: Add columns (nullable), update later
     * Option B: Create views for backward compatibility
     * Option C: Blue-green migration (parallel schemas)
     * Option D: Coordinate API + DB changes together
   ↓
5. User approves selected option
   ↓
6. DB Architect implements with API Architect guidance
```

**Example Invocation**:
```
"DB Architect needs to rename 'project_name' to 'title' in projects table.
Consult API Architect for compatibility check."
```

---

### Compatibility Check Response Format

All agents responding to compatibility checks should use this format:

```json
{
  "agent": "api_architect",
  "consultation_type": "compatibility_check",
  "requesting_agent": "ui_architect",
  "proposed_change": "Add 'tags' field to POST /projects payload",
  "compatibility_status": "COMPATIBLE|INCOMPATIBLE|REVIEW_NEEDED",
  "impact_analysis": {
    "breaking_changes": [
      "Frontend TypeScript types need regeneration",
      "API will reject payloads without 'tags' if required"
    ],
    "non_breaking_changes": [
      "If 'tags' is optional, fully backward compatible"
    ],
    "affected_components": [
      "api-tier/routes/projects.py",
      "ui-tier/types/Project.ts",
      "api-tier/schemas/project.py"
    ]
  },
  "recommendations": [
    {
      "option": "A",
      "description": "Make 'tags' optional (default: empty array)",
      "pros": ["Fully backward compatible", "No migration needed"],
      "cons": ["Existing projects won't have tags"],
      "effort": "low"
    },
    {
      "option": "B",
      "description": "Require 'tags' + backfill migration",
      "pros": ["All projects consistent", "Cleaner data model"],
      "cons": ["Breaking change", "Migration required"],
      "effort": "medium"
    },
    {
      "option": "C",
      "description": "Add to v2 API only",
      "pros": ["Zero impact on v1", "Clean separation"],
      "cons": ["API versioning overhead", "Maintain both versions"],
      "effort": "high"
    }
  ],
  "recommended_option": "A",
  "rationale": "Make 'tags' optional to maintain backward compatibility while enabling new feature"
}
```

---

### Orchestrator Enforcement

**The Claude orchestrator will**:
1. **Detect** when agents propose changes requiring consultation
2. **Block** implementation until compatibility checks complete
3. **Facilitate** parallel consultations when needed (e.g., API → UI + DB)
4. **Present** incompatibility options to user for decision
5. **Coordinate** implementation across agents after approval

**Status Tracking**:
```json
{
  "change_request_id": "uuid",
  "initiating_agent": "ui_architect",
  "consultations_required": ["api_architect"],
  "consultations_completed": [],
  "status": "awaiting_api_architect_review",
  "compatibility_status": "pending",
  "user_decision": null
}
```

---

### Example Multi-Agent Workflow

**Scenario**: UI needs new feature requiring API and DB changes

```
1. User requests: "Add project tagging feature"
   ↓
2. Orchestrator invokes UX Specialist first:
   → Design tag UI patterns
   ↓
3. UI Architect designs component:
   → Identifies need for API change: POST /projects needs 'tags' field
   → MANDATORY: Consult API Architect
   ↓
4. API Architect evaluates:
   → Determines DB schema change needed
   → MANDATORY: Consult DB Architect
   ↓
5. DB Architect responds:
   → COMPATIBLE: Can add 'tags' JSONB column
   → Provides migration script
   ↓
6. API Architect responds to UI Architect:
   → COMPATIBLE with Option A: Optional tags field
   → Provides updated OpenAPI spec
   ↓
7. Orchestrator presents plan to user:
   ✓ DB: Add tags column (migration provided)
   ✓ API: Add optional tags field (backward compatible)
   ✓ UI: Add tag selector component

   User approves: "Proceed"
   ↓
8. Coordinated implementation:
   a. DB Architect: Apply migration
   b. API Architect: Update routes + schemas
   c. UI Architect: Implement component
   d. UI QA: Test end-to-end
```

---

### Consultation Command Syntax

**For agents to use**:

```
CONSULT: <target_agent>
REASON: <change_description>
REQUEST: compatibility_check
PROPOSED_CHANGE: <detailed_change>
IMPACT_SCOPE: <affected_components>
```

**Example**:
```
CONSULT: api_architect
REASON: UI needs to display prompt version history
REQUEST: compatibility_check
PROPOSED_CHANGE: GET /prompts/{id}/versions endpoint
IMPACT_SCOPE: api-tier/routes/prompts.py, data-tier/models/prompt.py
```

---

## Context Persistence

### Memory File Format

**Location**: `.claude/context/{agent}_context.json`

```json
{
  "agent_name": "script-validator",
  "initialized": "2025-10-05T19:00:00Z",
  "total_sessions": 42,
  "validations": [
    {
      "task_uuid": "a1b2c3d4",
      "timestamp": "2025-10-05T20:00:00Z",
      "file": "scripts/deploy.sh",
      "status": "warn",
      "issues_found": 3,
      "issues_fixed": 2,
      "summary": "Fixed error handling, missing AWS profile check remains"
    }
  ],
  "learned_patterns": {
    "common_issues": {
      "missing-error-handling": 15,
      "hardcoded-paths": 8,
      "missing-shebangs": 3
    },
    "project_conventions": {
      "aws_profile_pattern": "terragrunt-{env}-{tier}",
      "script_location": "scripts/ or service/scripts/",
      "required_header": "#!/bin/bash\\nset -euo pipefail"
    }
  },
  "last_checkpoint": {
    "task_uuid": "a1b2c3d4",
    "timestamp": "2025-10-05T20:00:00Z",
    "cursor": "validation-42"
  }
}
```

### Resume Checkpoint

**Location**: `.claude/context/resume_checkpoint.json`

```json
{
  "last_activity": "2025-10-05T20:00:00Z",
  "active_tasks": [
    {
      "task_uuid": "a1b2c3d4",
      "agent": "script-validator",
      "status": "in_progress",
      "file": "scripts/deploy.sh",
      "started": "2025-10-05T19:58:00Z"
    }
  ],
  "pending_actions": [
    "Complete validation of scripts/deploy.sh",
    "Review API QA findings for core-service deployment"
  ]
}
```

---

## Routing Rules

### File Pattern → Agent Mapping

```yaml
routes:
  scripts:
    patterns:
      - "scripts/**/*.sh"
      - "scripts/**/*.bash"
      - "scripts/**/*.py"
      - "api-tier/scripts/**"
    agents: ["script-validator"]
    auto_trigger: true

  documentation:
    patterns:
      - "**/README*.md"
      - "**/SETUP*.md"
      - "**/GUIDE*.md"
      - "**/ARCHITECTURE*.md"
      - "**/TESTING*.md"
    agents: ["readme-validator"]
    auto_trigger: true

  ui_code:
    patterns:
      - "ui-tier/**/*.{ts,tsx,js,jsx}"
      - "**/mfe-*/**"
    agents: ["ui-architect", "ui-qa"]
    auto_trigger: false

  api_code:
    patterns:
      - "api-tier/**/*.py"
      - "**/routes/**"
      - "**/services/**"
    agents: ["api-architect", "api-qa"]
    auto_trigger: false

  database:
    patterns:
      - "data-tier/**/*.sql"
      - "**/migrations/**"
      - "**/models/**"
    agents: ["db-architect", "api-qa"]
    auto_trigger: false

policy:
  block_on:
    - "security-critical"
    - "data-loss-risk"
    - "spec-violation-major"
  warn_on:
    - "style-inconsistency"
    - "spec-violation-minor"
    - "performance-concern"
```

---

## Claude Code Task Tool Integration

### Spawning Validation Subagent

When a hook triggers or manual validation is requested:

```python
# Pseudo-code representation
Task(
    subagent_type="general-purpose",
    description="Validate script against build specs",
    prompt=f"""
You are the Script Validator subagent for PromptForge.

**Context:**
- Build specs: {BUILD_SPECS_DIR}
- Project root: {PROJECT_DIR}
- Context file: {CONTEXT_FILE}

**Task:**
Validate: {FILE_PATH}

**Validation checklist:**
{VALIDATION_RULES}

**Previous validations:**
{load_context(CONTEXT_FILE)}

**Expected output:**
{OUTPUT_ENVELOPE_SPEC}

Perform validation, auto-fix issues, and return JSON envelope.
"""
)
```

---

## Usage Examples

### Example 1: Automatic Script Validation

**Scenario**: User edits `scripts/deploy.sh`

**Flow**:
1. User makes changes via Edit tool
2. PostToolUse hook detects script file change
3. Hook invokes script-validator subagent via Task tool
4. Subagent:
   - Reads `scripts/deploy.sh`
   - Reads `PromptForge_Build_Specs/Phase2_APIs.md` (deployment section)
   - Runs shellcheck
   - Validates AWS profile usage matches project conventions
   - Checks error handling
   - Auto-fixes issues
   - Returns JSON envelope
5. Main session receives validation report
6. Context file updated with validation results

### Example 2: README Update Validation

**Scenario**: User updates `SETUP.md`

**Flow**:
1. User edits SETUP.md with new installation steps
2. PostToolUse hook triggers readme-validator
3. Subagent:
   - Validates all command examples
   - Checks file paths exist
   - Verifies alignment with build specs
   - Tests markdown syntax
   - Ensures completeness
   - Fixes formatting issues
   - Returns findings
4. User receives validation report with auto-fixes applied

### Example 3: Manual Multi-Agent Review

**User command**: "Review the entire API tier for Phase 2 compliance"

**Flow**:
```bash
# Main Claude session spawns multiple agents in parallel
Task[api-architect] → Reviews api-tier/ against Phase2_APIs.md
Task[api-qa] → Tests API endpoints, validates OpenAPI specs
Task[db-architect] → Reviews data models, migrations
Task[script-validator] → Validates api-tier/scripts/

# Each agent works independently, outputs JSON envelope
# Main session aggregates results, computes final verdict
# Merged report saved to .claude/reports/api-review-2025-10-05.json
```

---

## CLI Commands

### Initialization

```
"Initialize the orchestrator: create all context files, load subagent templates, check resume checkpoint"
```

### Manual Validation

```
"Validate scripts/deploy.sh against Phase 2 deployment specs"
```

```
"Validate all documentation files for spec compliance"
```

### Resume Operations

```
"Check resume checkpoint and continue any incomplete validations"
```

### Reporting

```
"Generate validation report for all scripts validated in the last 7 days"
```

```
"Summarize all QA findings across UI, API, and DB agents from today"
```

---

## Success Criteria

✅ **Automated Validation**
- PostToolUse hook triggers on script/readme changes
- Subagents validate against build specs automatically
- Issues auto-fixed when possible

✅ **Context Persistence**
- All validations logged to context files
- Learned patterns accumulate over time
- Resume checkpoint enables crash recovery

✅ **Spec Compliance**
- All validations cross-reference PromptForge_Build_Specs
- Violations reported with spec section references
- Compliance tracked over time

✅ **Multi-Agent Orchestration**
- Multiple agents can run in parallel via Task tool
- Results aggregated into unified reports
- Agent handoffs use standardized JSON envelopes

---

## Configuration Files

### Required Setup

1. Create context directory:
```bash
mkdir -p .claude/context
touch .claude/context/{ui_architect,api_architect,db_architect,apiqa,uiqa,validator,resume_checkpoint}_context.json
echo '{"agent_name":"validator","initialized":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","total_sessions":0,"validations":[]}' > .claude/context/validator_context.json
```

2. Install validation tools:
```bash
# Shell script validation
brew install shellcheck

# Python validation
pip install pylint black

# JavaScript/TypeScript validation
npm install -g eslint typescript
```

3. Configure hooks (see next section)

---

**Version**: 2.0 (Claude Code Enhanced)
**Maintainer**: PromptForge Team
**Last Updated**: 2025-10-05
