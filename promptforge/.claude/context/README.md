# PromptForge Context Files

**Version**: 2.0.0
**Last Updated**: 2025-10-11
**Purpose**: Persistent agent memory and workflow state management

---

## Directory Structure

```
context/
├── README.md                                # This file
├── agents/                                  # Agent-specific persistent memory
│   ├── api_architect.json
│   ├── apiqa.json
│   ├── checker.json
│   ├── db_architect.json
│   ├── doc_tracker.json
│   ├── ui_architect.json
│   ├── uiqa.json
│   ├── ux_specialist.json
│   └── validator.json
├── workflow/                                # Workflow coordination state
│   ├── workflow_state.json                 # Approval workflow tracking
│   └── resume_checkpoint.json              # Crash recovery state
└── schema/                                  # JSON schemas for validation
    ├── agent_context.schema.json           # Standard agent context schema
    └── workflow_state.schema.json          # Workflow state schema
```

---

## Agent Context Files

### Purpose
Store persistent memory for each subagent including:
- Session history
- Learned patterns
- Error tracking
- Performance metrics
- Task history

### File Naming Convention
`agents/{agent_name}.json`

### Standard Schema
All agent context files follow this base schema:

```json
{
  "agent_name": "string",
  "initialized": "ISO-8601 datetime",
  "total_sessions": "integer",
  "last_updated": "ISO-8601 datetime",
  "agent_specific_data": "varies by agent"
}
```

### Agent Context Inventory

| Agent | File | Size | Last Updated | Sessions |
|-------|------|------|--------------|----------|
| **API Architect** | `api_architect.json` | 104 B | 2025-10-05 | 0 |
| **API QA** | `apiqa.json` | 96 B | 2025-10-05 | 0 |
| **Checker** | `checker.json` | 17.4 KB | 2025-10-11 | 5 |
| **DB Architect** | `db_architect.json` | 103 B | 2025-10-05 | 0 |
| **Doc Tracker** | `doc_tracker.json` | 19.3 KB | 2025-10-11 | 3 |
| **UI Architect** | `ui_architect.json` | 103 B | 2025-10-05 | 0 |
| **UI QA** | `uiqa.json` | 95 B | 2025-10-05 | 0 |
| **UX Specialist** | `ux_specialist.json` | 13.8 KB | 2025-10-08 | 2 |
| **Validator** | `validator.json` | 100 B | 2025-10-05 | 0 |

---

## Workflow Context Files

### Purpose
Coordinate multi-agent workflows and track approval states.

### workflow_state.json
Tracks Checker Agent approval workflow for architect implementations.

**Schema**:
```json
{
  "workflow_version": "1.0",
  "last_updated": "ISO-8601 datetime",
  "pending_approvals": [
    {
      "task_uuid": "string",
      "architect_agent": "string",
      "timestamp": "ISO-8601 datetime",
      "status": "awaiting_checker_approval"
    }
  ],
  "approval_history": [
    {
      "task_uuid": "string",
      "architect_agent": "string",
      "status": "APPROVED|PASS_WITH_WARNINGS|BLOCKED",
      "approved_at": "ISO-8601 datetime"
    }
  ],
  "enforcement_rules": {
    "mandatory_checker_approval": true,
    "block_user_response_until_approved": true,
    "allow_parallel_approvals": false,
    "max_pending_approvals": 3
  }
}
```

### resume_checkpoint.json
Enables crash recovery for interrupted agent sessions.

**Schema**:
```json
{
  "last_activity": "ISO-8601 datetime",
  "active_tasks": [
    {
      "task_uuid": "string",
      "agent": "string",
      "status": "in_progress",
      "file": "string",
      "started": "ISO-8601 datetime"
    }
  ],
  "pending_actions": ["string array"]
}
```

---

## Validation Schemas

### agent_context.schema.json
JSON Schema for validating agent context files.

**Location**: `schema/agent_context.schema.json`

**Validates**:
- Required fields (agent_name, initialized, total_sessions)
- Data types (string, integer, datetime format)
- Value constraints (total_sessions >= 0)

### workflow_state.schema.json
JSON Schema for validating workflow state file.

**Location**: `schema/workflow_state.schema.json`

**Validates**:
- Workflow version format
- Approval status enums
- Required workflow fields
- Array structures

---

## Usage Guidelines

### Reading Context
```typescript
import { readFileSync } from 'fs';

function loadAgentContext(agentName: string) {
  const contextPath = `.claude/context/agents/${agentName}.json`;
  return JSON.parse(readFileSync(contextPath, 'utf-8'));
}

const checkerContext = loadAgentContext('checker');
console.log(`Total checks: ${checkerContext.total_checks}`);
```

### Updating Context
```typescript
import { writeFileSync } from 'fs';

function updateAgentContext(agentName: string, updates: object) {
  const contextPath = `.claude/context/agents/${agentName}.json`;
  const context = JSON.parse(readFileSync(contextPath, 'utf-8'));

  const updatedContext = {
    ...context,
    ...updates,
    last_updated: new Date().toISOString()
  };

  writeFileSync(contextPath, JSON.stringify(updatedContext, null, 2));
}

updateAgentContext('checker', {
  total_checks: checkerContext.total_checks + 1
});
```

### Validating Context
```bash
# Using validate-context.sh script
../scripts/validate-context.sh agents/checker.json

# Output:
# ✅ checker.json: Valid (matches agent_context.schema.json)
```

---

## Context Lifecycle

### Initialization
Context files are created when:
1. Agent first invoked
2. Project initialized with `init-project.sh`
3. Manually created by user

### Updates
Context files updated when:
1. Agent completes task
2. Patterns learned from implementations
3. Metrics accumulated
4. Workflow states change

### Archival
Context files archived when:
1. Agent deprecated
2. Major version upgrade
3. Fresh start requested

**Archive Location**: `.claude/context/archive/{date}/{agent_name}.json`

---

## Best Practices

### DO
✅ Always update `last_updated` timestamp when modifying context
✅ Validate context files before committing (use `validate-context.sh`)
✅ Keep context files under 100KB (archive old data if exceeding)
✅ Use ISO-8601 format for all timestamps
✅ Increment `total_sessions` on each agent invocation

### DON'T
❌ Store sensitive data (API keys, passwords) in context files
❌ Manually edit context files without validation
❌ Delete context files (archive instead)
❌ Use relative timestamps (always UTC ISO-8601)
❌ Store large binary data (use references instead)

---

## Context Migration

### From Flat Structure to Organized
```bash
# Migration already completed (2025-10-11)
# Context files moved from .claude/context/*.json
# to organized structure:
#   - agents/*.json (agent-specific)
#   - workflow/*.json (workflow coordination)

# If you need to migrate again:
cd .claude/context
for f in *_context.json; do
  mv "$f" "agents/${f/_context/}"
done
```

### Version Upgrades
When upgrading context schema version:
1. Create backup: `cp context/agents/* context/archive/v1/`
2. Run migration script: `../scripts/migrate-context-v2.sh`
3. Validate: `../scripts/validate-context.sh --all`
4. Test agent invocations
5. Archive old versions

---

## Troubleshooting

### Invalid JSON
```bash
# Check syntax
jq empty agents/checker.json

# Fix with formatter
jq '.' agents/checker.json > agents/checker.json.tmp
mv agents/checker.json.tmp agents/checker.json
```

### Missing Context File
```json
{
  "error": "Context file not found",
  "file": "agents/new_agent.json",
  "solution": "Initialize with base schema",
  "command": "../scripts/init-agent-context.sh new_agent"
}
```

### Corrupted Context
```bash
# Restore from git history
git checkout HEAD -- .claude/context/agents/checker.json

# Or restore from backup
cp .claude/context/archive/2025-10-10/checker.json \
   .claude/context/agents/checker.json
```

---

## Metrics Dashboard

### Overall Statistics
```json
{
  "total_agents": 9,
  "active_agents": 3,
  "total_sessions": 10,
  "total_context_size_kb": 51.2,
  "avg_context_size_kb": 5.7,
  "last_activity": "2025-10-11T21:39:00Z"
}
```

### Agent Activity
| Agent | Sessions | Last Activity | Context Size |
|-------|----------|---------------|--------------|
| Checker | 5 | 2025-10-11 | 17.4 KB |
| Doc Tracker | 3 | 2025-10-11 | 19.3 KB |
| UX Specialist | 2 | 2025-10-08 | 13.8 KB |
| Others | 0 | - | <200 B |

---

## Related Documentation

- **Agent Templates**: `../agents/README.md`
- **Build Specs**: `../specs/README.md`
- **Workflow Manager**: `../scripts/workflow-manager.sh`
- **Validation Script**: `../scripts/validate-context.sh`
- **Orchestrator**: `../CLAUDE.md`

---

**Maintained by**: PromptForge Team
**Location**: `/Users/rohitiyer/datagrub/promptforge/.claude/context/`
