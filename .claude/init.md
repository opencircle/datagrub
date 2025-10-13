# Claude Initialization - /datagrub Workspace

**Version**: 2.0.0
**Last Updated**: 2025-10-11
**Status**: ✅ Updated for Self-Contained Architecture

---

## 🎯 Quick Navigation

When Claude Code starts in `/Users/rohitiyer/datagrub`, you have access to:

### Primary Project: PromptForge
**Location**: `promptforge/`
**Status**: ✅ Fully Self-Contained Multi-Agent System

All PromptForge orchestration is now **self-contained** in `promptforge/.claude/`:
- **Master Orchestrator**: `promptforge/.claude/CLAUDE.md` (comprehensive 850-line guide)
- **11 Agent Templates**: `promptforge/.claude/agents/` (organized by role)
- **20 Build Specs**: `promptforge/.claude/specs/` (organized by phase/domain)
- **Context Files**: `promptforge/.claude/context/` (persistent agent memory)
- **Automated Hooks**: `promptforge/.claude/hooks/` (validation triggers)

---

## 📋 Subagent Registry (11 Agents)

### ✅ Active (Auto-triggered)
1. **Script Validator** - `promptforge/.claude/agents/04_validators/script-validator.md`
2. **README Validator** - `promptforge/.claude/agents/04_validators/readme-validator.md`

### 🏗️ Architecture Agents (Manual)
3. **UX Specialist** ⭐ **Priority: First for UX** - `promptforge/.claude/agents/01_architecture/UX_Specialist_Agent.md`
4. **UI Architect** - `promptforge/.claude/agents/01_architecture/UI_Architect_Agent.md`
5. **API Architect** - `promptforge/.claude/agents/01_architecture/API_Architect_Agent.md`
6. **DB Architect** - `promptforge/.claude/agents/01_architecture/DB_Architect_Agent.md`

### 🧪 QA Agents (Manual)
7. **API QA** - `promptforge/.claude/agents/02_quality/API_QA_Agent.md`
8. **UI QA** - `promptforge/.claude/agents/02_quality/UI_QA_Agent.md`
9. **Checker** 🔒 **Final Gate** - `promptforge/.claude/agents/02_quality/Checker_Agent.md`

### 📚 Operations (Manual)
10. **Doc Context Tracker** - `promptforge/.claude/agents/03_operations/Doc_Context_Tracker_Agent.md`

**Note**:
- **UX Specialist** should be consulted **first** for all design/style/UX decisions
- **Checker Agent** is **MANDATORY** final approval gate for all architect work

---

## 📁 Key Locations (Self-Contained)

- **Master Orchestrator**: `promptforge/.claude/CLAUDE.md` ← **START HERE**
- **Agent Templates**: `promptforge/.claude/agents/` (11 agents, version 2.0.0)
- **Build Specs**: `promptforge/.claude/specs/` (20 specs, organized by phase)
- **Context Files**: `promptforge/.claude/context/agents/` (persistent memory)
- **Workflow State**: `promptforge/.claude/context/workflow/` (approval tracking)
- **Validation Hooks**: `promptforge/.claude/hooks/post-tool-use.sh` (auto-validation)

---

## 🚀 Quick Commands

### Get Started
```
"Read promptforge/.claude/CLAUDE.md for the master orchestrator guide"
```

### List Subagents
```
"Show me all configured subagents and their status"
"Read promptforge/.claude/agents/README.md"
```

### Invoke an Agent
```
"Invoke UI Architect to review promptforge/ui-tier/mfe-projects"
"Run Script Validator on promptforge/scripts/deploy.sh"
"Have API Architect implement evaluation routes"
"Invoke Checker Agent to validate recent changes"
```

### Check Context
```
"Check all subagent context files"
"Show me validation history from validator context"
"List pending Checker approvals"
```

### Navigate to PromptForge
```
"Change to promptforge directory"
```

---

## 📖 Documentation Hierarchy

**Level 1 - Master Guide** (Start here):
- `promptforge/.claude/CLAUDE.md` - Comprehensive orchestrator (850 lines)

**Level 2 - Specialized Guides**:
- `promptforge/.claude/agents/README.md` - Agent registry (8KB)
- `promptforge/.claude/specs/README.md` - Spec index (5KB)
- `promptforge/.claude/context/README.md` - Context documentation (7KB)

**Level 3 - Migration History**:
- `promptforge/.claude/REORGANIZATION_COMPLETE.md` - Reorganization summary

---

## 🔄 Migration Status

**Previous Structure** (DEPRECATED):
- ❌ `/datagrub/Claude_Subagent_Prompts/` - Migrated to `promptforge/.claude/agents/`
- ❌ `/datagrub/PromptForge_Build_Specs/` - Migrated to `promptforge/.claude/specs/`
- ❌ `/datagrub/CLAUDE.md` - Replaced by `promptforge/.claude/CLAUDE.md`

**Current Structure** (ACTIVE):
- ✅ All resources self-contained in `promptforge/.claude/`
- ✅ Fully portable (no absolute paths)
- ✅ 100% reorganization complete

---

## 💡 Usage Patterns

### Pattern 1: Start from /datagrub
```bash
# If you start here, navigate to promptforge first
cd promptforge

# Then read the master orchestrator
"Read .claude/CLAUDE.md"
```

### Pattern 2: Start from /datagrub/promptforge
```bash
# You're already in the right place
"Read .claude/CLAUDE.md"
```

### Pattern 3: Multi-Project Workspace
```
/datagrub/
├── promptforge/     ← PromptForge (full subagent system)
├── oiiro/           ← Other projects
└── other-projects/
```

Each project can have its own `.claude/` configuration.

---

## ⚙️ System Status

- **Architecture**: Fully Self-Contained (Option 1)
- **Agent Templates**: 11 complete with v2.0.0 headers
- **Build Specs**: 20 specs organized by phase/domain
- **Context Files**: 11 with JSON schema validation
- **Documentation**: 23KB comprehensive docs
- **Completion**: ✅ 100%
- **Production Ready**: ✅ Yes

---

**For complete details, read**: `promptforge/.claude/CLAUDE.md`

**Status**: ✅ PromptForge subagent system initialized and ready
