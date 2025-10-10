# Claude Code Orchestrator Configuration

This directory contains the enhanced multi-subagent orchestration system for PromptForge.

## Directory Structure

```
.claude/
├── README.md                          # This file
├── CLAUDE_ORCHESTRATOR.md            # Master orchestrator documentation
├── hooks/                            # Event-driven hooks
│   └── post-tool-use.sh             # Validation trigger hook
├── agents/                           # Subagent definitions
│   ├── script-validator.md          # Script validation agent
│   └── readme-validator.md          # Documentation validation agent
├── context/                          # Persistent agent memory
│   ├── validator_context.json       # Validation history and patterns
│   ├── ui_architect_context.json    # UI architecture decisions
│   ├── api_architect_context.json   # API architecture decisions
│   ├── db_architect_context.json    # Database architecture decisions
│   ├── apiqa_context.json           # API QA findings
│   ├── uiqa_context.json            # UI QA findings
│   ├── doc_tracker_context.json     # Documentation tracking
│   └── resume_checkpoint_context.json # Crash recovery state
└── reports/                          # Validation reports (generated)
```

## Features

### ✅ Automated Validation
- PostToolUse hook triggers on script/readme changes
- Subagents validate against PromptForge_Build_Specs automatically
- Issues auto-fixed when possible
- Comprehensive validation reports

### ✅ Build Spec Awareness
- All validations cross-reference `/Users/rohitiyer/datagrub/PromptForge_Build_Specs`
- Phase-specific compliance checking
- Architectural alignment verification

### ✅ Persistent Context
- All validations logged to context files
- Patterns learned over time (common issues, project conventions)
- Resume capability for crash recovery

### ✅ Multi-Agent Orchestration
- Multiple agents run in parallel via Claude Code Task tool
- Standardized JSON communication protocol
- Aggregated reporting

## Quick Start

### 1. Verify Installation
```bash
cd /Users/rohitiyer/datagrub/promptforge
ls -la .claude/hooks/post-tool-use.sh
ls -la .claude/context/
```

### 2. Test Validation (Manual)
```bash
# Trigger script validation manually
echo "Validate scripts/deploy.sh against Phase 2 deployment specs"
```

### 3. Automatic Validation
When you edit any script or README file, the PostToolUse hook will automatically:
1. Detect the file type
2. Determine relevant build specs
3. Spawn appropriate validation subagent
4. Run comprehensive validation
5. Auto-fix issues
6. Return validation report

## Supported File Types

### Scripts (Auto-validated)
- `scripts/**/*.sh` (Shell scripts)
- `scripts/**/*.bash` (Bash scripts)
- `scripts/**/*.py` (Python scripts)
- `scripts/**/*.js` (JavaScript)
- `scripts/**/*.ts` (TypeScript)

### Documentation (Auto-validated)
- `**/README*.md`
- `**/SETUP*.md`
- `**/GUIDE*.md`
- `**/INSTALL*.md`
- `**/DEPLOY*.md`
- `**/ARCHITECTURE*.md`
- `**/TESTING*.md`

## Validation Rules

### Scripts
- ✅ Syntax validation (shellcheck, pylint, eslint)
- ✅ Security checks (no hardcoded credentials)
- ✅ Build spec compliance
- ✅ Error handling verification
- ✅ Dependency checking
- ✅ Path validation

### Documentation
- ✅ Command accuracy (syntax validation)
- ✅ File path verification
- ✅ Build spec alignment
- ✅ Completeness checking
- ✅ Markdown quality
- ✅ Link validation

## Configuration

### Hook Configuration
The PostToolUse hook is located at `.claude/hooks/post-tool-use.sh` and configured to:
- Trigger on Write/Edit operations
- Filter by file patterns (scripts, documentation)
- Inject build spec context
- Spawn appropriate subagent

### Context Files
Context files store:
- Validation history
- Learned patterns (common issues)
- Project conventions
- Resume checkpoints

### Agent Definitions
Agent definitions in `.claude/agents/` specify:
- Validation rules and checklists
- Auto-fix policies
- Output format requirements
- Build spec integration

## Usage Examples

### Example 1: Script Validation
```bash
# Edit a script
echo "#!/bin/bash" > scripts/test.sh
echo "aws s3 ls" >> scripts/test.sh

# PostToolUse hook automatically triggers:
# - Validates syntax with shellcheck
# - Checks for AWS profile usage
# - Verifies alignment with deployment specs
# - Auto-fixes missing error handling
# - Returns validation report
```

### Example 2: Documentation Validation
```bash
# Update README
echo "## Installation" >> README.md
echo "\`\`\`" >> README.md
echo "npm install" >> README.md
echo "\`\`\`" >> README.md

# PostToolUse hook automatically:
# - Validates code block has language tag
# - Auto-fixes: adds ```bash tag
# - Checks command syntax
# - Verifies against build specs
# - Returns validation report
```

### Example 3: Manual Validation Request
```
User: "Validate all scripts in api-tier/scripts/ for Phase 2 compliance"

Claude: [Spawns script-validator subagent]
- Reads all scripts in api-tier/scripts/
- Cross-references Phase2_APIs.md, Phase2_API_SecurityRequirements.md
- Runs comprehensive validation
- Auto-fixes safe issues
- Returns aggregated report
```

## Integration with Build Specs

All validations automatically reference:
- `/Users/rohitiyer/datagrub/PromptForge_Build_Specs/Phase1_CoreUI.md`
- `/Users/rohitiyer/datagrub/PromptForge_Build_Specs/Phase2_APIs.md`
- `/Users/rohitiyer/datagrub/PromptForge_Build_Specs/Phase2_API_SecurityRequirements.md`
- `/Users/rohitiyer/datagrub/PromptForge_Build_Specs/Phase2_API_PerformanceRequirements.md`
- `/Users/rohitiyer/datagrub/PromptForge_Build_Specs/Phase2_Evaluation_Framework.md`
- `/Users/rohitiyer/datagrub/PromptForge_Build_Specs/Phase3_Privacy_Framework.md`

The hook intelligently selects relevant specs based on file paths and content.

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
ls -la .claude/context/

# Reinitialize if needed
cd .claude/context
echo '{"agent_name":"validator","initialized":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","total_sessions":0,"validations":[]}' > validator_context.json
```

### Validation Not Running
Check that:
1. File matches supported patterns (scripts/, README.md, etc.)
2. Hook script is executable
3. Required tools installed (shellcheck, jq, etc.)

## Dependencies

### Required Tools
```bash
# JSON processing
brew install jq

# Script validation
brew install shellcheck  # for shell scripts
pip install pylint       # for Python scripts
npm install -g eslint    # for JavaScript/TypeScript
```

### Optional Tools
```bash
# Enhanced validation
pip install black        # Python formatting
npm install -g prettier  # JS/TS formatting
```

## Next Steps

1. **Test the system**: Edit a script or README to trigger validation
2. **Review validation reports**: Check `.claude/reports/` for generated reports
3. **Customize agents**: Modify `.claude/agents/*.md` for project-specific rules
4. **Extend routing**: Add new file patterns to hook script
5. **Add more agents**: Create additional agent definitions for specialized validation

## References

- **Main Orchestrator Docs**: `.claude/CLAUDE_ORCHESTRATOR.md`
- **Original Init Script**: `/Users/rohitiyer/datagrub/Claude_Init_Script.md`
- **Subagent Templates**: `/Users/rohitiyer/datagrub/Claude_Subagent_Prompts/`
- **Build Specs**: `/Users/rohitiyer/datagrub/PromptForge_Build_Specs/`

---

**Version**: 2.0
**Last Updated**: 2025-10-05
**Status**: Active
