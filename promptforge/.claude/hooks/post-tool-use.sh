#!/bin/bash
# PostToolUse Hook - Automated Script and README Validation
# Triggers validation subagent after Write/Edit tools modify scripts or documentation
#
# Context:
# - Build Specs: /Users/rohitiyer/datagrub/PromptForge_Build_Specs
# - Project Root: /Users/rohitiyer/datagrub/promptforge
# - Subagent Definitions: .claude/agents/
#
# Integration: Uses Claude Code's Task tool to spawn validation subagents

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

BUILD_SPECS_DIR="/Users/rohitiyer/datagrub/PromptForge_Build_Specs"
PROJECT_ROOT="/Users/rohitiyer/datagrub/promptforge"
CONTEXT_DIR="$PROJECT_ROOT/.claude/context"
AGENTS_DIR="$PROJECT_ROOT/.claude/agents"

# ============================================================================
# Parse Tool Use Input
# ============================================================================

# Read tool use data from stdin (JSON format from Claude Code)
TOOL_DATA=$(cat)

# Extract tool information
TOOL_NAME=$(echo "$TOOL_DATA" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$TOOL_DATA" | jq -r '.parameters.file_path // empty')

# Only proceed for Write or Edit operations
if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" ]]; then
    exit 0
fi

# Validate file path exists
if [[ -z "$FILE_PATH" ]]; then
    exit 0
fi

# ============================================================================
# Determine if Validation is Required
# ============================================================================

VALIDATE=false
FILE_TYPE=""
AGENT_TYPE=""
AGENT_PROMPT_FILE=""

# Check for script files
if [[ "$FILE_PATH" =~ /scripts/ ]] && [[ "$FILE_PATH" =~ \.(sh|bash|py|js|ts)$ ]]; then
    VALIDATE=true
    FILE_TYPE="script"
    AGENT_TYPE="script-validator"
    AGENT_PROMPT_FILE="$AGENTS_DIR/script-validator.md"
fi

# Check for documentation files
if [[ "$FILE_PATH" =~ \.(md|MD|markdown)$ ]] && [[ "$FILE_PATH" =~ (README|SETUP|GUIDE|INSTALL|DEPLOY|ARCHITECTURE|TESTING) ]]; then
    VALIDATE=true
    FILE_TYPE="readme"
    AGENT_TYPE="readme-validator"
    AGENT_PROMPT_FILE="$AGENTS_DIR/readme-validator.md"
fi

# Exit if file type doesn't require validation
if [[ "$VALIDATE" != "true" ]]; then
    exit 0
fi

# ============================================================================
# Load Agent Prompt Template
# ============================================================================

if [[ ! -f "$AGENT_PROMPT_FILE" ]]; then
    echo "WARNING: Agent prompt file not found: $AGENT_PROMPT_FILE" >&2
    exit 0
fi

AGENT_TEMPLATE=$(cat "$AGENT_PROMPT_FILE")

# ============================================================================
# Determine Relevant Build Specs
# ============================================================================

RELEVANT_SPECS=()

# Analyze file path to determine relevant specs
if [[ "$FILE_PATH" =~ ui-tier|frontend|mfe- ]]; then
    RELEVANT_SPECS+=("Phase1_CoreUI.md")
fi

if [[ "$FILE_PATH" =~ api-tier|backend|routes|services ]]; then
    RELEVANT_SPECS+=("Phase2_APIs.md" "Phase2_API_SecurityRequirements.md" "Phase2_API_PerformanceRequirements.md")
fi

if [[ "$FILE_PATH" =~ data-tier|database|migrations|models ]]; then
    RELEVANT_SPECS+=("Phase2_APIs.md")
fi

if [[ "$FILE_PATH" =~ test|qa|evaluation ]]; then
    RELEVANT_SPECS+=("Phase2_Evaluation_Framework.md")
fi

if [[ "$FILE_PATH" =~ privacy|compliance|gdpr ]]; then
    RELEVANT_SPECS+=("Phase3_Privacy_Framework.md")
fi

# Default: Include Phase2_APIs.md if no specific match
if [[ ${#RELEVANT_SPECS[@]} -eq 0 ]]; then
    RELEVANT_SPECS+=("Phase2_APIs.md")
fi

# ============================================================================
# Build Validation Prompt
# ============================================================================

SPECS_LIST=$(printf '%s\n' "${RELEVANT_SPECS[@]}" | jq -R . | jq -s .)

VALIDATION_PROMPT="You are the **$AGENT_TYPE** subagent for the PromptForge project.

**CRITICAL CONTEXT:**
- **Build Specs Directory**: $BUILD_SPECS_DIR
- **Project Root**: $PROJECT_ROOT
- **Relevant Specifications**: $SPECS_LIST
- **Context File**: $CONTEXT_DIR/validator_context.json

**Agent Instructions:**
$AGENT_TEMPLATE

---

**CURRENT TASK:**
Validate the following $FILE_TYPE file that was just modified:

**File Path**: $FILE_PATH

**Validation Requirements:**
1. Read the target file: $FILE_PATH
2. Read relevant build specs from: $BUILD_SPECS_DIR
3. Load previous validation context from: $CONTEXT_DIR/validator_context.json (if exists)
4. Perform comprehensive validation per agent template checklist
5. Auto-fix issues when safe to do so
6. Generate detailed JSON validation report

**Expected Output Format (JSON):**
\`\`\`json
{
  \"agent\": \"$AGENT_TYPE\",
  \"status\": \"ok|warn|error|blocked\",
  \"summary\": \"Brief summary of validation results\",
  \"findings\": [
    {
      \"rule_id\": \"RULE-ID\",
      \"severity\": \"critical|high|medium|low\",
      \"file\": \"$FILE_PATH\",
      \"line\": 0,
      \"issue\": \"Description of issue\",
      \"fix_applied\": true|false,
      \"fix_description\": \"What was fixed (if applicable)\",
      \"recommendation\": \"How to resolve (if not auto-fixed)\"
    }
  ],
  \"spec_compliance\": {
    \"aligned_specs\": [\"spec#section\"],
    \"violations\": []
  },
  \"next_actions\": [\"Action items\"],
  \"context_update\": {
    \"last_validated\": \"ISO-8601 timestamp\",
    \"issues_found\": 0,
    \"issues_fixed\": 0
  }
}
\`\`\`

**IMPORTANT:**
- Always cross-reference with build specs in $BUILD_SPECS_DIR
- Apply safe auto-fixes immediately (syntax, formatting, missing headers)
- Report issues requiring review (security, logic, architectural decisions)
- Update validation context with learnings
- Provide clear, actionable recommendations

Begin validation now."

# ============================================================================
# Trigger Validation Subagent
# ============================================================================

# Generate task UUID
TASK_UUID=$(uuidgen 2>/dev/null || echo "task-$(date +%s)")

# Log validation trigger
cat <<EOF >&2
[PostToolUse Hook] Triggering validation:
  File: $(basename "$FILE_PATH")
  Type: $FILE_TYPE
  Agent: $AGENT_TYPE
  Task: $TASK_UUID
EOF

# Return control to Claude Code with subagent request
# Claude Code will spawn the Task tool with the prompt
cat <<EOF
{
  "type": "validation_triggered",
  "message": "🔍 Validating $FILE_TYPE: $(basename "$FILE_PATH")",
  "task_uuid": "$TASK_UUID",
  "agent": "$AGENT_TYPE",
  "file": "$FILE_PATH",
  "validation_prompt": $(echo "$VALIDATION_PROMPT" | jq -Rs .)
}
EOF

exit 0
