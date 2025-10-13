#!/bin/bash
# PostToolUse Hook - Automated Validation and Architecture Review
# Triggers subagents after Write/Edit tools modify critical files
#
# Auto-Triggered Agents (5 total):
# - Script Validator: scripts/**/*.{sh,py,js,ts}
# - README Validator: **/{README,SETUP,GUIDE}*.md
# - API Architect: api-tier/**/*.py (routes, services, models, schemas)
# - DB Architect: data-tier/**/*.py (models, migrations, seed_data)
# - UI Architect: ui-tier/**/*.{tsx,ts,jsx,js} (components, pages, hooks)
#
# Cross-Agent Consultations:
# - API Architect → UI Architect, DB Architect, API QA
# - DB Architect → API Architect (MANDATORY)
# - UI Architect → UX Specialist (MANDATORY), API Architect (if API calls)
#
# Integration: Uses Claude Code's Task tool to spawn subagents

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

# Determine paths relative to this hook's location
HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$HOOK_DIR/../.." && pwd)"
BUILD_SPECS_DIR="$PROJECT_ROOT/.claude/specs"
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
    AGENT_PROMPT_FILE="$AGENTS_DIR/04_validators/script-validator.md"
fi

# Check for documentation files
if [[ "$FILE_PATH" =~ \.(md|MD|markdown)$ ]] && [[ "$FILE_PATH" =~ (README|SETUP|GUIDE|INSTALL|DEPLOY|ARCHITECTURE|TESTING) ]]; then
    VALIDATE=true
    FILE_TYPE="readme"
    AGENT_TYPE="readme-validator"
    AGENT_PROMPT_FILE="$AGENTS_DIR/04_validators/readme-validator.md"
fi

# Check for API-tier files (routes, services, models, schemas)
if [[ "$FILE_PATH" =~ api-tier/ ]] && [[ "$FILE_PATH" =~ \.(py)$ ]]; then
    # Determine specific API file type
    if [[ "$FILE_PATH" =~ /routes/ ]] || [[ "$FILE_PATH" =~ /endpoints/ ]]; then
        VALIDATE=true
        FILE_TYPE="api-route"
        AGENT_TYPE="api-architect"
        AGENT_PROMPT_FILE="$AGENTS_DIR/01_architecture/API_Architect_Agent.md"
    elif [[ "$FILE_PATH" =~ /services/ ]]; then
        VALIDATE=true
        FILE_TYPE="api-service"
        AGENT_TYPE="api-architect"
        AGENT_PROMPT_FILE="$AGENTS_DIR/01_architecture/API_Architect_Agent.md"
    elif [[ "$FILE_PATH" =~ /schemas/ ]]; then
        VALIDATE=true
        FILE_TYPE="pydantic-schema"
        AGENT_TYPE="api-architect"
        AGENT_PROMPT_FILE="$AGENTS_DIR/01_architecture/API_Architect_Agent.md"
    elif [[ "$FILE_PATH" =~ /models/ ]] && [[ "$FILE_PATH" =~ api-tier ]]; then
        VALIDATE=true
        FILE_TYPE="api-model"
        AGENT_TYPE="api-architect"
        AGENT_PROMPT_FILE="$AGENTS_DIR/01_architecture/API_Architect_Agent.md"
    fi
fi

# Check for database-tier files (models, migrations)
if [[ "$FILE_PATH" =~ data-tier/ ]] || [[ "$FILE_PATH" =~ database-tier/ ]]; then
    if [[ "$FILE_PATH" =~ /models/ ]] && [[ "$FILE_PATH" =~ \.(py)$ ]]; then
        VALIDATE=true
        FILE_TYPE="db-model"
        AGENT_TYPE="db-architect"
        AGENT_PROMPT_FILE="$AGENTS_DIR/01_architecture/DB_Architect_Agent.md"
    elif [[ "$FILE_PATH" =~ /migrations/ ]] || [[ "$FILE_PATH" =~ alembic/versions/ ]]; then
        VALIDATE=true
        FILE_TYPE="db-migration"
        AGENT_TYPE="db-architect"
        AGENT_PROMPT_FILE="$AGENTS_DIR/01_architecture/DB_Architect_Agent.md"
    elif [[ "$FILE_PATH" =~ /seed_data/ ]] && [[ "$FILE_PATH" =~ \.(py|sql)$ ]]; then
        VALIDATE=true
        FILE_TYPE="db-seed"
        AGENT_TYPE="db-architect"
        AGENT_PROMPT_FILE="$AGENTS_DIR/01_architecture/DB_Architect_Agent.md"
    fi
fi

# Check for UI-tier files (components, pages, hooks)
if [[ "$FILE_PATH" =~ ui-tier/ ]] && [[ "$FILE_PATH" =~ \.(tsx|ts|jsx|js)$ ]]; then
    if [[ "$FILE_PATH" =~ /components/ ]]; then
        VALIDATE=true
        FILE_TYPE="ui-component"
        AGENT_TYPE="ui-architect"
        AGENT_PROMPT_FILE="$AGENTS_DIR/01_architecture/UI_Architect_Agent.md"
    elif [[ "$FILE_PATH" =~ /pages/ ]] || [[ "$FILE_PATH" =~ /routes/ ]]; then
        VALIDATE=true
        FILE_TYPE="ui-page"
        AGENT_TYPE="ui-architect"
        AGENT_PROMPT_FILE="$AGENTS_DIR/01_architecture/UI_Architect_Agent.md"
    elif [[ "$FILE_PATH" =~ /hooks/ ]] || [[ "$FILE_PATH" =~ /services/ ]]; then
        VALIDATE=true
        FILE_TYPE="ui-logic"
        AGENT_TYPE="ui-architect"
        AGENT_PROMPT_FILE="$AGENTS_DIR/01_architecture/UI_Architect_Agent.md"
    fi
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

# Different prompt templates for validators vs architects
if [[ "$AGENT_TYPE" == "api-architect" ]]; then
    # API Architect Review (not just validation)
    VALIDATION_PROMPT="You are the **API Architect** agent for the PromptForge project.

**CRITICAL CONTEXT:**
- **Build Specs Directory**: $BUILD_SPECS_DIR
- **Project Root**: $PROJECT_ROOT
- **Relevant Specifications**: $SPECS_LIST
- **Context File**: $CONTEXT_DIR/agents/api_architect.json

**Agent Template:**
$AGENT_TEMPLATE

---

**CURRENT TASK:**
Review the following $FILE_TYPE file that was just modified:

**File Path**: $FILE_PATH

**Review Requirements:**
1. Read the modified file: $FILE_PATH
2. Read relevant API specs from: $BUILD_SPECS_DIR/02_phase2_core_features/apis/
3. Load API Architect context: $CONTEXT_DIR/agents/api_architect.json
4. Perform architectural review per agent template
5. Check for:
   - REST API best practices
   - Security vulnerabilities (authentication, authorization, input validation)
   - Error handling patterns
   - Status code correctness
   - Schema alignment with database models
   - Breaking API changes (versioning needed?)
   - Cross-tier compatibility (UI ↔ API ↔ DB)
6. **MANDATORY CROSS-AGENT CONSULTATIONS:**
   - If UI changes needed → Flag for UI Architect review
   - If DB changes needed → Flag for DB Architect review
   - If breaking changes detected → Flag for API QA testing
7. Suggest improvements (do NOT auto-fix architectural decisions)

**Expected Output Format (JSON):**
\`\`\`json
{
  \"agent\": \"api-architect\",
  \"status\": \"ok|warn|error|blocked\",
  \"summary\": \"Brief summary of architectural review\",
  \"findings\": [
    {
      \"rule_id\": \"API-RULE-ID\",
      \"severity\": \"critical|high|medium|low\",
      \"file\": \"$FILE_PATH\",
      \"line\": 0,
      \"issue\": \"Description of architectural concern\",
      \"recommendation\": \"Suggested fix or improvement\",
      \"requires_user_decision\": true|false
    }
  ],
  \"spec_compliance\": {
    \"aligned_specs\": [\"Phase2_APIs.md#section\"],
    \"violations\": []
  },
  \"cross_tier_impacts\": {
    \"ui_changes_needed\": [],
    \"db_changes_needed\": [],
    \"breaking_changes\": []
  },
  \"consultation_requests\": {
    \"ui_architect\": {\"needed\": false, \"reason\": \"\"},
    \"db_architect\": {\"needed\": false, \"reason\": \"\"},
    \"api_qa\": {\"needed\": false, \"reason\": \"\"}
  },
  \"next_actions\": [\"Action items\"],
  \"context_update\": {
    \"last_reviewed\": \"ISO-8601 timestamp\",
    \"file\": \"$FILE_PATH\",
    \"review_type\": \"$FILE_TYPE\"
  }
}
\`\`\`

**IMPORTANT:**
- This is an ARCHITECTURAL REVIEW, not just validation
- Flag security concerns (missing auth, SQL injection risks, etc.)
- Check for breaking changes that need API versioning
- Identify cross-tier impacts (UI/DB changes needed)
- DO NOT auto-fix - provide recommendations for user review
- Update context with learnings for future reviews

Begin architectural review now."

elif [[ "$AGENT_TYPE" == "db-architect" ]]; then
    # DB Architect Review with MANDATORY API Architect consultation
    VALIDATION_PROMPT="You are the **DB Architect** agent for the PromptForge project.

**CRITICAL CONTEXT:**
- **Build Specs Directory**: $BUILD_SPECS_DIR
- **Project Root**: $PROJECT_ROOT
- **Relevant Specifications**: $SPECS_LIST
- **Context File**: $CONTEXT_DIR/agents/db_architect.json

**Agent Template:**
$AGENT_TEMPLATE

---

**CURRENT TASK:**
Review the following $FILE_TYPE file that was just modified:

**File Path**: $FILE_PATH

**Review Requirements:**
1. Read the modified file: $FILE_PATH
2. Read relevant DB specs from: $BUILD_SPECS_DIR/02_phase2_core_features/apis/
3. Load DB Architect context: $CONTEXT_DIR/agents/db_architect.json
4. Perform database architectural review per agent template
5. Check for:
   - Schema design best practices (normalization, indexes)
   - Migration safety (rollback scripts, data integrity)
   - Database constraints (foreign keys, NOT NULL, defaults)
   - Query performance implications
   - Data type correctness
   - Breaking schema changes
   - Cross-tier compatibility (API ORM models alignment)
6. **MANDATORY CROSS-AGENT CONSULTATION:**
   - API Architect consultation is **ALWAYS REQUIRED** for database changes
   - Reason: API ORM models must align with database schema
7. Suggest improvements (do NOT auto-fix architectural decisions)

**Expected Output Format (JSON):**
\`\`\`json
{
  \"agent\": \"db-architect\",
  \"status\": \"ok|warn|error|blocked\",
  \"summary\": \"Brief summary of database architectural review\",
  \"findings\": [
    {
      \"rule_id\": \"DB-RULE-ID\",
      \"severity\": \"critical|high|medium|low\",
      \"file\": \"$FILE_PATH\",
      \"line\": 0,
      \"issue\": \"Description of database concern\",
      \"recommendation\": \"Suggested fix or improvement\",
      \"requires_user_decision\": true|false
    }
  ],
  \"spec_compliance\": {
    \"aligned_specs\": [\"Phase2_APIs.md#database-section\"],
    \"violations\": []
  },
  \"cross_tier_impacts\": {
    \"api_orm_changes_needed\": [],
    \"breaking_changes\": [],
    \"migration_required\": false
  },
  \"consultation_requests\": {
    \"api_architect\": {\"needed\": true, \"reason\": \"MANDATORY: API ORM models must be updated to reflect schema changes\"}
  },
  \"next_actions\": [\"Action items\"],
  \"context_update\": {
    \"last_reviewed\": \"ISO-8601 timestamp\",
    \"file\": \"$FILE_PATH\",
    \"review_type\": \"$FILE_TYPE\"
  }
}
\`\`\`

**IMPORTANT:**
- This is a DATABASE ARCHITECTURAL REVIEW, not just validation
- ALWAYS flag API Architect for consultation (DB changes affect API ORM)
- Check for breaking schema changes that need migration strategy
- Verify rollback scripts exist for migrations
- Ensure indexes exist for foreign keys and frequently queried columns
- DO NOT auto-fix - provide recommendations for user review
- Update context with learnings for future reviews

Begin database architectural review now."

elif [[ "$AGENT_TYPE" == "ui-architect" ]]; then
    # UI Architect Review with MANDATORY UX Specialist consultation
    VALIDATION_PROMPT="You are the **UI Architect** agent for the PromptForge project.

**CRITICAL CONTEXT:**
- **Build Specs Directory**: $BUILD_SPECS_DIR
- **Project Root**: $PROJECT_ROOT
- **Relevant Specifications**: $SPECS_LIST
- **Context File**: $CONTEXT_DIR/agents/ui_architect.json

**Agent Template:**
$AGENT_TEMPLATE

---

**CURRENT TASK:**
Review the following $FILE_TYPE file that was just modified:

**File Path**: $FILE_PATH

**Review Requirements:**
1. Read the modified file: $FILE_PATH
2. Read relevant UI specs from: $BUILD_SPECS_DIR/01_phase1_foundation/ and $BUILD_SPECS_DIR/02_phase2_core_features/ui/
3. Load UI Architect context: $CONTEXT_DIR/agents/ui_architect.json
4. Perform UI architectural review per agent template
5. Check for:
   - React component best practices (hooks, state management)
   - Module Federation integration (remote/host configuration)
   - Component structure and modularity
   - API integration patterns
   - State management (local vs global)
   - Error boundaries and loading states
   - Accessibility patterns (ARIA labels, keyboard navigation)
   - Design system compliance (colors, spacing, typography)
   - Cross-tier compatibility (API contracts, TypeScript types)
6. **MANDATORY CROSS-AGENT CONSULTATIONS:**
   - UX Specialist consultation is **ALWAYS REQUIRED** for UI components
   - Reason: All UI must follow design system and accessibility standards
   - API Architect consultation if API calls detected or API contracts changed
7. Suggest improvements (do NOT auto-fix architectural decisions)

**Expected Output Format (JSON):**
\`\`\`json
{
  \"agent\": \"ui-architect\",
  \"status\": \"ok|warn|error|blocked\",
  \"summary\": \"Brief summary of UI architectural review\",
  \"findings\": [
    {
      \"rule_id\": \"UI-RULE-ID\",
      \"severity\": \"critical|high|medium|low\",
      \"file\": \"$FILE_PATH\",
      \"line\": 0,
      \"issue\": \"Description of UI concern\",
      \"recommendation\": \"Suggested fix or improvement\",
      \"requires_user_decision\": true|false
    }
  ],
  \"spec_compliance\": {
    \"aligned_specs\": [\"Phase1_CoreUI.md#section\", \"Phase2_UI_Framework.md#section\"],
    \"violations\": []
  },
  \"cross_tier_impacts\": {
    \"api_changes_needed\": [],
    \"design_system_violations\": [],
    \"accessibility_issues\": [],
    \"breaking_changes\": []
  },
  \"consultation_requests\": {
    \"ux_specialist\": {\"needed\": true, \"reason\": \"MANDATORY: Design system and accessibility compliance review\"},
    \"api_architect\": {\"needed\": false, \"reason\": \"\"}
  },
  \"next_actions\": [\"Action items\"],
  \"context_update\": {
    \"last_reviewed\": \"ISO-8601 timestamp\",
    \"file\": \"$FILE_PATH\",
    \"review_type\": \"$FILE_TYPE\"
  }
}
\`\`\`

**IMPORTANT:**
- This is a UI ARCHITECTURAL REVIEW, not just validation
- ALWAYS flag UX Specialist for consultation (design system compliance)
- Check for accessibility violations (WCAG AAA standards)
- Identify custom colors/spacing that violate design system
- Flag missing loading states or error boundaries
- If API calls detected, flag API Architect for contract compatibility
- DO NOT auto-fix - provide recommendations for user review
- Update context with learnings for future reviews

Begin UI architectural review now."

else
    # Validator agents (script, readme)
    VALIDATION_PROMPT="You are the **$AGENT_TYPE** subagent for the PromptForge project.

**CRITICAL CONTEXT:**
- **Build Specs Directory**: $BUILD_SPECS_DIR
- **Project Root**: $PROJECT_ROOT
- **Relevant Specifications**: $SPECS_LIST
- **Context File**: $CONTEXT_DIR/agents/validator.json

**Agent Instructions:**
$AGENT_TEMPLATE

---

**CURRENT TASK:**
Validate the following $FILE_TYPE file that was just modified:

**File Path**: $FILE_PATH

**Validation Requirements:**
1. Read the target file: $FILE_PATH
2. Read relevant build specs from: $BUILD_SPECS_DIR
3. Load previous validation context from: $CONTEXT_DIR/agents/validator.json (if exists)
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
fi

# ============================================================================
# Trigger Validation Subagent
# ============================================================================

# Generate task UUID
TASK_UUID=$(uuidgen 2>/dev/null || echo "task-$(date +%s)")

# Determine action verb (validation vs review)
if [[ "$AGENT_TYPE" == "api-architect" ]] || [[ "$AGENT_TYPE" == "db-architect" ]] || [[ "$AGENT_TYPE" == "ui-architect" ]]; then
    ACTION_VERB="Reviewing"
    ICON="🏗️"
    MESSAGE_TYPE="architectural_review_triggered"
else
    ACTION_VERB="Validating"
    ICON="🔍"
    MESSAGE_TYPE="validation_triggered"
fi

# Log trigger
cat <<EOF >&2
[PostToolUse Hook] Triggering $ACTION_VERB:
  File: $(basename "$FILE_PATH")
  Type: $FILE_TYPE
  Agent: $AGENT_TYPE
  Task: $TASK_UUID
EOF

# Return control to Claude Code with subagent request
# Claude Code will spawn the Task tool with the prompt
cat <<EOF
{
  "type": "$MESSAGE_TYPE",
  "message": "$ICON $ACTION_VERB $FILE_TYPE: $(basename "$FILE_PATH")",
  "task_uuid": "$TASK_UUID",
  "agent": "$AGENT_TYPE",
  "file": "$FILE_PATH",
  "validation_prompt": $(echo "$VALIDATION_PROMPT" | jq -Rs .)
}
EOF

exit 0
