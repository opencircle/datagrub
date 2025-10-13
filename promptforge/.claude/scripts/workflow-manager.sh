#!/bin/bash
# Workflow State Manager - Track approval checkpoints
#
# Purpose: Manage architect agent approval workflow state
# Enforces: MANDATORY checker approval policy (CLAUDE_ORCHESTRATOR.md:73-90)
#
# Usage:
#   ./workflow-manager.sh add <task_uuid> <architect_agent>     - Add approval checkpoint
#   ./workflow-manager.sh check <task_uuid>                     - Check approval status
#   ./workflow-manager.sh approve <task_uuid> <status>          - Record approval
#   ./workflow-manager.sh list                                  - List pending approvals
#   ./workflow-manager.sh history [limit]                       - Show approval history
#
# Exit Codes:
#   0 - Success
#   1 - Invalid command or arguments
#   2 - Workflow state file not found

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
WORKFLOW_STATE="$PROJECT_ROOT/.claude/context/workflow_state.json"

# ============================================================================
# Helper Functions
# ============================================================================

error() {
    echo "ERROR: $*" >&2
    exit 1
}

usage() {
    cat <<EOF
Workflow State Manager - Track architect agent approval checkpoints

Usage:
  $0 add <task_uuid> <architect_agent>    Add approval checkpoint
  $0 check <task_uuid>                    Check approval status
  $0 approve <task_uuid> <status>         Record approval (APPROVED|PASS_WITH_WARNINGS|BLOCKED)
  $0 list                                 List pending approvals
  $0 history [limit]                      Show approval history (default: 10)

Examples:
  $0 add task-abc-123 UI_Architect_Agent
  $0 check task-abc-123
  $0 approve task-abc-123 APPROVED
  $0 list
  $0 history 20

Exit Codes:
  0 - Success
  1 - Invalid command or arguments
  2 - Workflow state file not found
EOF
    exit 1
}

init_workflow_state() {
    if [[ ! -f "$WORKFLOW_STATE" ]]; then
        echo "Initializing workflow state file: $WORKFLOW_STATE" >&2
        mkdir -p "$(dirname "$WORKFLOW_STATE")"
        cat > "$WORKFLOW_STATE" <<EOF
{
  "workflow_version": "1.0",
  "last_updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "pending_approvals": [],
  "approval_history": [],
  "enforcement_rules": {
    "mandatory_checker_approval": true,
    "block_user_response_until_approved": true,
    "allow_parallel_approvals": false,
    "max_pending_approvals": 3
  }
}
EOF
    fi
}

validate_status() {
    local status="$1"
    case "$status" in
        APPROVED|PASS_WITH_WARNINGS|BLOCKED)
            return 0
            ;;
        *)
            error "Invalid approval status: $status. Must be APPROVED, PASS_WITH_WARNINGS, or BLOCKED"
            ;;
    esac
}

# ============================================================================
# Command Handlers
# ============================================================================

cmd_add() {
    local task_uuid="${1:-}"
    local architect_agent="${2:-}"

    [[ -z "$task_uuid" ]] && error "Missing argument: task_uuid"
    [[ -z "$architect_agent" ]] && error "Missing argument: architect_agent"

    init_workflow_state

    # Check if checkpoint already exists
    local existing
    existing=$(jq -r --arg uuid "$task_uuid" \
        '.pending_approvals[] | select(.task_uuid == $uuid) | .task_uuid' \
        "$WORKFLOW_STATE" 2>/dev/null || echo "")

    if [[ -n "$existing" ]]; then
        echo "⚠️  Checkpoint already exists for $task_uuid (status: awaiting_checker_approval)" >&2
        return 0
    fi

    # Add new checkpoint
    jq --arg uuid "$task_uuid" \
       --arg agent "$architect_agent" \
       --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.pending_approvals += [{
           "task_uuid": $uuid,
           "architect_agent": $agent,
           "timestamp": $timestamp,
           "status": "awaiting_checker_approval"
       }] | .last_updated = $timestamp' \
       "$WORKFLOW_STATE" > "$WORKFLOW_STATE.tmp"

    mv "$WORKFLOW_STATE.tmp" "$WORKFLOW_STATE"
    echo "✅ Added approval checkpoint for $task_uuid ($architect_agent)"
}

cmd_check() {
    local task_uuid="${1:-}"

    [[ -z "$task_uuid" ]] && error "Missing argument: task_uuid"
    [[ ! -f "$WORKFLOW_STATE" ]] && echo "approved" && return 0

    local status
    status=$(jq -r --arg uuid "$task_uuid" \
        '.pending_approvals[] | select(.task_uuid == $uuid) | .status' \
        "$WORKFLOW_STATE" 2>/dev/null || echo "")

    if [[ -z "$status" ]]; then
        # Check approval history
        local approved_status
        approved_status=$(jq -r --arg uuid "$task_uuid" \
            '.approval_history[] | select(.task_uuid == $uuid) | .status' \
            "$WORKFLOW_STATE" 2>/dev/null | tail -1 || echo "")

        if [[ -n "$approved_status" ]]; then
            echo "$approved_status"
        else
            echo "approved"
        fi
    else
        echo "$status"
    fi
}

cmd_approve() {
    local task_uuid="${1:-}"
    local approval_status="${2:-}"

    [[ -z "$task_uuid" ]] && error "Missing argument: task_uuid"
    [[ -z "$approval_status" ]] && error "Missing argument: approval_status"

    validate_status "$approval_status"
    init_workflow_state

    # Get architect agent before removing from pending
    local architect_agent
    architect_agent=$(jq -r --arg uuid "$task_uuid" \
        '.pending_approvals[] | select(.task_uuid == $uuid) | .architect_agent' \
        "$WORKFLOW_STATE" 2>/dev/null || echo "")

    if [[ -z "$architect_agent" ]]; then
        error "Checkpoint not found for task_uuid: $task_uuid. Use 'add' command first."
    fi

    # Remove from pending and add to history
    jq --arg uuid "$task_uuid" \
       --arg status "$approval_status" \
       --arg agent "$architect_agent" \
       --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       'del(.pending_approvals[] | select(.task_uuid == $uuid)) |
        .approval_history += [{
            "task_uuid": $uuid,
            "architect_agent": $agent,
            "status": $status,
            "approved_at": $timestamp
        }] | .last_updated = $timestamp' \
       "$WORKFLOW_STATE" > "$WORKFLOW_STATE.tmp"

    mv "$WORKFLOW_STATE.tmp" "$WORKFLOW_STATE"

    case "$approval_status" in
        APPROVED)
            echo "✅ Approved $task_uuid with status: APPROVED"
            ;;
        PASS_WITH_WARNINGS)
            echo "⚠️  Approved $task_uuid with status: PASS_WITH_WARNINGS"
            ;;
        BLOCKED)
            echo "🚫 Blocked $task_uuid - requires revisions before approval"
            ;;
    esac
}

cmd_list() {
    init_workflow_state

    local count
    count=$(jq -r '.pending_approvals | length' "$WORKFLOW_STATE")

    if [[ "$count" -eq 0 ]]; then
        echo "No pending approvals"
        return 0
    fi

    echo "Pending Approvals ($count):"
    echo ""

    jq -r '.pending_approvals[] |
        "  Task: \(.task_uuid)\n  Agent: \(.architect_agent)\n  Status: \(.status)\n  Since: \(.timestamp)\n"' \
        "$WORKFLOW_STATE"
}

cmd_history() {
    local limit="${1:-10}"
    init_workflow_state

    local count
    count=$(jq -r '.approval_history | length' "$WORKFLOW_STATE")

    if [[ "$count" -eq 0 ]]; then
        echo "No approval history"
        return 0
    fi

    echo "Approval History (showing last $limit of $count):"
    echo ""

    jq -r --argjson limit "$limit" '.approval_history[-$limit:] | reverse | .[] |
        "  Task: \(.task_uuid)\n  Agent: \(.architect_agent)\n  Status: \(.status)\n  Approved: \(.approved_at)\n"' \
        "$WORKFLOW_STATE"
}

# ============================================================================
# Main Entry Point
# ============================================================================

if [[ $# -eq 0 ]]; then
    usage
fi

COMMAND="$1"
shift

case "$COMMAND" in
    add)
        cmd_add "$@"
        ;;
    check)
        cmd_check "$@"
        ;;
    approve)
        cmd_approve "$@"
        ;;
    list)
        cmd_list "$@"
        ;;
    history)
        cmd_history "$@"
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        error "Unknown command: $COMMAND. Use 'help' for usage."
        ;;
esac

exit 0
