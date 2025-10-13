# Checker Agent Auto-Invocation Strategy

**Version**: 1.0.0
**Created**: 2025-10-11
**Status**: Implementation Ready

---

## Problem Statement

The MANDATORY Checker approval policy requires explicit invocation after architect work, but this is currently manual and easy to forget. This creates a gap where architect outputs could be presented to users without quality validation.

**Current Flow** (Manual):
```
User Request → Invoke Architect → Architect Work → User Manually Invokes Checker → Present Results
                                                    ↑
                                        Easy to forget, inconsistent
```

**Desired Flow** (Automatic):
```
User Request → Invoke Architect → Architect Work → AUTO-INVOKE Checker → Present Results with Badge
                                                    ↑
                                        Automatic, enforced, consistent
```

---

## Solution Design

### Core Principle: Orchestrator-Level Enforcement

Rather than relying on hooks or external scripts, the **main Claude orchestrator** will detect architect work and automatically invoke the Checker Agent before presenting results to the user.

### Detection Mechanism

**Trigger Conditions** (ANY of these):
1. **Explicit Architect Invocation**: User command contains "Invoke [UI|API|DB|UX] Architect"
2. **Architect Task Tool Use**: Task tool invoked with architect agent template
3. **Architect File Modifications**: Edit/Write to architect-managed files (ui-tier/, api-tier/, data-tier/)

### Workflow Phases

#### Phase 1: Architect Work Detection
```
When orchestrator receives architect invocation:
1. Parse user command/task
2. Identify architect agent type (UI, API, DB, UX)
3. Generate task_uuid
4. Add approval checkpoint: workflow-manager.sh add <task_uuid> <architect>
```

#### Phase 2: Architect Work Execution
```
1. Execute architect agent task
2. Collect architect output
3. DO NOT present to user yet
```

#### Phase 3: Automatic Checker Invocation
```
1. Invoke Checker Agent with Post_Check command
2. Pass architect output, changed files, relevant specs
3. Wait for Checker approval status
```

#### Phase 4: Status Handling
```
IF status == BLOCKED:
  - Present Checker findings to architect agent
  - Request fixes
  - Loop back to Phase 2

IF status == APPROVED or PASS_WITH_WARNINGS:
  - Record approval: workflow-manager.sh approve <task_uuid> <status>
  - Proceed to Phase 5
```

#### Phase 5: Present to User with Badge
```
Format response with Checker validation badge:

**Checker Agent Validation**: ✅ APPROVED (96% confidence)
- All 6 quality gates passed
- No regressions detected
- Specification compliance: 100%

[Architect Output]
```

---

## Implementation Components

### Component 1: Architect Work Detector

**Location**: Orchestrator logic (main Claude session)

**Pseudocode**:
```python
def detect_architect_work(user_command: str, tool_uses: list) -> dict:
    """
    Detect if architect work is being performed.

    Returns: {
        "is_architect_work": bool,
        "architect_type": "UI_Architect|API_Architect|DB_Architect|UX_Specialist",
        "task_description": str,
        "changed_files": list,
        "relevant_specs": list
    }
    """
    # Check for explicit invocation
    architect_patterns = [
        r"Invoke (UI|API|DB) Architect",
        r"Have (UX Specialist|UI Architect|API Architect|DB Architect)",
        r"(UI|API|DB|UX) Architect: "
    ]

    for pattern in architect_patterns:
        match = re.search(pattern, user_command, re.IGNORECASE)
        if match:
            return {
                "is_architect_work": True,
                "architect_type": normalize_architect_name(match.group(1)),
                "task_description": extract_task_description(user_command),
                "changed_files": [],  # Will be populated after work
                "relevant_specs": []   # Will be determined by agent
            }

    # Check for Task tool with architect agent
    for tool_use in tool_uses:
        if tool_use["tool"] == "Task":
            prompt = tool_use["parameters"]["prompt"]
            if any(agent in prompt for agent in ARCHITECT_AGENTS):
                return {
                    "is_architect_work": True,
                    "architect_type": extract_architect_from_prompt(prompt),
                    ...
                }

    return {"is_architect_work": False}
```

### Component 2: Approval Checkpoint Manager

**Location**: Orchestrator logic

**Pseudocode**:
```python
def add_approval_checkpoint(architect_type: str, task_description: str) -> str:
    """
    Add approval checkpoint to workflow state.

    Returns: task_uuid
    """
    task_uuid = generate_task_uuid()

    # Execute workflow-manager.sh
    result = bash_command(
        f".claude/scripts/workflow-manager.sh add {task_uuid} {architect_type}"
    )

    # Log checkpoint creation
    log_to_context(f"Approval checkpoint created: {task_uuid}")

    return task_uuid
```

### Component 3: Checker Auto-Invoker

**Location**: Orchestrator logic

**Pseudocode**:
```python
def auto_invoke_checker(task_uuid: str, architect_type: str, architect_output: dict) -> dict:
    """
    Automatically invoke Checker Agent for validation.

    Returns: {
        "status": "APPROVED|PASS_WITH_WARNINGS|BLOCKED",
        "confidence": float,
        "review_notes": str,
        "action_items": list,
        "regressions_detected": bool
    }
    """
    # Build Checker invocation prompt
    checker_prompt = f"""
You are the Checker Agent performing Post_Check validation.

**Task UUID**: {task_uuid}
**Architect Agent**: {architect_type}
**Task Description**: {architect_output['task_description']}

**Changed Files**:
{format_changed_files(architect_output['changed_files'])}

**Architect Output**:
{architect_output['summary']}

**Relevant Specifications**:
{architect_output['relevant_specs']}

**VALIDATION REQUIREMENTS**:
1. Run all 6 quality gates (see Checker_Agent.md)
2. Check for regressions against checker_context.json
3. Validate specification compliance
4. If MFE changes detected: Invoke API QA Agent for MFE-specific tests
5. Return approval status with confidence score

**Output Format** (JSON):
{{
  "agent_name": "{architect_type}",
  "status": "APPROVED|PASS_WITH_WARNINGS|BLOCKED",
  "confidence": 0.0-1.0,
  "review_notes": "...",
  "action_items": [...],
  "regressions_detected": bool,
  "quality_gates": {{
    "specification_alignment": "PASS|FAIL",
    "regression_prevention": "PASS|FAIL",
    "error_pattern_avoidance": "PASS|WARN|FAIL",
    "test_coverage": "PASS|FAIL",
    "documentation": "PASS|WARN",
    "mfe_api_integration": "PASS|FAIL|SKIPPED"
  }}
}}

Begin Post_Check validation now.
"""

    # Invoke Checker Agent using Task tool
    checker_result = invoke_task_tool(
        description="Checker validation",
        prompt=checker_prompt,
        subagent_type="general-purpose"
    )

    # Parse Checker response
    approval_data = parse_checker_response(checker_result)

    return approval_data
```

### Component 4: Approval Status Handler

**Location**: Orchestrator logic

**Pseudocode**:
```python
def handle_checker_status(task_uuid: str, approval_data: dict, architect_output: dict) -> dict:
    """
    Handle Checker approval status and determine next action.

    Returns: {
        "should_present_to_user": bool,
        "response_text": str,
        "requires_fixes": bool,
        "fix_recommendations": list
    }
    """
    status = approval_data["status"]

    if status == "BLOCKED":
        # Do NOT present to user, request fixes
        return {
            "should_present_to_user": False,
            "response_text": format_blocked_message(approval_data),
            "requires_fixes": True,
            "fix_recommendations": approval_data["action_items"]
        }

    elif status in ["APPROVED", "PASS_WITH_WARNINGS"]:
        # Record approval in workflow state
        bash_command(
            f".claude/scripts/workflow-manager.sh approve {task_uuid} {status}"
        )

        # Format user-facing response with Checker badge
        response = format_approved_response(
            architect_output=architect_output,
            checker_approval=approval_data
        )

        return {
            "should_present_to_user": True,
            "response_text": response,
            "requires_fixes": False,
            "fix_recommendations": []
        }
```

### Component 5: Response Formatter

**Location**: Orchestrator logic

**Pseudocode**:
```python
def format_approved_response(architect_output: dict, checker_approval: dict) -> str:
    """
    Format final response with Checker validation badge.
    """
    status_emoji = {
        "APPROVED": "✅",
        "PASS_WITH_WARNINGS": "⚠️"
    }

    emoji = status_emoji[checker_approval["status"]]
    confidence_pct = int(checker_approval["confidence"] * 100)

    # Build Checker badge
    badge = f"""
**Checker Agent Validation**: {emoji} {checker_approval["status"]} ({confidence_pct}% confidence)
- Quality Gates: {count_passed_gates(checker_approval["quality_gates"])}/6 passed
- Regressions: {"None detected" if not checker_approval["regressions_detected"] else "Detected"}
- Specification Compliance: {checker_approval["spec_compliance_rate"]}%
"""

    if checker_approval["status"] == "PASS_WITH_WARNINGS":
        badge += f"\n**Warnings**:\n"
        for warning in checker_approval.get("warnings", []):
            badge += f"  - {warning}\n"

    # Combine badge with architect output
    response = f"{badge}\n\n---\n\n{architect_output['summary']}"

    return response
```

---

## Orchestrator Behavior Changes

### Before Implementation

```
User: "Invoke UI Architect to create ProjectCard component"
    ↓
Orchestrator:
1. Invoke UI Architect
2. UI Architect completes work
3. Present results to user immediately
```

**Problem**: No quality validation, no Checker approval

### After Implementation

```
User: "Invoke UI Architect to create ProjectCard component"
    ↓
Orchestrator:
1. Detect architect work (UI_Architect)
2. Generate task_uuid: "task-abc-123"
3. Add approval checkpoint: workflow-manager.sh add task-abc-123 UI_Architect_Agent
4. Invoke UI Architect
5. UI Architect completes work
6. Auto-invoke Checker Agent with Post_Check
7. Checker returns: APPROVED (96% confidence)
8. Record approval: workflow-manager.sh approve task-abc-123 APPROVED
9. Present results to user with Checker badge
```

**Result**: Automatic quality validation, enforced approval gate

---

## Edge Cases & Handling

### Edge Case 1: Checker Returns BLOCKED

**Scenario**: Checker finds critical issues

**Handling**:
```
1. Orchestrator receives BLOCKED status
2. Present Checker findings to USER (not architect)
3. Ask user: "Checker found critical issues. Options:"
   a. Review issues and manually fix
   b. Have architect agent address issues automatically
   c. Override Checker (requires explicit user confirmation)
4. If user chooses (b):
   - Pass Checker findings to architect
   - Architect makes fixes
   - Loop back to Checker validation
```

### Edge Case 2: Multiple Architects Involved

**Scenario**: Task requires UI Architect AND API Architect

**Handling**:
```
1. Create separate approval checkpoints for each:
   - task-abc-123-ui → UI_Architect_Agent
   - task-abc-123-api → API_Architect_Agent
2. Invoke each Checker validation separately
3. Both must pass before presenting to user
4. Combine Checker badges in final response
```

### Edge Case 3: User Bypasses Architect, Edits Files Directly

**Scenario**: User uses Edit tool to modify ui-tier/components/Button.tsx directly

**Handling**:
```
Option A: Don't auto-invoke Checker (user knows what they're doing)
Option B: Suggest Checker review:
  "I see you modified Button.tsx. Would you like me to invoke Checker Agent to validate this change?"

Recommended: Option B (suggest but don't force)
```

### Edge Case 4: Checker Agent Unavailable/Fails

**Scenario**: Checker Agent fails to respond or returns error

**Handling**:
```
1. Log error to checker_context.json
2. Present to user with warning:
   "⚠️ Checker Agent validation failed. Presenting unvalidated output."
3. Recommend manual review
4. Do NOT block user progress
```

---

## Testing Plan

### Test Case 1: Basic Flow
```
User: "Invoke UI Architect to create Button component"
Expected:
1. Approval checkpoint created
2. UI Architect invoked
3. Checker auto-invoked
4. Response includes Checker badge
```

### Test Case 2: Blocked Status
```
User: "Invoke API Architect to add DELETE endpoint"
Setup: Checker detects missing permission check
Expected:
1. Checker returns BLOCKED
2. User sees findings, not endpoint implementation
3. No approval recorded
```

### Test Case 3: Multiple Architects
```
User: "Invoke UI Architect and API Architect to build project form"
Expected:
1. Two approval checkpoints created
2. Both architects complete work
3. Both Checker validations run
4. Final response includes both badges
```

### Test Case 4: MFE Changes
```
User: "Invoke UI Architect to modify mfe-playground"
Expected:
1. Checker detects MFE change
2. Checker invokes API QA Agent for MFE tests
3. API QA runs: pytest tests/mfe_playground/ -v
4. Checker approval contingent on test results
```

---

## Implementation Checklist

- [ ] Add architect work detection logic to orchestrator
- [ ] Implement approval checkpoint creation
- [ ] Create Checker auto-invocation function
- [ ] Implement status handling (APPROVED/BLOCKED/PASS_WITH_WARNINGS)
- [ ] Create response formatter with Checker badge
- [ ] Update orchestrator rules in .claude/CLAUDE.md
- [ ] Test basic flow with UI Architect
- [ ] Test BLOCKED status handling
- [ ] Test MFE changes (Checker → API QA integration)
- [ ] Document new behavior in CLAUDE.md
- [ ] Create user-facing examples

---

## Migration Strategy

### Phase 1: Soft Rollout (Suggested)
- Implement auto-invocation
- Add user prompt: "Invoke Checker automatically? (Y/n)"
- Default: Yes
- Allow users to opt-out if needed

### Phase 2: Hard Enforcement (Recommended)
- Remove opt-out option
- Enforce MANDATORY approval policy automatically
- Block user-facing responses until Checker approval

### Phase 3: Optimization
- Track metrics: approval time, blocked rate, confidence scores
- Optimize Checker Agent prompts based on patterns
- Add pre-emptive warnings (Pre_Check before architect work)

---

## Success Metrics

Track effectiveness of auto-invocation:

1. **Coverage Rate**: % of architect work with Checker validation
   - **Target**: 100%

2. **Blocked Rate**: % of architect outputs blocked by Checker
   - **Baseline**: Unknown
   - **Target**: <10% (with continuous improvement)

3. **Average Approval Time**: Time from architect completion to Checker approval
   - **Target**: <30 seconds

4. **False Positive Rate**: % of BLOCKED that user overrides
   - **Target**: <5%

5. **Regression Detection Rate**: % of regressions caught by Checker
   - **Target**: >95%

---

## Rollback Plan

If auto-invocation causes issues:

1. **Immediate**: Set environment variable `DISABLE_AUTO_CHECKER=true`
2. **Temporary**: Revert to manual invocation model
3. **Analysis**: Review logs to identify failure pattern
4. **Fix**: Address root cause
5. **Re-enable**: Deploy fixed version

---

## Documentation Updates Required

1. `.claude/CLAUDE.md`:
   - Update "Orchestration Rules" section
   - Add "Automatic Checker Invocation" section
   - Update usage examples

2. `.claude/agents/README.md`:
   - Update Checker Agent section
   - Document auto-invocation behavior

3. `.claude/agents/02_quality/Checker_Agent.md`:
   - Add "Auto-Invocation Protocol" section

4. User-facing examples:
   - Show Checker badge in response examples
   - Document what happens when BLOCKED

---

## Next Steps

1. ✅ Design complete (this document)
2. ⏭️ Implement detection logic in orchestrator
3. ⏭️ Test with sample architect invocations
4. ⏭️ Update documentation
5. ⏭️ Deploy and monitor

---

**Status**: Ready for implementation
**Approval Required**: User confirmation to proceed
