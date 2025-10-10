# Claude Multi-Project Orchestrator

This file serves as the **master entrypoint** for Claude when launched from `/Users/rohitiyer/datagrub`. It provides visibility into all configured subagents across projects and their responsibilities.

---

## Project Structure

```
/Users/rohitiyer/datagrub/
├── CLAUDE.md                          # This file - master orchestrator
├── Claude_Init_Script.md              # Original orchestration architecture
├── Claude_Subagent_Prompts/           # Shared subagent templates
│   ├── UI_Architect_Agent.md
│   ├── API_Architect_Agent.md
│   ├── DB_Architect_Agent.md
│   ├── API_QA_Agent.md
│   ├── UI_QA_Agent.md
│   └── Doc_Context_Tracker_Agent.md
├── PromptForge_Build_Specs/           # Product specifications
│   ├── Phase1_CoreUI.md
│   ├── Phase2_APIs.md
│   ├── Phase2_API_SecurityRequirements.md
│   ├── Phase2_API_PerformanceRequirements.md
│   ├── Phase2_Evaluation_Framework.md
│   ├── Phase2_Summarization_Insights_API_DTA.md
│   ├── Phase2_Insights_History.md
│   ├── Phase2_Trace_Dashboard.md
│   ├── Phase2_UI_Framework.md
│   ├── Phase3_Privacy_Framework.md
│   └── Phase3_SaaSRefinement.md
└── promptforge/                       # Active project with subagent system
    ├── .claude/                       # Claude Code configuration
    │   ├── CLAUDE_ORCHESTRATOR.md     # Project-level orchestrator
    │   ├── README.md                  # Quick reference
    │   ├── hooks/
    │   │   └── post-tool-use.sh       # Auto-validation hook
    │   ├── agents/
    │   │   ├── script-validator.md    # Script validation
    │   │   └── readme-validator.md    # Documentation validation
    │   └── context/                   # Persistent agent memory
    │       ├── validator_context.json
    │       ├── ui_architect_context.json
    │       ├── api_architect_context.json
    │       ├── db_architect_context.json
    │       ├── apiqa_context.json
    │       ├── uiqa_context.json
    │       └── doc_tracker_context.json
    ├── ui-tier/
    ├── api-tier/
    ├── data-tier/
    └── scripts/
```

---

## Subagent Registry (All Projects)

**Total Agents**: 10 (2 auto-triggered, 8 manual invocation)

### 🔍 Validation Agents (PromptForge - Auto-triggered)

#### Script Validator
**Location**: `promptforge/.claude/agents/script-validator.md`
**Status**: ✅ Active
**Trigger**: Auto on Write/Edit to `promptforge/scripts/**/*.{sh,py,js,ts}`
**Context**: `promptforge/.claude/context/validator_context.json`

**Responsibilities**:
- Syntax validation (shellcheck, pylint, eslint, tsc)
- Security checks (no hardcoded credentials)
- Build spec compliance (refs: PromptForge_Build_Specs/)
- Error handling verification
- Dependency and path validation
- Auto-fix safe issues

**Invocation** (if in /datagrub):
```bash
cd promptforge
# Then edit any script - validation runs automatically
```

---

#### README Validator
**Location**: `promptforge/.claude/agents/readme-validator.md`
**Status**: ✅ Active
**Trigger**: Auto on Write/Edit to `promptforge/**/{README,SETUP,GUIDE}*.md`
**Context**: `promptforge/.claude/context/validator_context.json`

**Responsibilities**:
- Command accuracy (validate all code examples)
- File path verification (ensure paths exist)
- Build spec alignment
- Markdown quality (formatting, links, code blocks)
- Auto-fix formatting issues

**Invocation** (if in /datagrub):
```bash
cd promptforge
# Then edit any README - validation runs automatically
```

---

### 🏗️ Architecture Agents (Shared Templates)

#### UI Architect
**Template**: `Claude_Subagent_Prompts/UI_Architect_Agent.md`
**Status**: ⚙️ Template available, context in promptforge
**Context**: `promptforge/.claude/context/ui_architect_context.json`
**Build Specs**:
- `PromptForge_Build_Specs/Phase1_CoreUI.md` (Component architecture)
- `PromptForge_Build_Specs/Phase2_UI_Framework.md` (Routing, state, design system)
- `PromptForge_Build_Specs/Phase2_Insights_History.md` (Deep Insights UI implementation) ⭐

**Responsibilities**:
- Create/maintain React UI components (micro-frontends)
- Ensure modular MFE structure
- Integrate frontend with backend APIs
- Enforce WCAG AAA accessibility and UX best practices
- Follow UI Framework standards (routing, state persistence, design system)
- Create CI pipeline (`ci-ui.yml`)
- Maintain consistent UI design patterns

**Commands**:
- `Build_UI_Component` - Build new component
- `Link_Backend_API` - Connect to API route
- `Run_UI_Tests` - Execute regression/integration tests

**Invocation**:
```
"Invoke UI Architect to review promptforge/ui-tier/mfe-projects against Phase 1 CoreUI specs"
"Invoke UI Architect to implement routing following Phase2_UI_Framework standards"
"Invoke UI Architect to review Deep Insights UI components against Phase2_Insights_History.md"
```

---

#### API Architect
**Template**: `Claude_Subagent_Prompts/API_Architect_Agent.md`
**Status**: ⚙️ Template available, context in promptforge
**Context**: `promptforge/.claude/context/api_architect_context.json`
**Build Specs**:
- `PromptForge_Build_Specs/Phase2_APIs.md` (General API architecture)
- `PromptForge_Build_Specs/Phase2_Summarization_Insights_API_DTA.md` (Deep Insights API) ⭐

**Responsibilities**:
- Define routes (Projects, Prompts, Evaluations, Traces)
- Manage API authentication, versioning, schema validation
- Implement evaluation abstraction layer (Ragas, DeepEval, MLflow, Deepchecks, Arize Phoenix)
- Maintain CI pipeline (`ci-api.yml`)
- Log all API interactions

**Commands**:
- `Create_API_Route` - Define new API route
- `Test_API` - Run FastAPI test cases
- `Validate_Security` - Security compliance checks

**Invocation**:
```
"Invoke API Architect to implement evaluation routes per Phase 2 Evaluation Framework"
"Invoke API Architect to review Deep Insights API implementation against Phase2_Summarization_Insights_API_DTA.md"
```

---

#### DB Architect
**Template**: `Claude_Subagent_Prompts/DB_Architect_Agent.md`
**Status**: ⚙️ Template available, context in promptforge
**Context**: `promptforge/.claude/context/db_architect_context.json`
**Build Specs**: `PromptForge_Build_Specs/Phase2_APIs.md`

**Responsibilities**:
- Maintain normalized schemas (PostgreSQL + Redis)
- Design tables for trace logging and metrics
- Implement seed scripts (golden, edge, adversarial datasets)
- Create CI pipeline (`ci-db.yml`)
- Optimize for high concurrency and data integrity

**Commands**:
- `Create_Table` - Define/update schema
- `Seed_Data` - Load seed data
- `Run_Migration_Test` - Validate migrations

**Invocation**:
```
"Invoke DB Architect to review promptforge/data-tier schema for Phase 2 requirements"
```

---

### 🎨 Design Agent (Shared Template)

#### UX Specialist
**Template**: `Claude_Subagent_Prompts/UX_Specialist_Agent.md`
**Status**: ⚙️ Template available, context in promptforge
**Context**: `promptforge/.claude/context/ux_specialist_context.json`
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

**Orchestration Priority**: **Consult UX Specialist FIRST** for all UX/design/style decisions to ensure consistent look and feel.

**Invocation**:
```
"Invoke UX Specialist to design search results card component for evaluations page"
"Have UX Specialist audit accessibility of project creation form"
"UX Specialist: review Button component for design consistency"
```

---

### 🧪 QA Agents (Shared Templates)

#### API QA
**Template**: `Claude_Subagent_Prompts/API_QA_Agent.md`
**Status**: ⚙️ Template available, context in promptforge
**Context**: `promptforge/.claude/context/apiqa_context.json`
**Build Specs**:
- `PromptForge_Build_Specs/Phase2_APIs.md` (General API testing)
- `PromptForge_Build_Specs/Phase2_Summarization_Insights_API_DTA.md` (Deep Insights API) ⭐

**Responsibilities**:
- Run unit and integration tests for backend routes
- Validate OpenAPI specifications
- Ensure consistent status codes and payload schemas
- Log results and coverage reports

**Commands**:
- `Run_API_Tests` - Execute test suites
- `Compare_Spec` - Validate against design specs
- `Log_Results` - Record test outputs

**Invocation**:
```
"Run API QA tests on all promptforge/api-tier routes"
```

---

#### UI QA
**Template**: `Claude_Subagent_Prompts/UI_QA_Agent.md`
**Status**: ⚙️ Template available, context in promptforge
**Context**: `promptforge/.claude/context/uiqa_context.json`
**Build Specs**:
- `PromptForge_Build_Specs/Phase1_CoreUI.md` (General UI testing)
- `PromptForge_Build_Specs/Phase2_Insights_History.md` (Deep Insights UI) ⭐

**Responsibilities**:
- Execute Playwright tests for components/flows
- Validate UI ↔ API integration
- Run regression suite for merge requests
- Generate test and coverage reports

**Commands**:
- `Run_E2E_Tests` - Execute Playwright E2E tests
- `Validate_Integration` - Verify UI ↔ API communication
- `Generate_Report` - Create test summary

**Invocation**:
```
"Run UI QA Playwright tests for promptforge/ui-tier/mfe-evaluations"
```

---

### 📚 Documentation Agent (Shared Template)

#### Doc Context Tracker
**Template**: `Claude_Subagent_Prompts/Doc_Context_Tracker_Agent.md`
**Status**: ⚙️ Template available, context in promptforge
**Context**: `promptforge/.claude/context/doc_tracker_context.json`

**Responsibilities**:
- Track and update prompt templates
- Monitor new documents/scripts for compliance
- Sync prompt documentation with other subagents
- Update templates to reflect design/test changes

**Commands**:
- `Update_Prompt_Template` - Apply template updates
- `Sync_Context` - Merge changes from other agents
- `Audit_Document` - Review/validate documentation

**Invocation**:
```
"Invoke Doc Context Tracker to sync Claude_Subagent_Prompts with latest changes"
```

---

### 🔒 Quality Assurance Agent (Shared Template)

#### Checker Agent
**Template**: `Claude_Subagent_Prompts/Checker_Agent.md`
**Status**: ⚙️ Template available, context in promptforge
**Context**: `promptforge/.claude/context/checker_context.json`
**Build Specs**: All phases (reviews against all specifications)

**Responsibilities**:
- Final review gate for all subagent outputs (UI, API, DB, UX, QA)
- Ensure deliverables meet project specifications and quality expectations
- Prevent regressions by tracking error patterns and historical issues
- Cross-agent consistency checks (UI ↔ API ↔ DB alignment)
- Continuous learning from failures to improve guardrails
- Approve/flag/reject updates before user-facing publication

**Quality Gates**:
1. **Specification Alignment** - Implementation matches build specs (BLOCK if not met)
2. **Regression Prevention** - All regression tests pass (BLOCK if failed)
3. **Error Pattern Avoidance** - No repeated known issues (WARNING/BLOCK if critical)
4. **Test Coverage** - Unit >80%, integration critical paths (BLOCK if below threshold)
5. **Documentation** - Code comments, API docs, guides updated (WARNING if incomplete)

**Error Pattern Categories**:
- **API Errors**: Missing try-catch, incorrect status codes, missing validation
- **UI Errors**: Missing loading states, accessibility violations, memory leaks
- **DB Errors**: Missing indexes, N+1 queries, missing rollback scripts
- **Integration Errors**: Type mismatches, breaking API contracts, schema inconsistencies

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

## Quick Reference by Working Directory

### If Working in `/Users/rohitiyer/datagrub/`

**To use validation agents**:
```bash
cd promptforge
# Edit scripts or READMEs - validation runs automatically
```

**To invoke architecture/QA agents**:
```
"Invoke [Agent Name] to [task] in promptforge/[directory]"
```

**To view all subagent configs**:
```
"Show me the subagent registry"
"List all configured subagents and their status"
```

### If Working in `/Users/rohitiyer/datagrub/promptforge/`

**Validation agents**: Auto-trigger on file edits
**Architecture/QA agents**: Manual invocation
**See**: `.claude/README.md` for detailed usage

---

## Initialization Commands

### From /datagrub directory:

**List all subagents**:
```
"List all configured subagents across all projects"
```

**Check subagent status**:
```
"Check the status of all subagent context files"
```

**Invoke specific agent**:
```
"Invoke UI Architect to review promptforge/ui-tier/mfe-projects"
"Run Script Validator on promptforge/scripts/deploy.sh"
"Have API Architect implement evaluation routes in promptforge/api-tier"
```

**Resume checkpoint**:
```
"Check resume checkpoint and continue any incomplete tasks"
```

### From /datagrub/promptforge directory:

**See**: `VALIDATION_SYSTEM_SETUP.md` for complete guide
**See**: `.claude/README.md` for quick reference
**See**: `.claude/CLAUDE_ORCHESTRATOR.md` for technical details

---

## Context File Locations

All persistent agent memory stored in:
```
promptforge/.claude/context/
├── validator_context.json          # Script & README validation history
├── ux_specialist_context.json      # Design system, UX patterns, accessibility
├── ui_architect_context.json       # UI architecture decisions
├── api_architect_context.json      # API architecture decisions
├── db_architect_context.json       # Database schema evolution
├── apiqa_context.json              # API QA test results
├── uiqa_context.json               # UI QA test results
├── doc_tracker_context.json        # Documentation tracking
├── checker_context.json            # Quality checks, error patterns, regressions
└── resume_checkpoint_context.json  # Crash recovery state
```

---

## Build Spec References

All subagents reference specifications from:
```
PromptForge_Build_Specs/
├── Phase1_CoreUI.md                       # UI architecture
├── Phase2_APIs.md                         # API architecture
├── Phase2_API_SecurityRequirements.md     # Security requirements
├── Phase2_API_PerformanceRequirements.md  # Performance requirements
├── Phase2_Evaluation_Framework.md         # Evaluation system architecture
├── Phase2_Evaluation_Playground.md        # Evaluation Playground dashboard ⭐ NEW
├── Phase2_Summarization_Insights_API_DTA.md  # Deep Insights API specification
├── Phase2_Insights_History.md             # Deep Insights implementation guide
├── Phase2_Trace_Dashboard.md              # Trace visualization
├── Phase2_UI_Framework.md                 # UI Framework standards
├── Phase3_Privacy_Framework.md            # Privacy & compliance
└── Phase3_SaaSRefinement.md              # SaaS features
```

Subagents automatically load relevant specs based on:
- File paths (ui-tier → Phase1 + Phase2_UI_Framework, api-tier → Phase2, etc.)
- Task context (evaluation → Evaluation Framework, insights → Deep Insights specs, routing → UI Framework)
- Feature names (mfe-insights → Phase2_Summarization_Insights_API_DTA.md + Phase2_Insights_History.md)
- Explicit references in prompts

---

## Agent Communication Protocol

### Input Envelope (JSON)
```json
{
  "task_type": "validate|review|implement|test",
  "file_path": "/absolute/path/to/file",
  "build_specs_dir": "/Users/rohitiyer/datagrub/PromptForge_Build_Specs",
  "relevant_specs": ["Phase2_APIs.md"],
  "context_file": "promptforge/.claude/context/[agent]_context.json",
  "task_uuid": "uuid-v4",
  "resume": false
}
```

### Output Envelope (JSON)
```json
{
  "agent": "agent-name",
  "status": "ok|warn|error|blocked",
  "summary": "Brief summary",
  "findings": [...],
  "spec_compliance": {...},
  "next_actions": [...],
  "context_update": {...}
}
```

---

## Routing Rules

### File Pattern → Agent Mapping

| Pattern | Agent(s) | Auto-Trigger |
|---------|----------|--------------|
| `promptforge/scripts/**/*.{sh,py,js,ts}` | Script Validator | ✅ Yes |
| `promptforge/**/{README,SETUP,GUIDE}*.md` | README Validator | ✅ Yes |
| `promptforge/ui-tier/**/*.{ts,tsx}` | UI Architect, UI QA | ❌ Manual |
| `promptforge/api-tier/**/*.py` | API Architect, API QA | ❌ Manual |
| `promptforge/data-tier/**/*.sql` | DB Architect | ❌ Manual |
| `promptforge/docs/**/*.md` | Doc Context Tracker | ❌ Manual |

---

## Status Summary

| Agent | Status | Trigger | Location | Priority |
|-------|--------|---------|----------|----------|
| **Script Validator** | ✅ Active | Auto | `promptforge/.claude/agents/` | - |
| **README Validator** | ✅ Active | Auto | `promptforge/.claude/agents/` | - |
| **UX Specialist** | ⚙️ Ready | Manual | `Claude_Subagent_Prompts/` | **First for UX** |
| **UI Architect** | ⚙️ Ready | Manual | `Claude_Subagent_Prompts/` | After UX |
| **API Architect** | ⚙️ Ready | Manual | `Claude_Subagent_Prompts/` | - |
| **DB Architect** | ⚙️ Ready | Manual | `Claude_Subagent_Prompts/` | - |
| **API QA** | ⚙️ Ready | Manual | `Claude_Subagent_Prompts/` | - |
| **UI QA** | ⚙️ Ready | Manual | `Claude_Subagent_Prompts/` | After UX |
| **Doc Context Tracker** | ⚙️ Ready | Manual | `Claude_Subagent_Prompts/` | - |
| **Checker Agent** | ⚙️ Ready | Manual | `Claude_Subagent_Prompts/` | **Final Gate** |

**Legend**:
- ✅ **Active** = Configured with hooks, runs automatically
- ⚙️ **Ready** = Template and context available, invoke manually
- **First for UX** = Consult first for all design/style/UX decisions
- **Final Gate** = Reviews all outputs before user publication

---

## Dependencies

### Required Tools (for validation agents)
```bash
# JSON processing
brew install jq

# Script validation
brew install shellcheck          # Shell scripts
pip install pylint               # Python
npm install -g eslint typescript # JavaScript/TypeScript
```

### Optional Tools
```bash
pip install black                # Python formatting
npm install -g prettier          # JS/TS formatting
```

---

## Quick Start

### 1. View Subagent Configuration
```
"Show me all configured subagents"
```

### 2. Check Context Status
```bash
ls -la promptforge/.claude/context/
cat promptforge/.claude/context/validator_context.json
```

### 3. Invoke an Agent
```
"Invoke Script Validator to check promptforge/scripts/deploy.sh"
"Have UI Architect review promptforge/ui-tier/mfe-projects"
"Run API QA tests on promptforge/api-tier/routes"
```

### 4. Automatic Validation (when in promptforge/)
```bash
cd promptforge
# Edit any script or README - validation runs automatically
vim scripts/test.sh
vim README.md
```

---

## Documentation

- **Master Orchestrator**: This file (`/datagrub/CLAUDE.md`)
- **Original Architecture**: `Claude_Init_Script.md`
- **PromptForge Orchestrator**: `promptforge/.claude/CLAUDE_ORCHESTRATOR.md`
- **PromptForge Quick Guide**: `promptforge/.claude/README.md`
- **Setup Guide**: `promptforge/VALIDATION_SYSTEM_SETUP.md`
- **Subagent Templates**: `Claude_Subagent_Prompts/*.md`
- **Build Specs**: `PromptForge_Build_Specs/*.md`

---

**Version**: 2.0
**Last Updated**: 2025-10-05
**Scope**: Multi-project orchestrator for /datagrub workspace
**Active Projects**: PromptForge (with full subagent system)
