# Pre-User-Response Approval Checklist

**Purpose**: Enforce mandatory Checker Agent approval before presenting architect agent results to user.

**Policy Reference**: `CLAUDE_ORCHESTRATOR.md:73-90` - MANDATORY CHECKER APPROVAL POLICY

---

## Before Presenting Architect Agent Results to User

Verify all checkpoints before user-facing response:

### ✅ Phase 1: Task Completion
- [ ] **Architect Agent Completed**: Task status = "completed"
- [ ] **Files Modified**: List of modified files documented
- [ ] **Build Specs Validated**: Relevant Phase 1/2/3 specs checked
- [ ] **Agent Context Updated**: Architect agent context file updated with task details

### ✅ Phase 2: Approval Checkpoint
- [ ] **Checkpoint Added**: Execute `./claude/scripts/workflow-manager.sh add <task_uuid> <architect_agent>`
- [ ] **Checkpoint Verified**: Confirm checkpoint appears in `workflow_state.json`
- [ ] **Status**: Verify status = "awaiting_checker_approval"

### ✅ Phase 3: Checker Invocation
- [ ] **Checker Agent Invoked**: "Invoke Checker Agent to perform Post_Check validation of <architect_agent>'s work on <task_description>"
- [ ] **Quality Gates Executed**: All 6 quality gates validated
  - Specification Alignment (BLOCK if not met)
  - Regression Prevention (BLOCK if failed)
  - Error Pattern Avoidance (WARNING/BLOCK if critical)
  - Test Coverage (BLOCK if <80% unit, missing integration)
  - Documentation (WARNING if incomplete)
  - Cross-Agent Consistency (BLOCK if mismatched)
- [ ] **Approval Status Received**: APPROVED, PASS_WITH_WARNINGS, or BLOCKED

### ✅ Phase 4: Status Handling

#### If Status = BLOCKED 🚫
- [ ] **Present Findings**: Share Checker findings with architect agent
- [ ] **Require Fixes**: Address critical issues identified
- [ ] **Re-submit to Checker**: Invoke Checker again after fixes
- [ ] **Loop Until Approved**: Repeat until status = APPROVED or PASS_WITH_WARNINGS

#### If Status = APPROVED ✅ or PASS_WITH_WARNINGS ⚠️
- [ ] **Update Workflow State**: Execute `./claude/scripts/workflow-manager.sh approve <task_uuid> <status>`
- [ ] **Verify Approval Recorded**: Confirm appears in approval_history
- [ ] **Prepare Checker Badge**: Format approval badge for user response

### ✅ Phase 5: User Response
- [ ] **Include Checker Badge**: Add approval badge to response
- [ ] **Link to Report**: If available, link to `.claude/reports/CHK-*.json`
- [ ] **Summarize Findings**: Include key Checker findings (warnings, recommendations)
- [ ] **Present Results**: Now safe to present architect agent results to user

---

## Checker Badge Format

### APPROVED Status (✅)
```markdown
**Checker Agent Validation**: ✅ APPROVED (96% confidence)
- All 6 quality gates passed
- No issues found
- Implementation ready for use
```

### PASS_WITH_WARNINGS Status (⚠️)
```markdown
**Checker Agent Validation**: ⚠️ PASS_WITH_WARNINGS (94% confidence)
- 5/6 quality gates passed
- Minor warnings:
  - Documentation: Add JSDoc comments to component props
  - Test Coverage: Consider adding edge case tests
- Implementation approved with recommendations

📄 [Full Report](.claude/reports/CHK-2025-10-11-001.json)
```

### BLOCKED Status (🚫)
```markdown
**Checker Agent Validation**: 🚫 BLOCKED
- Critical issues detected:
  - Specification Alignment: Component doesn't match Phase2_UI_Framework.md design system
  - Regression Prevention: 3 existing tests now failing
- Addressing issues before presenting results...

⏳ Status: Fixing issues and re-submitting to Checker Agent
```

---

## Quick Reference Commands

### Add Checkpoint
```bash
./claude/scripts/workflow-manager.sh add <task_uuid> <architect_agent>
```

### Check Status
```bash
./claude/scripts/workflow-manager.sh check <task_uuid>
# Returns: approved | awaiting_checker_approval | APPROVED | PASS_WITH_WARNINGS | BLOCKED
```

### Approve Checkpoint
```bash
./claude/scripts/workflow-manager.sh approve <task_uuid> <status>
# status = APPROVED | PASS_WITH_WARNINGS | BLOCKED
```

### List Pending Approvals
```bash
./claude/scripts/workflow-manager.sh list
```

### View Approval History
```bash
./claude/scripts/workflow-manager.sh history 10
```

---

## Workflow Example

### Scenario: UI Architect Implements EvaluationSelector Component

**Step 1: Architect Completes**
```
UI Architect Agent: "Implemented EvaluationSelector in ui-tier/shared/components/EvaluationSelector.tsx"
```

**Step 2: Add Checkpoint**
```bash
./claude/scripts/workflow-manager.sh add task-eval-selector-001 UI_Architect_Agent
# Output: ✅ Added approval checkpoint for task-eval-selector-001 (UI_Architect_Agent)
```

**Step 3: Invoke Checker**
```
"Invoke Checker Agent to perform Post_Check validation of UI Architect's EvaluationSelector component implementation against Phase2_UI_Framework.md"
```

**Step 4: Checker Returns Status**
```json
{
  "review_id": "CHK-2025-10-11-001",
  "status": "PASS_WITH_WARNINGS",
  "confidence": 0.94,
  "quality_gates_passed": 5,
  "quality_gates_warnings": 1
}
```

**Step 5: Approve**
```bash
./claude/scripts/workflow-manager.sh approve task-eval-selector-001 PASS_WITH_WARNINGS
# Output: ⚠️  Approved task-eval-selector-001 with status: PASS_WITH_WARNINGS
```

**Step 6: Present to User**
```markdown
✅ EvaluationSelector component implemented successfully!

**Checker Agent Validation**: ⚠️ PASS_WITH_WARNINGS (94% confidence)
- 5/6 quality gates passed
- Minor warning: Add JSDoc comments for better documentation
- Component ready for integration

**Files Modified**:
- ui-tier/shared/components/EvaluationSelector.tsx (200 lines)

**Build Specs**: Phase2_UI_Framework.md (Design System compliance confirmed)
```

---

## Common Pitfalls to Avoid

### ❌ DON'T: Skip Checker Approval
```markdown
# BAD - Presenting results without Checker approval
"I've implemented the component. Here are the files..."
```

### ✅ DO: Always Invoke Checker First
```markdown
# GOOD - Add checkpoint and invoke Checker
1. Add checkpoint: workflow-manager.sh add task-123 UI_Architect_Agent
2. Invoke Checker Agent for validation
3. Wait for approval
4. Present results with Checker badge
```

### ❌ DON'T: Present BLOCKED Results to User
```markdown
# BAD - User sees blocked implementation
"Checker Agent found issues but here's what I built..."
```

### ✅ DO: Fix Issues Before User Presentation
```markdown
# GOOD - Address blocking issues first
"Checker Agent identified critical issues. Fixing now...
[After fixes] Re-submitted to Checker. Status: APPROVED. Here are the results..."
```

### ❌ DON'T: Forget to Update Workflow State
```markdown
# BAD - Checker approves but state not updated
Checker: "APPROVED"
[Immediately present to user without workflow-manager.sh approve]
```

### ✅ DO: Record All Approvals
```markdown
# GOOD - Update state before presenting
Checker: "APPROVED"
workflow-manager.sh approve task-123 APPROVED
[Now present to user with badge]
```

---

## Integration with Existing Agents

### UI Architect Agent
After implementation completes:
1. Add checkpoint for UI_Architect_Agent
2. Invoke Checker with Phase1_CoreUI.md + Phase2_UI_Framework.md context
3. Wait for UX/accessibility/design system validation
4. Record approval and present

### API Architect Agent
After implementation completes:
1. Add checkpoint for API_Architect_Agent
2. Invoke Checker with Phase2_APIs.md + Phase2_API_SecurityRequirements.md context
3. Wait for security/performance/OpenAPI validation
4. Record approval and present

### DB Architect Agent
After implementation completes:
1. Add checkpoint for DB_Architect_Agent
2. Invoke Checker with Phase2_APIs.md database section context
3. Wait for schema/migration/indexing validation
4. Record approval and present

### UX Specialist Agent
After design review completes:
1. Add checkpoint for UX_Specialist_Agent
2. Invoke Checker with WCAG AAA + Design System validation
3. Wait for accessibility/design consistency validation
4. Record approval and present

---

## Metrics to Track

### Approval Coverage
- **Target**: 100% of architect implementations receive Checker approval
- **Current**: Track via `workflow_state.json` approval_history length
- **Formula**: (approved_tasks / total_architect_tasks) × 100

### Approval Response Time
- **Target**: <2 minutes from checkpoint to approval
- **Measure**: timestamp difference between checkpoint add and approve commands

### Blocked Rate
- **Target**: <10% of implementations blocked
- **Measure**: (BLOCKED approvals / total approvals) × 100
- **Action**: If >10%, review quality gates for false positives

### Repeat Issues
- **Target**: 0 repeat error patterns
- **Measure**: Track via `checker_context.json` error_patterns occurrences
- **Action**: If occurrences >1, update subagent templates with prevention guidance

---

## Troubleshooting

### Problem: Checkpoint Not Found
```bash
ERROR: Checkpoint not found for task_uuid: task-123. Use 'add' command first.
```
**Solution**: Execute `workflow-manager.sh add <task_uuid> <architect_agent>` before checking or approving

### Problem: Checker Agent Not Responding
**Symptoms**: Invoked Checker but no response after 5 minutes
**Solution**:
1. Check if Task tool completed: Look for "Task completed" message
2. Review Checker context: `cat .claude/context/checker_context.json`
3. Re-invoke Checker with explicit build specs: "Invoke Checker Agent with Phase2_APIs.md context"

### Problem: Workflow State File Corrupted
```bash
ERROR: jq parse error
```
**Solution**:
1. Backup current file: `cp workflow_state.json workflow_state.json.bak`
2. Re-initialize: Delete file and run `workflow-manager.sh list` to auto-create
3. Manually restore approval_history from backup if needed

---

**Version**: 1.0
**Last Updated**: 2025-10-11
**Next Review**: After 10 approvals (evaluate workflow efficiency)
