# PromptForge Claude Code Subagents

**Version**: 2.0.0
**Last Updated**: 2025-10-11
**Total Agents**: 11 (8 shared, 3 project-specific)

---

## Directory Structure

```
agents/
├── 00_meta/                  # Agent templates and schemas
├── 01_architecture/          # System design and implementation agents
├── 02_quality/               # Quality assurance and testing agents
├── 03_operations/            # Documentation and operations agents
└── 04_validators/            # Project-specific validation agents
```

---

## Agent Registry

### 01_architecture: Architecture Agents

| Agent | File | Size | Status | Priority |
|-------|------|------|--------|----------|
| **UI Architect** | `UI_Architect_Agent.md` | 7.8 KB | ✅ Complete | After UX |
| **API Architect** | `API_Architect_Agent.md` | 6.6 KB | ✅ Complete | Standard |
| **DB Architect** | `DB_Architect_Agent.md` | 6.6 KB | ✅ Complete | Standard |
| **UX Specialist** | `UX_Specialist_Agent.md` | 5.2 KB | ✅ Complete | **FIRST** |

**Trigger**: Manual invocation
**Context**: `../../context/agents/{agent_name}_context.json`

---

### 02_quality: Quality Assurance Agents

| Agent | File | Size | Status | Priority |
|-------|------|------|--------|----------|
| **Checker** | `Checker_Agent.md` | 24.4 KB | ✅ Complete | **LAST (Final Gate)** |
| **API QA** | `API_QA_Agent.md` | 8.2 KB | ⚠️ Partial | Standard |
| **UI QA** | `UI_QA_Agent.md` | 626 bytes | ⚠️ Incomplete | Standard |

**Trigger**: Manual invocation (Checker mandatory after architect work)
**Context**: `../../context/agents/{agent_name}_context.json`

---

### 03_operations: Operations Agents

| Agent | File | Size | Status | Priority |
|-------|------|------|--------|----------|
| **Doc Context Tracker** | `Doc_Context_Tracker_Agent.md` | 681 bytes | ⚠️ Incomplete | Standard |

**Trigger**: Manual invocation
**Context**: `../../context/agents/doc_tracker_context.json`

---

### 04_validators: Validation Agents (Project-Specific)

| Agent | File | Status | Priority |
|-------|------|--------|----------|
| **Script Validator** | `script-validator.md` | ✅ Complete | Auto |
| **README Validator** | `readme-validator.md` | ✅ Complete | Auto |

**Trigger**: Auto on Write/Edit to matching file patterns
**Context**: `../../context/agents/validator_context.json`

---

## Agent Dependency Matrix

### Build Specification Dependencies

| Agent | Primary Specs | Secondary Specs |
|-------|---------------|-----------------|
| **UI Architect** | `specs/01_phase1_foundation/Phase1_CoreUI.md`<br>`specs/02_phase2_core_features/ui/Phase2_UI_Framework.md` | `specs/02_phase2_core_features/insights/Phase2_Insights_History.md`<br>`specs/02_phase2_core_features/evaluation/Phase2_Evaluation_Dashboard.md` |
| **API Architect** | `specs/02_phase2_core_features/apis/Phase2_APIs.md`<br>`specs/02_phase2_core_features/apis/Phase2_API_SecurityRequirements.md` | `specs/02_phase2_core_features/apis/Phase2_API_PerformanceRequirements.md`<br>`specs/02_phase2_core_features/insights/Phase2_Summarization_Insights_API_DTA.md` |
| **DB Architect** | `specs/02_phase2_core_features/apis/Phase2_APIs.md` | All domain specs for schema design |
| **UX Specialist** | `specs/02_phase2_core_features/ui/Phase2_UI_Framework.md` | All feature specs for UX requirements |
| **Checker** | **ALL SPECS** | - |
| **API QA** | `specs/02_phase2_core_features/apis/Phase2_APIs.md` | All API-related specs |
| **UI QA** | `specs/01_phase1_foundation/Phase1_CoreUI.md`<br>`specs/02_phase2_core_features/ui/Phase2_UI_Framework.md` | All UI-related specs |
| **Script Validator** | All relevant specs based on file path | - |
| **README Validator** | All relevant specs based on file path | - |

---

## Agent Workflow Orchestration

### Priority Rules

1. **UX Specialist FIRST**: Consult for all UX/design/style decisions before implementation
2. **Architect Implementation**: UI/API/DB architects implement features
3. **Checker LAST**: MANDATORY approval after all architect implementations before user presentation
4. **QA Validation**: Run tests after implementation (can run in parallel with Checker)

### Mandatory Checker Approval Workflow

**CRITICAL**: After any architect agent completes work, the following workflow MUST be executed:

```
Phase 1: Add Approval Checkpoint
  → ./claude/scripts/workflow-manager.sh add <task_uuid> <architect_agent>

Phase 2: Invoke Checker Agent
  → "Invoke Checker Agent to perform Post_Check validation"

Phase 3: Wait for Approval Status
  → Checker returns: APPROVED, PASS_WITH_WARNINGS, or BLOCKED

Phase 4: Handle Status
  → If BLOCKED: Fix issues and re-submit
  → If APPROVED/PASS_WITH_WARNINGS: Proceed to Phase 5

Phase 5: Record Approval
  → ./claude/scripts/workflow-manager.sh approve <task_uuid> <status>

Phase 6: Present to User
  → Include Checker badge in response
```

**Reference**: `../templates/approval-checklist.md` for complete workflow

---

## Cross-Agent Compatibility Rules

### UI Architect → API Architect Consultation

**Trigger**: When UI Architect makes API-related changes (endpoints, payloads)

**Process**:
1. UI Architect identifies API change needed
2. Invoke API Architect for compatibility check
3. API Architect evaluates breaking changes
4. API Architect recommends approach (compatible, versioning, migration)
5. User approves selected option
6. UI Architect implements with API Architect guidance

---

### API Architect → UI Architect & DB Architect Consultation

**Trigger**: When API Architect makes API changes (routes, schemas, responses)

**Process**:
1. API Architect proposes change
2. **PARALLEL**: Invoke UI Architect AND DB Architect
3. Both evaluate compatibility
4. API Architect provides options if incompatible
5. User approves approach
6. Coordinated implementation

---

### DB Architect → API Architect Consultation

**Trigger**: When DB Architect makes database changes (schema, indexes, constraints)

**Process**:
1. DB Architect identifies change needed
2. Invoke API Architect for compatibility check
3. API Architect evaluates ORM and query impact
4. API Architect recommends migration strategy
5. User approves approach
6. DB Architect implements with API guidance

---

## Agent Invocation Examples

### Architecture Agents

```
"Invoke UI Architect to review ui-tier/mfe-projects against Phase 1 CoreUI specs"
"Invoke UI Architect to implement routing following Phase2_UI_Framework standards"

"Invoke API Architect to implement evaluation routes per Phase 2 Evaluation Framework"
"Invoke API Architect to review Deep Insights API implementation"

"Invoke DB Architect to review data-tier schema for Phase 2 requirements"

"Invoke UX Specialist to design search results card component for evaluations page"
"Have UX Specialist audit accessibility of project creation form"
```

### Quality Agents

```
"Invoke Checker Agent to review API Architect's evaluation endpoints implementation"
"Run Pre_Check for new project tagging feature"
"Have Checker validate all changes before deployment"

"Run API QA tests on all api-tier routes"

"Run UI QA Playwright tests for ui-tier/mfe-evaluations"
```

### Operations Agents

```
"Invoke Doc Context Tracker to sync agent templates with latest changes"
```

---

## Agent Communication Protocol

### Input Envelope (JSON)

```json
{
  "task_type": "validate|review|implement|test",
  "file_path": "/absolute/path/to/file",
  "specs_dir": "../specs",
  "relevant_specs": ["02_phase2_core_features/apis/Phase2_APIs.md"],
  "context_file": "../context/agents/api_architect.json",
  "task_uuid": "uuid-v4",
  "resume": false
}
```

### Output Envelope (JSON)

```json
{
  "agent": "api_architect",
  "status": "ok|warn|error|blocked",
  "summary": "Brief summary",
  "findings": [...],
  "spec_compliance": {...},
  "next_actions": [...],
  "context_update": {...}
}
```

---

## File Pattern → Agent Routing

| Pattern | Agent(s) | Auto-Trigger |
|---------|----------|--------------|
| `scripts/**/*.{sh,py,js,ts}` | Script Validator | ✅ Yes |
| `**/{README,SETUP,GUIDE}*.md` | README Validator | ✅ Yes |
| `ui-tier/**/*.{ts,tsx}` | UI Architect, UI QA | ❌ Manual |
| `api-tier/**/*.py` | API Architect, API QA | ❌ Manual |
| `data-tier/**/*.sql` | DB Architect | ❌ Manual |
| `docs/**/*.md` | Doc Context Tracker | ❌ Manual |

---

## Agent Status Summary

| Agent | Status | Completion | Priority | Next Action |
|-------|--------|------------|----------|-------------|
| **UX Specialist** | ✅ Complete | 100% | **FIRST** | Ready for use |
| **UI Architect** | ✅ Complete | 100% | After UX | Ready for use |
| **API Architect** | ✅ Complete | 100% | Standard | Ready for use |
| **DB Architect** | ✅ Complete | 100% | Standard | Ready for use |
| **Checker** | ✅ Complete | 100% | **LAST** | Ready for use |
| **API QA** | ⚠️ Partial | 70% | Standard | Add FastAPI test examples |
| **UI QA** | ⚠️ Incomplete | 10% | Standard | Complete template |
| **Doc Context Tracker** | ⚠️ Incomplete | 15% | Standard | Complete template |
| **Script Validator** | ✅ Complete | 100% | Auto | Ready for use |
| **README Validator** | ✅ Complete | 100% | Auto | Ready for use |

---

## Adding New Agents

### Step 1: Choose Category

- **01_architecture**: System design and implementation agents
- **02_quality**: Testing and quality assurance agents
- **03_operations**: Documentation and operational support agents
- **04_validators**: Project-specific validation agents

### Step 2: Use Template

See `00_meta/agent_template.md` for standard agent structure.

### Step 3: Create Context File

Add to `../context/agents/{agent_name}.json` with schema:

```json
{
  "agent_name": "new_agent",
  "initialized": "2025-10-11T00:00:00Z",
  "total_sessions": 0,
  "last_updated": "2025-10-11T00:00:00Z"
}
```

### Step 4: Update This README

Add entry to appropriate category table and dependency matrix.

### Step 5: Update Routing Rules

If auto-trigger needed, update `../hooks/post-tool-use.sh`.

---

## Version History

### 2.0.0 (2025-10-11)
- Reorganized into role-based structure
- Moved to self-contained project architecture
- Added comprehensive README with agent registry
- Created dependency matrix
- Documented workflow orchestration

### 1.0.0 (2025-10-05)
- Initial flat directory structure
- Core agents implemented

---

## Contributing

When adding or modifying agents:

1. **Follow template** in `00_meta/agent_template.md`
2. **Add version header** to agent file
3. **Update this README** with new entry
4. **Create context file** in `../context/agents/`
5. **Test agent invocation** before committing
6. **Update dependency matrix** if new spec dependencies

---

**Maintained by**: PromptForge Team
**Location**: `/Users/rohitiyer/datagrub/promptforge/.claude/agents/`
