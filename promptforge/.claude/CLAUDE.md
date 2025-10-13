# PromptForge Claude Code Orchestrator

**Version**: 2.2.0
**Last Updated**: 2025-10-12
**Status**: ✅ Production Ready - Full Cross-Agent Orchestration Enabled
**Architecture**: Fully Self-Contained Multi-Agent System

This document serves as the **master orchestration guide** for Claude Code when working with PromptForge. It provides comprehensive documentation for the multi-subagent orchestration system with persistent context, automated validation hooks, cross-agent consultations, and build spec awareness.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Quick Start](#quick-start)
3. [Subagent Registry](#subagent-registry)
4. [Orchestration Rules](#orchestration-rules)
5. [Automated Validation System](#automated-validation-system)
6. [Cross-Agent Compatibility](#cross-agent-compatibility)
7. [Context Persistence](#context-persistence)
8. [Build Spec References](#build-spec-references)
9. [Usage Examples](#usage-examples)
10. [Configuration & Setup](#configuration--setup)

---

## Project Structure

```
promptforge/
├── .claude/                               # Claude Code configuration (THIS DIRECTORY)
│   ├── CLAUDE.md                         # This file - master orchestrator
│   ├── REORGANIZATION_COMPLETE.md        # Migration documentation
│   ├── specs/                            # Build specifications (organized by phase)
│   │   ├── README.md                     # Spec index with dependency matrix
│   │   ├── 00_meta/                      # Meta specifications
│   │   ├── 01_phase1_foundation/         # Phase 1: Core UI
│   │   ├── 02_phase2_core_features/      # Phase 2: APIs, Evaluation, Insights, Models, Traces, UI
│   │   ├── 03_phase3_advanced/           # Phase 3: Privacy, SaaS
│   │   └── 04_phase4_enterprise/         # Phase 4: Enterprise features
│   ├── agents/                           # Subagent templates (organized by role)
│   │   ├── README.md                     # Agent registry with workflow rules
│   │   ├── 00_meta/                      # Agent templates (coming soon)
│   │   ├── 01_architecture/              # UI, API, DB, UX architects
│   │   ├── 02_quality/                   # Checker, API QA, UI QA
│   │   ├── 03_operations/                # Doc Context Tracker
│   │   └── 04_validators/                # Script & README validators
│   ├── context/                          # Persistent agent memory
│   │   ├── README.md                     # Context file documentation
│   │   ├── agents/                       # Agent-specific state
│   │   ├── workflow/                     # Workflow coordination
│   │   └── schema/                       # JSON validation schemas
│   ├── hooks/                            # Event-driven hooks
│   │   └── post-tool-use.sh             # Auto-validation trigger
│   ├── scripts/                          # Workflow management scripts
│   │   ├── workflow-manager.sh          # Approval workflow tracking
│   │   └── validate-context.sh          # Context file validation
│   ├── templates/                        # Documentation templates
│   │   └── approval-checklist.md        # Checker approval checklist
│   └── reports/                          # Validation reports (generated)
├── ui-tier/                              # React micro-frontends
├── api-tier/                             # FastAPI backend
├── data-tier/                            # PostgreSQL database
└── scripts/                              # Deployment & utility scripts
```

---

## Quick Start

### 1. Verify Installation

```bash
cd /Users/rohitiyer/datagrub/promptforge
ls -la .claude/hooks/post-tool-use.sh
ls -la .claude/context/
ls -la .claude/specs/
ls -la .claude/agents/
```

### 2. View Subagent Configuration

```
"Show me all configured subagents"
"List agent status and locations"
```

### 3. Test Automatic Validation

```bash
# Edit any script - validation runs automatically
vim scripts/deploy.sh

# Edit any README - validation runs automatically
vim README.md
```

### 4. Manual Agent Invocation

```
"Invoke Script Validator to check scripts/deploy.sh"
"Have UI Architect review ui-tier/mfe-projects"
"Run API QA tests on api-tier/routes"
```

### 5. Check Context Status

```bash
ls -la .claude/context/agents/
cat .claude/context/agents/validator.json
```

---

## Subagent Registry

**Total Agents**: 12 (5 auto-triggered, 7 manual invocation)

### 🔍 Validation Agents (Auto-triggered)

#### Script Validator
**Location**: `.claude/agents/04_validators/script-validator.md`
**Version**: 2.0.0
**Status**: ✅ Active
**Trigger**: Auto on Write/Edit to `scripts/**/*.{sh,py,js,ts}`
**Context**: `.claude/context/agents/validator.json`

**Responsibilities**:
- Syntax validation (shellcheck, pylint, eslint, tsc)
- Security checks (no hardcoded credentials)
- Build spec compliance
- Error handling verification
- Dependency and path validation
- Auto-fix safe issues

**Invocation**: Automatic when editing scripts

---

#### README Validator
**Location**: `.claude/agents/04_validators/readme-validator.md`
**Version**: 2.0.0
**Status**: ✅ Active
**Trigger**: Auto on Write/Edit to `**/{README,SETUP,GUIDE}*.md`
**Context**: `.claude/context/agents/validator.json`

**Responsibilities**:
- Command accuracy (validate all code examples)
- File path verification (ensure paths exist)
- Build spec alignment
- Markdown quality (formatting, links, code blocks)
- Auto-fix formatting issues

**Invocation**: Automatic when editing documentation

---

### 🏗️ Architecture Agents (3 Auto-triggered, 1 Manual)

#### API Architect ⭐ AUTO-TRIGGERED
**Location**: `.claude/agents/01_architecture/API_Architect_Agent.md`
**Version**: 2.0.0
**Status**: ✅ Complete
**Trigger**: **AUTO** on Write/Edit to `api-tier/**/*.py` (routes, services, models)
**Context**: `.claude/context/agents/api_architect.json`
**Build Specs**:
- `specs/02_phase2_core_features/apis/Phase2_APIs.md` (General API architecture)
- `specs/02_phase2_core_features/insights/Phase2_Summarization_Insights_API_DTA.md` (Deep Insights API)

**Responsibilities**:
- **AUTO-REVIEW** API changes for security, best practices, breaking changes
- Define routes (Projects, Prompts, Evaluations, Traces)
- Manage API authentication, versioning, schema validation
- Implement evaluation abstraction layer (Ragas, DeepEval, MLflow, Deepchecks, Arize Phoenix)
- **MANDATORY**: Consult UI Architect AND DB Architect before making API changes
- **MANDATORY**: Provide compatibility assessments when consulted by other agents

**Auto-Review Checks**:
- REST API best practices
- Security vulnerabilities (auth, authorization, input validation)
- Error handling patterns
- HTTP status code correctness
- Schema alignment with database models
- Breaking API changes detection
- Cross-tier compatibility (UI ↔ API ↔ DB)

**Commands**:
- `Create_API_Route` - Define new API route
- `Test_API` - Run FastAPI test cases
- `Validate_Security` - Security compliance checks
- `Consult_UI_Architect` - Request UI compatibility check
- `Consult_DB_Architect` - Request DB compatibility check
- `Provide_Compatibility_Assessment` - Respond to consultation requests

**Invocation**:
- **Automatic**: When editing `api-tier/routes/*.py`, `api-tier/services/*.py`, `api-tier/models/*.py`
- **Manual**: `"Invoke API Architect to implement evaluation routes per Phase 2 Evaluation Framework"`

**What You'll See**:
```
🏗️ Reviewing api-route: playground.py

**API Architect Review**: ⚠️ WARNINGS FOUND
- Security: Missing rate limiting on POST endpoint
- Breaking Change: Response schema changed (version bump needed)
- Cross-Tier Impact: UI types need regeneration

[Detailed findings...]
```

---

#### UI Architect ⭐ AUTO-TRIGGERED
**Location**: `.claude/agents/01_architecture/UI_Architect_Agent.md`
**Version**: 2.0.0
**Status**: ✅ Complete
**Trigger**: **AUTO** on Write/Edit to `ui-tier/**/*.{tsx,ts,jsx,js}` (components, pages, hooks)
**Context**: `.claude/context/agents/ui_architect.json`
**Build Specs**:
- `specs/01_phase1_foundation/Phase1_CoreUI.md` (Component architecture)
- `specs/02_phase2_core_features/ui/Phase2_UI_Framework.md` (Routing, state, design system)
- `specs/02_phase2_core_features/insights/Phase2_Insights_History.md` (Deep Insights UI)

**Responsibilities**:
- **AUTO-REVIEW** UI changes for design system compliance, accessibility, best practices
- Create/maintain React UI components (micro-frontends)
- Ensure modular MFE structure
- Integrate frontend with backend APIs
- Enforce WCAG AAA accessibility and UX best practices
- Follow UI Framework standards (routing, state persistence, design system)
- **MANDATORY**: Consult UX Specialist for all UI components (design system compliance)
- **MANDATORY**: Consult API Architect if API calls detected or contracts changed

**Auto-Review Checks**:
- React component best practices (hooks, state management)
- Module Federation integration (remote/host configuration)
- Design system compliance (colors, spacing, typography)
- Accessibility patterns (ARIA labels, keyboard navigation)
- Error boundaries and loading states
- API integration patterns
- Cross-tier compatibility (API contracts, TypeScript types)

**Commands**:
- `Build_UI_Component` - Build new component
- `Link_Backend_API` - Connect to API route
- `Run_UI_Tests` - Execute regression/integration tests
- `Consult_UX_Specialist` - Request design system review (MANDATORY)
- `Consult_API_Architect` - Request compatibility check for API changes

**Invocation**:
- **Automatic**: When editing `ui-tier/components/*.tsx`, `ui-tier/pages/*.tsx`, `ui-tier/hooks/*.ts`
- **Manual**: `"Invoke UI Architect to review ui-tier/mfe-projects against Phase 1 CoreUI specs"`

**What You'll See**:
```
🏗️ Reviewing ui-component: ProjectCard.tsx

**UI Architect Review**: ⚠️ DESIGN SYSTEM VIOLATIONS DETECTED
- Custom color #FF0000 used (should be #FF385C from design system)
- Spacing 12px not on 8px grid (use 8px or 16px)
- Missing loading state for API calls
- UX Specialist consultation required

[Detailed findings...]
```

---

#### DB Architect ⭐ AUTO-TRIGGERED
**Location**: `.claude/agents/01_architecture/DB_Architect_Agent.md`
**Version**: 2.0.0
**Status**: ✅ Complete
**Trigger**: **AUTO** on Write/Edit to `data-tier/**/*.py` (models, migrations, seed_data)
**Context**: `.claude/context/agents/db_architect.json`
**Build Specs**: `specs/02_phase2_core_features/apis/Phase2_APIs.md`

**Responsibilities**:
- **AUTO-REVIEW** database changes for schema design, migration safety, performance
- Maintain normalized schemas (PostgreSQL + Redis)
- Design tables for trace logging and metrics
- Implement seed scripts (golden, edge, adversarial datasets)
- **MANDATORY**: Consult API Architect for ALL database schema changes (API ORM alignment)
- **MANDATORY**: Provide compatibility assessments when consulted by API Architect

**Auto-Review Checks**:
- Schema design best practices (normalization, indexes)
- Migration safety (rollback scripts, data integrity)
- Database constraints (foreign keys, NOT NULL, defaults)
- Query performance implications
- Data type correctness
- Breaking schema changes
- Cross-tier compatibility (API ORM models alignment)

**Commands**:
- `Create_Table` - Define/update schema
- `Seed_Data` - Load seed data
- `Run_Migration_Test` - Validate migrations
- `Consult_API_Architect` - Request API compatibility check (MANDATORY)
- `Provide_Compatibility_Assessment` - Respond to consultation requests

**Invocation**:
- **Automatic**: When editing `data-tier/models/*.py`, `data-tier/migrations/*.py`, `database-tier/seed_data/*.py`
- **Manual**: `"Invoke DB Architect to review data-tier schema for Phase 2 requirements"`

**What You'll See**:
```
🏗️ Reviewing db-migration: add_tags_column.py

**DB Architect Review**: ⚠️ API SYNC REQUIRED
- New column: tags JSONB[] added to projects table
- Missing index on tags column (recommended for filtering)
- API Architect consultation required (ORM model needs update)
- Rollback script present ✓

[Detailed findings...]
```

---

### 🎨 Design Agent (Manual)

#### UX Specialist
**Location**: `.claude/agents/01_architecture/UX_Specialist_Agent.md`
**Version**: 2.0.0
**Status**: ✅ Complete
**Context**: `.claude/context/agents/ux_specialist.json`
**Build Specs**: All phases (design system applies across entire application)

**Responsibilities**:
- Maintain unified design system (Airbnb-style: colors, typography, spacing, shadows)
- Enforce WCAG 2.1 AAA accessibility standards
- Define user interaction patterns (hover, focus, disabled states)
- Establish responsive design patterns (mobile-first)
- Review UI components for design consistency
- Collaborate with UI Architect (provides specs before implementation)
- Guide UI QA on UX validation criteria

**Design System**:
- **Colors**: Primary #FF385C, Neutral #222222, soft contrast
- **Typography**: Inter/Cereal fonts, 8-level scale
- **Spacing**: 8px grid (0, 8, 16, 24, 32, 48, 64, 96)
- **Style**: Modern minimalism, generous whitespace, rounded corners (12-16px)
- **Shadows**: Soft only, no hard edges
- **Accessibility**: AAA contrast ratios (7:1 normal, 4.5:1 large text)

**Commands**:
- `Review_UI_Component` - Review component for UX/accessibility
- `Generate_Style_Guide` - Update design system documentation
- `Validate_Accessibility` - WCAG AAA compliance audit
- `Apply_Design_Tokens` - Provide design specifications

**Orchestration Priority**: **Consult UX Specialist FIRST** for all UX/design/style decisions

**Invocation**:
```
"Invoke UX Specialist to design search results card component for evaluations page"
"Have UX Specialist audit accessibility of project creation form"
"UX Specialist: review Button component for design consistency"
```

---

### 🧪 QA Agents (Manual)

#### API QA
**Location**: `.claude/agents/02_quality/API_QA_Agent.md`
**Version**: 2.0.0
**Status**: ✅ Complete
**Context**: `.claude/context/agents/apiqa.json`
**Build Specs**:
- `specs/02_phase2_core_features/apis/Phase2_APIs.md` (General API testing)
- `specs/02_phase2_core_features/insights/Phase2_Summarization_Insights_API_DTA.md` (Deep Insights API)

**Responsibilities**:
- Run unit and integration tests for backend routes
- Execute MFE-specific API tests when MFE UI or API changes detected
- Validate OpenAPI specifications
- Ensure consistent status codes and payload schemas
- Log results and coverage reports

**Commands**:
- `Run_API_Tests` - Execute test suites
- `Run_MFE_Tests` - Execute MFE-specific test suite
- `Compare_Spec` - Validate against design specs
- `Log_Results` - Record test outputs

**Invocation**:
```
"Run API QA tests on all api-tier routes"
"Run API QA MFE tests for mfe-playground module"
```

---

#### UI QA
**Location**: `.claude/agents/02_quality/UI_QA_Agent.md`
**Version**: 2.0.0
**Status**: ✅ Complete
**Context**: `.claude/context/agents/uiqa.json`
**Build Specs**:
- `specs/01_phase1_foundation/Phase1_CoreUI.md` (General UI testing)
- `specs/02_phase2_core_features/insights/Phase2_Insights_History.md` (Deep Insights UI)

**Responsibilities**:
- Execute Playwright tests for components/flows
- Validate UI ↔ API integration
- Run regression suite for merge requests
- Generate test and coverage reports
- Visual regression testing
- Accessibility testing (WCAG AAA compliance)

**Commands**:
- `Run_E2E_Tests` - Execute Playwright E2E tests
- `Validate_Integration` - Verify UI ↔ API communication
- `Generate_Report` - Create test summary
- `Run_Visual_Regression` - Compare screenshots to detect visual changes
- `Run_Accessibility_Tests` - Validate WCAG AAA compliance

**Invocation**:
```
"Run UI QA Playwright tests for ui-tier/mfe-evaluations"
"Run accessibility tests on mfe-projects for WCAG AAA compliance"
```

---

### 📚 Documentation Agent (Manual)

#### Doc Context Tracker
**Location**: `.claude/agents/03_operations/Doc_Context_Tracker_Agent.md`
**Version**: 2.0.0
**Status**: ✅ Complete
**Context**: `.claude/context/agents/doc_tracker.json`

**Responsibilities**:
- Track and update prompt templates
- Monitor new documents/scripts for compliance
- Sync prompt documentation with other subagents
- Update templates to reflect design/test changes
- Generate documentation indices

**Commands**:
- `Update_Prompt_Template` - Apply template updates
- `Sync_Context` - Merge changes from other agents
- `Audit_Document` - Review/validate documentation
- `Generate_Documentation_Index` - Create spec/agent index
- `Detect_Outdated_Documentation` - Find stale docs

**Invocation**:
```
"Invoke Doc Context Tracker to sync agent templates with latest changes"
"Have Doc Tracker generate documentation index for all Phase 2 specs"
```

---

#### Auth Token Generator
**Location**: `.claude/agents/03_operations/Auth_Token_Generator_Agent.md`
**Version**: 1.0.0
**Status**: ✅ Complete
**Context**: `.claude/context/agents/auth_token_generator.json`

**Responsibilities**:
- Generate authentication tokens for API testing and curl requests
- Create or find test users in test organizations
- Seed test users with specific emails and organizations
- Provide ready-to-use authenticated curl commands
- Support both pytest fixtures and manual command-line testing
- Maintain test user database for consistent testing

**Commands**:
- `Generate_Token` - Create authentication token for test user
- `Create_Test_User` - Seed new test user in database
- `List_Test_Users` - Show all available test users
- `Get_Curl_Command` - Generate curl command with authentication

**Available Scripts**:
- `api-tier/scripts/get_test_token.sh` - Quick token generation for demo user
- `api-tier/scripts/create_test_user.py` - Create custom test users with specific emails/orgs

**Default Test User**:
- Email: `demo@promptforge.ai`
- Password: `demo123`
- Organization: Demo Organization
- Role: admin

**Invocation**:
```
"Generate an auth token for testing"
"Create a test user john@acme.com in ACME Corp and generate a token"
"Give me a curl command to test POST /api/v1/projects with authentication"
"How do I get a token in pytest tests?"
```

**Quick Usage**:
```bash
# Get token for demo user
cd /Users/rohitiyer/datagrub/promptforge/api-tier
./scripts/get_test_token.sh

# Create custom test user
python scripts/create_test_user.py --email alice@example.com --org "Example Corp"

# Use in pytest
# The auth_headers fixture automatically provides authentication
```

---

### 🔒 Quality Assurance Agent (Manual)

#### Checker Agent
**Location**: `.claude/agents/02_quality/Checker_Agent.md`
**Version**: 2.0.0
**Status**: ✅ Complete
**Context**: `.claude/context/agents/checker.json`
**Build Specs**: All phases (reviews against all specifications)

**Responsibilities**:
- **MANDATORY**: Final review gate for all subagent outputs (UI, API, DB, UX, QA)
- Ensure deliverables meet project specifications and quality expectations
- Prevent regressions by tracking error patterns and historical issues
- Cross-agent consistency checks (UI ↔ API ↔ DB alignment)
- Continuous learning from failures to improve guardrails
- Approve/flag/reject updates before user-facing publication
- **Invoke API QA Agent before approving ANY MFE changes**

**Quality Gates**:
1. **Specification Alignment** - Implementation matches build specs (BLOCK if not met)
2. **Regression Prevention** - All regression tests pass (BLOCK if failed)
3. **Error Pattern Avoidance** - No repeated known issues (WARNING/BLOCK if critical)
4. **Test Coverage** - Unit >80%, integration critical paths (BLOCK if below threshold)
5. **Documentation** - Code comments, API docs, guides updated (WARNING if incomplete)
6. **MFE API Integration Tests** - All MFE-specific API tests pass (BLOCK if ANY test fails)

**Error Pattern Categories**:
- **API Errors**: Missing try-catch, incorrect status codes, missing validation
- **UI Errors**: Missing loading states, accessibility violations, memory leaks
- **DB Errors**: Missing indexes, N+1 queries, missing rollback scripts
- **Integration Errors**: Type mismatches, breaking API contracts, schema inconsistencies
- **Module Federation Errors**: Double context provider wrapping, missing expose paths

**Commands**:
- `Pre_Check` - Validate readiness before implementation (risk assessment, warnings)
- `Post_Check` - Validate implementation quality (compliance, regressions)
- `Record_Error` - Log error pattern for future prevention
- `Run_Regression_Suite` - Execute all regression tests
- `Generate_Quality_Report` - Comprehensive quality assessment

**Invocation**:
```
"Invoke Checker Agent to review API Architect's evaluation endpoints implementation"
"Run Pre_Check for new project tagging feature"
"Have Checker validate all changes before deployment"
```

**Output Format**:
```json
{
  "agent_name": "API_Architect_Agent",
  "status": "Approved|Flagged|Rejected",
  "confidence": 0.96,
  "review_notes": "All endpoints follow REST standards. No schema mismatches found.",
  "action_items": [],
  "regressions_detected": false
}
```

---

## Orchestration Rules

### ⚠️ MANDATORY CHECKER APPROVAL POLICY ⚠️

**CRITICAL RULE**: All architect agent implementations (UI, API, DB, UX) **MUST** receive Checker Agent approval before presenting results to the user.

#### Enforcement Workflow

**Phase 1: Add Approval Checkpoint**
```bash
.claude/scripts/workflow-manager.sh add <task_uuid> <architect_agent>
# Generates unique task identifier and tracks it in workflow_state.json
```

**Phase 2: Invoke Checker Agent**
```
"Invoke Checker Agent to perform Post_Check validation of <architect_agent>'s work on <task_description> against relevant build specifications"
```

**Phase 3: Wait for Approval Status**
Checker Agent will return one of three statuses:
- **APPROVED** (✅): All quality gates passed, no issues
- **PASS_WITH_WARNINGS** (⚠️): Quality gates passed with minor warnings
- **BLOCKED** (🚫): Critical issues detected, requires fixes

**Phase 4: Handle Status**
- **If BLOCKED**: Present findings to architect agent, require fixes, re-submit to Checker
- **If APPROVED or PASS_WITH_WARNINGS**: Proceed to Phase 5

**Phase 5: Record Approval**
```bash
.claude/scripts/workflow-manager.sh approve <task_uuid> <approval_status>
# Records approval in workflow_state.json approval_history
```

**Phase 6: Present to User with Checker Badge**

**APPROVED Format**:
```markdown
**Checker Agent Validation**: ✅ APPROVED (96% confidence)
- All 6 quality gates passed
- No issues found
- Implementation ready for use
```

**PASS_WITH_WARNINGS Format**:
```markdown
**Checker Agent Validation**: ⚠️ PASS_WITH_WARNINGS (94% confidence)
- 5/6 quality gates passed
- Minor warnings: [list warnings]
- Implementation approved with recommendations
```

#### Pre-User-Response Checklist

Before every user-facing response after architect work, verify:
- [ ] Approval checkpoint added via workflow-manager.sh
- [ ] Checker Agent invoked with Post_Check
- [ ] Approval status received (APPROVED, PASS_WITH_WARNINGS, or BLOCKED)
- [ ] If BLOCKED: Issues addressed and re-checked
- [ ] Workflow state updated with approval
- [ ] Checker badge included in response

**Reference**: See `.claude/templates/approval-checklist.md` for complete checklist

---

### Orchestration Priority Rules

1. **UX Specialist FIRST**: Consult for all UX/design/style decisions before implementation
2. **Checker LAST**: MANDATORY approval after all architect implementations before user presentation
3. **No user-facing response without Checker approval status**

---

### 🤖 AUTOMATIC CHECKER INVOCATION (v2.0.1)

**Status**: ✅ ACTIVE - Enforces mandatory Checker approval automatically

**What Changed**: Checker Agent invocation is now **automatic** for all architect work. You no longer need to manually invoke the Checker - the orchestrator handles this automatically.

#### Automatic Detection

The orchestrator automatically detects architect work when:

1. **Explicit Invocation**: User command contains keywords like:
   - "Invoke [UI|API|DB|UX] Architect..."
   - "Have [UI|API|DB|UX] Architect..."
   - "[UI|API|DB|UX] Architect: ..."

2. **Task Tool Usage**: Task tool invoked with architect agent templates

3. **Implicit Work**: Major changes to architect-managed files (optional)

#### Automatic Workflow

**Old Manual Flow** (Deprecated):
```
User Request → Invoke Architect → Architect Work → User Manually Invokes Checker → Present Results
                                                    ↑
                                        Easy to forget, inconsistent
```

**New Automatic Flow** (Active):
```
User Request → Invoke Architect → Architect Work → AUTO-INVOKE Checker → Present with Badge
                                                    ↑
                                        Automatic, enforced, guaranteed
```

#### Detailed Auto-Flow

```
Step 1: User Request
  "Invoke UI Architect to create Button component"
    ↓
Step 2: Orchestrator Detection
  - Detects architect invocation
  - Generates task_uuid: "task-abc-123"
  - Adds approval checkpoint
    ↓
Step 3: Architect Execution
  - UI Architect creates Button component
  - Collects output, changed files, relevant specs
  - Does NOT present to user yet
    ↓
Step 4: AUTO-INVOKE Checker
  - Orchestrator automatically invokes Checker Post_Check
  - Passes architect output + context
  - Waits for approval status
    ↓
Step 5: Status Handling
  IF BLOCKED:
    - Present Checker findings to USER
    - Offer options: manual fix, architect re-work, override
    - Loop back if user chooses re-work
  IF APPROVED or PASS_WITH_WARNINGS:
    - Record approval in workflow state
    - Proceed to Step 6
    ↓
Step 6: Present to User
  Response includes automatic Checker badge:

  **Checker Agent Validation**: ✅ APPROVED (96% confidence)
  - Quality Gates: 6/6 passed
  - Regressions: None detected
  - Specification Compliance: 100%

  [Architect Output]
```

#### What You See

**Before (Manual)**:
```
User: "Invoke UI Architect to create ProjectCard"
Claude: [Creates component]
        "Component created successfully."
```
❌ No quality validation, no assurance

**After (Automatic)**:
```
User: "Invoke UI Architect to create ProjectCard"
Claude: [Creates component]
        [Automatically invokes Checker]

        **Checker Agent Validation**: ✅ APPROVED (96% confidence)
        - Quality Gates: 6/6 passed
        - Regressions: None detected
        - Specification Compliance: 100%

        "Component created successfully with the following features..."
```
✅ Quality validated, confidence score, full transparency

#### When Checker Returns BLOCKED

```
User: "Invoke API Architect to add DELETE /projects endpoint"
Claude: [API Architect creates endpoint]
        [Automatically invokes Checker]
        [Checker finds critical issue]

        **Checker Agent Validation**: 🚫 BLOCKED

        Critical issues found that must be addressed:

        1. Missing permission check (HIGH)
           - Location: api-tier/routes/projects.py:DELETE endpoint
           - Risk: Any authenticated user could delete any project
           - Fix: Add owner/admin permission check

        2. Missing cascade delete logic (MEDIUM)
           - Risk: Orphaned prompts and evaluations
           - Fix: Implement soft delete with is_deleted flag

        Options:
        a) Review and manually fix the issues
        b) Have API Architect address issues automatically
        c) Override Checker (requires explicit confirmation)

        Which would you like to do?
```

User maintains control but gets automatic quality validation.

#### Edge Cases

**Multiple Architects**:
```
User: "Invoke UI Architect and API Architect to build project form"
Claude: - Invokes both architects
        - Auto-invokes Checker for EACH architect's output
        - Presents combined results with both badges
```

**Checker Unavailable**:
```
Claude: ⚠️ Checker Agent validation failed (timeout)
        Presenting unvalidated architect output.
        Recommend manual review before deployment.
```

**User Direct File Edits** (No Auto-Invoke):
```
User: [Uses Edit tool to modify Button.tsx directly]
Claude: [Completes edit]

        "Would you like me to invoke Checker Agent to validate this change?"
```
Suggests but doesn't force for direct edits.

#### Benefits

1. **100% Coverage**: No architect work escapes quality validation
2. **Zero Cognitive Load**: You don't need to remember to invoke Checker
3. **Consistent Quality**: Every architect output gets the same rigorous review
4. **Transparency**: Checker badge shows exactly what was validated
5. **Confidence Scores**: Know the reliability of each validation
6. **Regression Prevention**: Historical error patterns caught automatically

#### Disabling (Emergency Only)

If automatic invocation causes issues:

```bash
# Temporary disable
export DISABLE_AUTO_CHECKER=true

# Re-enable
unset DISABLE_AUTO_CHECKER
```

#### Metrics Tracking

The system tracks:
- **Coverage Rate**: % of architect work with Checker validation (Target: 100%)
- **Blocked Rate**: % of outputs blocked by Checker (Target: <10%)
- **Approval Time**: Avg time from architect → Checker approval (Target: <30s)
- **False Positive Rate**: % of BLOCKED that user overrides (Target: <5%)

**View metrics**:
```
"Show me Checker validation metrics for the last 7 days"
```

#### Documentation

**Full Strategy**: `.claude/CHECKER_AUTO_INVOCATION_STRATEGY.md`
**Checker Agent Details**: `.claude/agents/02_quality/Checker_Agent.md`
**Workflow Manager**: `.claude/scripts/workflow-manager.sh`

---

## Automated Validation System

### Hook: PostToolUse (Cross-Tier Architectural Review)

**File**: `.claude/hooks/post-tool-use.sh`

**Triggers**: After any `Write` or `Edit` tool use on:

**Validators (Auto-fix):**
- Scripts: `scripts/**/*.{sh,bash,py,js,ts}` → Script Validator
- Documentation: `**/{README,SETUP,GUIDE,INSTALL,DEPLOY,ARCHITECTURE,TESTING}*.md` → README Validator

**Architects (Review + Cross-Agent Consultation):**
- API Pydantic Schemas: `api-tier/schemas/**/*.py` → API Architect (→ UI, DB, API QA)
- API Routes: `api-tier/routes/**/*.py` → API Architect (→ UI, DB, API QA)
- API Services: `api-tier/services/**/*.py` → API Architect (→ UI, DB, API QA)
- API Models: `api-tier/models/**/*.py` → API Architect (→ UI, DB, API QA)
- DB Models: `data-tier/models/**/*.py` → DB Architect (→ API Architect)
- DB Migrations: `data-tier/migrations/**/*.py` → DB Architect (→ API Architect)
- DB Seed Data: `database-tier/seed_data/**/*.{py,sql}` → DB Architect (→ API Architect)
- UI Components: `ui-tier/components/**/*.{tsx,ts}` → UI Architect (→ UX Specialist, API Architect)
- UI Pages: `ui-tier/pages/**/*.{tsx,ts}` → UI Architect (→ UX Specialist, API Architect)
- UI Hooks/Services: `ui-tier/hooks/**/*.ts`, `ui-tier/services/**/*.ts` → UI Architect (→ UX Specialist, API Architect)

**Behavior**:
1. Detects file type and tier (validator vs architect)
2. Invokes appropriate subagent via Claude Code Task tool
   - **Validators** (script, readme): Auto-fix safe issues
   - **Architects** (API, DB, UI): Architectural review, flag concerns, request consultations
3. Architect identifies cross-tier impacts and requests consultations via `consultation_requests` in output
4. Orchestrator processes consultation requests and invokes consulted agents in parallel
5. Consultation responses aggregated and presented with consolidated recommendations
6. Reports findings back to main session
7. Updates context with learnings

**Validation Context Injection**:
```bash
SPECS_DIR=".claude/specs"
PROJECT_DIR="."  # Relative to promptforge root
```

Every validation task automatically receives:
- Full path to build specs
- Current project structure
- Relevant phase documentation
- Previous validation history from context files

---

### Validation Rules

#### Script Validation (Shell/Python/JS/TS)

**Critical Checks**:
1. **Syntax validation**: shellcheck, pylint, eslint, tsc
2. **Build spec alignment**: Cross-reference with build specs
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

#### README/Documentation Validation

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

## Cross-Agent Compatibility

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
   - INCOMPATIBLE: Recommend options (versioning, new endpoint, migration plan)
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
   2a. Invoke UI Architect: Will UI components break?
   2b. Invoke DB Architect: Does database schema support this?
   ↓
3. Both agents evaluate and respond:
   - UI Architect: COMPATIBLE | INCOMPATIBLE (with recommendations)
   - DB Architect: COMPATIBLE | INCOMPATIBLE (with recommendations)
   ↓
4. If INCOMPATIBLE from either:
   API Architect provides options (modify API, add migration, version API, phased rollout)
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
   ↓
4. API Architect responds with:
   - COMPATIBLE: Proceed with migration
   - INCOMPATIBLE: Recommend options (nullable columns, views, blue-green migration)
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
      "Frontend TypeScript types need regeneration"
    ],
    "non_breaking_changes": [
      "If 'tags' is optional, fully backward compatible"
    ],
    "affected_components": [
      "api-tier/routes/projects.py",
      "ui-tier/types/Project.ts"
    ]
  },
  "recommendations": [
    {
      "option": "A",
      "description": "Make 'tags' optional (default: empty array)",
      "pros": ["Fully backward compatible"],
      "cons": ["Existing projects won't have tags"],
      "effort": "low"
    }
  ],
  "recommended_option": "A",
  "rationale": "Make 'tags' optional to maintain backward compatibility while enabling new feature"
}
```

---

## Context Persistence

### Memory File Format

**Location**: `.claude/context/agents/{agent}.json`

```json
{
  "agent_name": "script-validator",
  "initialized": "2025-10-11T00:00:00Z",
  "total_sessions": 42,
  "validations": [
    {
      "task_uuid": "a1b2c3d4",
      "timestamp": "2025-10-11T20:00:00Z",
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
    "timestamp": "2025-10-11T20:00:00Z",
    "cursor": "validation-42"
  }
}
```

### Resume Checkpoint

**Location**: `.claude/context/workflow/resume_checkpoint.json`

```json
{
  "last_activity": "2025-10-11T20:00:00Z",
  "active_tasks": [
    {
      "task_uuid": "a1b2c3d4",
      "agent": "script-validator",
      "status": "in_progress",
      "file": "scripts/deploy.sh",
      "started": "2025-10-11T19:58:00Z"
    }
  ],
  "pending_actions": [
    "Complete validation of scripts/deploy.sh",
    "Review API QA findings for core-service deployment"
  ]
}
```

### Workflow State Tracking

**File**: `.claude/context/workflow/workflow_state.json`

Tracks all approval checkpoints and maintains audit trail:
- `pending_approvals[]`: Tasks awaiting Checker approval
- `approval_history[]`: Completed approvals with status
- `enforcement_rules`: Configuration for mandatory approval policy

**Commands**:
- `.claude/scripts/workflow-manager.sh add <task_uuid> <architect_agent>` - Add checkpoint
- `.claude/scripts/workflow-manager.sh check <task_uuid>` - Check status
- `.claude/scripts/workflow-manager.sh approve <task_uuid> <status>` - Record approval
- `.claude/scripts/workflow-manager.sh list` - List pending approvals
- `.claude/scripts/workflow-manager.sh history [limit]` - View approval history

---

## Build Spec References

All subagents reference specifications from `.claude/specs/`:

```
specs/
├── README.md                                       # Spec index with dependency matrix
├── 00_meta/                                        # Meta specifications
│   ├── Competitor_Analysis.md
│   └── MODEL_PROVIDER_CONFIGURATION_SPEC.md
├── 01_phase1_foundation/                          # Phase 1: Core UI
│   └── Phase1_CoreUI.md
├── 02_phase2_core_features/                       # Phase 2: Core features (domain-grouped)
│   ├── apis/
│   │   ├── Phase2_APIs.md
│   │   ├── Phase2_API_SecurityRequirements.md
│   │   └── Phase2_API_PerformanceRequirements.md
│   ├── evaluation/
│   │   ├── Phase2_Evaluation_Framework.md
│   │   ├── Phase2_Evaluation_Dashboard.md
│   │   └── Phase2_Evaluation_Playground.md
│   ├── insights/
│   │   ├── Phase2_Summarization_Insights_API_DTA.md
│   │   ├── Phase2_Insights_History.md
│   │   └── Phase2_Insight_Comparator.md
│   ├── models/
│   │   └── Phase2_Model_Dashboard.md
│   ├── traces/
│   │   └── Phase2_Trace_Dashboard.md
│   └── ui/
│       └── Phase2_UI_Framework.md
├── 03_phase3_advanced/                            # Phase 3: Advanced features
│   ├── Phase3_Privacy_Framework.md
│   └── Phase3_SaaSRefinement.md
└── 04_phase4_enterprise/                          # Phase 4: Enterprise features
    └── Phase4_EnterpriseEnablement.md
```

Subagents automatically load relevant specs based on:
- File paths (ui-tier → Phase1 + Phase2_UI_Framework, api-tier → Phase2)
- Task context (evaluation → Evaluation Framework, insights → Deep Insights specs)
- Feature names (mfe-insights → Phase2_Summarization_Insights_API_DTA.md + Phase2_Insights_History.md)
- Explicit references in prompts

**For full spec details, see**: `.claude/specs/README.md`

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
   - Reads `.claude/specs/02_phase2_core_features/apis/Phase2_APIs.md` (deployment section)
   - Runs shellcheck
   - Validates AWS profile usage matches project conventions
   - Checks error handling
   - Auto-fixes issues
   - Returns JSON envelope
5. Main session receives validation report
6. Context file updated with validation results

---

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

---

### Example 3: UI Component Development with Checker Approval

**User command**: "Create ProjectCard component"

**Flow**:
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
    ↓
UI Architect: Implement with recommendations
    ↓
Orchestrator: Add approval checkpoint
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
Orchestrator: Record approval
    ↓
Present to user with Checker badge:
"✅ Checker Agent Validation: APPROVED (96% confidence)"
```

---

### Example 4: API Endpoint Creation with Cross-Agent Consultation

**User command**: "Add DELETE /projects/{id} endpoint"

**Flow**:
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
API Architect: Implements with recommendations
API Architect: Identifies DB schema change needed
API Architect: CONSULT DB Architect for compatibility
    ↓
DB Architect: {
  "compatibility_status": "COMPATIBLE",
  "migration_script": "ALTER TABLE projects ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;"
}
    ↓
Orchestrator: Add approval checkpoint
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
Orchestrator: Record approval
    ↓
Present to user with Checker badge:
"⚠️ Checker Agent Validation: PASS_WITH_WARNINGS (94% confidence)"
```

---

### Example 5: Manual Multi-Agent Review

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
# Merged report saved to .claude/reports/api-review-2025-10-11.json
```

---

## Configuration & Setup

### Required Setup

1. **Verify Directory Structure**:
```bash
cd /Users/rohitiyer/datagrub/promptforge
ls -la .claude/context/
ls -la .claude/hooks/
ls -la .claude/specs/
ls -la .claude/agents/
```

2. **Install Validation Tools**:
```bash
# Shell script validation
brew install shellcheck

# Python validation
pip install pylint black

# JavaScript/TypeScript validation
npm install -g eslint typescript

# JSON processing
brew install jq
```

3. **Verify Hook Configuration**:
```bash
# Check hook is executable
ls -la .claude/hooks/post-tool-use.sh
# Should show: -rwxr-xr-x

# Make executable if needed
chmod +x .claude/hooks/post-tool-use.sh
```

---

### Context File Initialization

All context files are pre-initialized in `.claude/context/agents/`. To verify:

```bash
ls -la .claude/context/agents/
# Should see: api_architect.json, apiqa.json, checker.json, db_architect.json,
#             doc_tracker.json, ui_architect.json, uiqa.json, ux_specialist.json, validator.json
```

To reinitialize a context file:
```bash
cd .claude/context/agents
echo '{"agent_name":"validator","initialized":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","total_sessions":0,"validations":[]}' > validator.json
```

---

### Validation

**Validate Context Files**:
```bash
cd .claude/scripts
./validate-context.sh ../context/agents/checker.json
```

**Test Workflow Manager**:
```bash
cd .claude/scripts
./workflow-manager.sh add task-test-001 UI_Architect_Agent
./workflow-manager.sh check task-test-001
./workflow-manager.sh approve task-test-001 APPROVED
./workflow-manager.sh history 5
```

---

## Troubleshooting

### Hook Not Triggering

```bash
# Check hook is executable
ls -la .claude/hooks/post-tool-use.sh
# Should show: -rwxr-xr-x

# Make executable if needed
chmod +x .claude/hooks/post-tool-use.sh
```

### Context File Issues

```bash
# Verify context files exist
ls -la .claude/context/agents/

# Validate context file schema
cd .claude/scripts
./validate-context.sh ../context/agents/validator.json
```

### Validation Not Running

Check that:
1. File matches supported patterns (scripts/, README.md, etc.)
2. Hook script is executable
3. Required tools installed (shellcheck, jq, etc.)

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

## Agent Status Summary

| Agent | Status | Trigger | Cross-Agent Consultations | Location | Priority |
|-------|--------|---------|---------------------------|----------|----------|
| **Script Validator** | ✅ Active | Auto | None | `.claude/agents/04_validators/` | - |
| **README Validator** | ✅ Active | Auto | None | `.claude/agents/04_validators/` | - |
| **API Architect** | ✅ Active | **Auto** ⭐ | → UI, DB, API QA | `.claude/agents/01_architecture/` | - |
| **DB Architect** | ✅ Active | **Auto** ⭐ | → API (MANDATORY) | `.claude/agents/01_architecture/` | - |
| **UI Architect** | ✅ Active | **Auto** ⭐ | → UX (MANDATORY), API | `.claude/agents/01_architecture/` | After UX consult |
| **UX Specialist** | ✅ Complete | Manual | None | `.claude/agents/01_architecture/` | **First for UX** |
| **API QA** | ✅ Complete | Manual | None | `.claude/agents/02_quality/` | - |
| **UI QA** | ✅ Complete | Manual | None | `.claude/agents/02_quality/` | After UX |
| **Doc Context Tracker** | ✅ Complete | Manual | None | `.claude/agents/03_operations/` | - |
| **Auth Token Generator** | ✅ Complete | Manual | None | `.claude/agents/03_operations/` | - |
| **Checker Agent** | ✅ Complete | Auto (after architects) | None | `.claude/agents/02_quality/` | **Final Gate** |

**Legend**:
- ✅ **Active** = Configured with hooks, runs automatically
- ✅ **Complete** = Template and context available, invoke manually
- ⭐ **Auto** = Automatic architectural review on file changes
- **→** = Auto-invokes consulted agents when cross-tier impacts detected
- **(MANDATORY)** = Consultation ALWAYS required for this agent type
- **First for UX** = Consult first for all design/style/UX decisions
- **Final Gate** = Reviews all outputs before user publication

---

## Related Documentation

- **Agent Registry**: `.claude/agents/README.md` (8KB agent documentation)
- **Spec Index**: `.claude/specs/README.md` (5KB spec documentation with dependency matrix)
- **Context Documentation**: `.claude/context/README.md` (7KB context file guide)
- **Migration Summary**: `.claude/REORGANIZATION_COMPLETE.md` (Complete reorganization history)
- **Approval Checklist**: `.claude/templates/approval-checklist.md` (Workflow guidance)
- **Auto-Checker Strategy**: `.claude/CHECKER_AUTO_INVOCATION_STRATEGY.md` (Automatic Checker invocation)
- **Cross-Agent Orchestration**: `.claude/CROSS_AGENT_ORCHESTRATION_v2.2.md` (Cross-tier consultation workflows)

---

**Maintainer**: PromptForge Team
**Repository**: `/Users/rohitiyer/datagrub/promptforge`
**Architecture**: Fully Self-Contained (Option 1)
**Completion**: 100% ✅ (Full Cross-Agent Orchestration v2.2.0)
**Cross-Agent Features**:
- ✅ Auto-Checker Invocation (v2.0.1)
- ✅ Auto-API-Architect Review (v2.1.0)
- ✅ Auto-DB-Architect Review + API Consultation (v2.2.0)
- ✅ Auto-UI-Architect Review + UX Consultation (v2.2.0)
- ✅ Pydantic Schema Cross-Tier Detection (v2.2.0)
