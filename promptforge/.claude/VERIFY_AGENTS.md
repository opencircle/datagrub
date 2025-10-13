# Agent Verification Guide

**Version**: 1.0.0
**Created**: 2025-10-12
**Purpose**: Verify that the multi-agent orchestration system is working correctly

---

## Quick Verification

### Step 1: Check Hook Configuration

Verify hooks are registered in Claude Code:

```bash
# In VSCode with Claude Code, type:
/hooks
```

**Expected Output**:
```
PostToolUse hooks:
  - Matcher: Write|Edit
  - Command: .claude/hooks/post-tool-use.sh
```

If you don't see the hook listed, the configuration is not loaded properly.

---

### Step 2: Test Hook Execution (Script Validator)

**Create or edit a script file:**

```bash
# Edit the test script
vim /Users/rohitiyer/datagrub/promptforge/scripts/test_hook.sh
```

**Use Claude Code to edit:**
```
"Edit the file scripts/test_hook.sh and add a comment at the top saying 'Testing hooks'"
```

**What Should Happen**:
1. Claude Code executes the Write/Edit tool
2. PostToolUse hook triggers
3. `post-tool-use.sh` detects it's a script file
4. Script Validator agent is invoked via Task tool
5. You see a message in VSCode console: `🔍 Validating script: test_hook.sh`
6. Validation results appear in the conversation

**Expected Output in Conversation**:
```
Script Validator Results:
✅ Syntax: Valid
⚠️  Warning: Missing error handling for curl command
⚠️  Warning: No set -euo pipefail
```

---

### Step 3: Test API Architect Auto-Trigger

**Edit an API file:**

```
"Edit the file api-tier/app/api/v1/endpoints/playground.py and add a comment"
```

**What Should Happen**:
1. PostToolUse hook triggers
2. Hook detects `api-tier/*.py` file (API route)
3. API Architect agent is invoked
4. You see: `🏗️ Reviewing api-route: playground.py`
5. Architectural review results appear

**Expected Output**:
```
API Architect Review: ✅ OK
- REST best practices followed
- No security concerns detected
- No breaking changes
```

---

### Step 4: Test DB Architect Auto-Trigger

**Edit a migration file:**

```
"Edit api-tier/alembic/versions/n0p1q2r3s4t5_add_insight_comparisons_table.py and add a comment"
```

**What Should Happen**:
1. PostToolUse hook triggers
2. Hook detects migration file
3. DB Architect agent is invoked
4. You see: `🏗️ Reviewing db-migration: n0p1q2r3s4t5_add_insight_comparisons_table.py`
5. Migration review appears with mandatory API Architect consultation request

---

### Step 5: Test UI Architect Auto-Trigger

**Edit a UI component:**

```
"Create a simple test component in ui-tier/components/TestButton.tsx"
```

**What Should Happen**:
1. PostToolUse hook triggers
2. Hook detects UI component file
3. UI Architect agent is invoked
4. You see: `🏗️ Reviewing ui-component: TestButton.tsx`
5. UI review appears with mandatory UX Specialist consultation request

---

## Troubleshooting

### Issue 1: No Hook Output in VSCode Console

**Symptom**: Edit files but don't see any hook execution messages

**Diagnosis**:
1. Check if hooks are registered:
   ```
   /hooks
   ```

2. Check settings file:
   ```bash
   cat /Users/rohitiyer/datagrub/promptforge/.claude/settings.local.json | jq '.hooks'
   ```

3. Verify hook script is executable:
   ```bash
   ls -la /Users/rohitiyer/datagrub/promptforge/.claude/hooks/post-tool-use.sh
   # Should show: -rwxr-xr-x
   ```

**Solutions**:
- **If hooks not registered**: Restart VSCode to reload settings
- **If script not executable**: `chmod +x .claude/hooks/post-tool-use.sh`
- **If settings missing**: Verify `.claude/settings.local.json` has hooks configuration

---

### Issue 2: Hook Runs But No Agent Invocation

**Symptom**: See hook trigger message but no agent validation results

**Diagnosis**:
```bash
# Test hook manually
cd /Users/rohitiyer/datagrub/promptforge
echo '{"tool_name":"Write","parameters":{"file_path":"'$(pwd)'/scripts/test_hook.sh"}}' | .claude/hooks/post-tool-use.sh
```

**Expected Output**:
```json
{
  "type": "validation_triggered",
  "message": "🔍 Validating script: test_hook.sh",
  "task_uuid": "task-...",
  "agent": "script-validator",
  "file": ".../scripts/test_hook.sh",
  "validation_prompt": "..."
}
```

**Common Issues**:
1. **Missing jq**: Install with `brew install jq`
2. **Missing agent template**: Check `.claude/agents/04_validators/script-validator.md` exists
3. **Wrong file path pattern**: Hook only triggers for specific patterns

---

### Issue 3: Agent Invoked But No Validation Output

**Symptom**: See agent invocation message but validation results never appear

**Diagnosis**:
This means the Task tool was invoked but the agent didn't complete or return results.

**Possible Causes**:
1. **Agent template not found**: Check file exists at path specified in hook
2. **Context file missing**: Check `.claude/context/agents/` has required JSON files
3. **Build specs missing**: Check `.claude/specs/` directory has specification files
4. **Agent timeout**: Agent took too long (>2 minutes default)

**Solutions**:
```bash
# Verify all required files exist
ls -la .claude/agents/04_validators/script-validator.md
ls -la .claude/context/agents/validator.json
ls -la .claude/specs/02_phase2_core_features/apis/Phase2_APIs.md

# Check context file is valid JSON
cat .claude/context/agents/validator.json | jq .
```

---

### Issue 4: Hook Works Sometimes But Not Always

**Symptom**: Hook triggers inconsistently

**Diagnosis**:
Check the file path patterns in the hook script:

```bash
grep -A 5 "Check for script files" .claude/hooks/post-tool-use.sh
```

**File Pattern Matching**:
- Scripts: `scripts/**/*.{sh,py,js,ts}`
- READMEs: `**/{README,SETUP,GUIDE}*.md`
- API routes: `api-tier/routes/**/*.py` or `api-tier/endpoints/**/*.py`
- API services: `api-tier/services/**/*.py`
- API models: `api-tier/models/**/*.py`
- API schemas: `api-tier/schemas/**/*.py`
- DB models: `data-tier/models/**/*.py`
- DB migrations: `data-tier/migrations/**/*.py` or `alembic/versions/**/*.py`
- UI components: `ui-tier/components/**/*.{tsx,ts,jsx,js}`
- UI pages: `ui-tier/pages/**/*.{tsx,ts,jsx,js}`

**Note**: File must match one of these patterns exactly, including directory structure.

---

## Manual Agent Testing (Without Hooks)

If hooks aren't working, you can still test agents manually:

### Test Script Validator

```
"Invoke the Script Validator agent to validate scripts/test_hook.sh against build specs"
```

### Test API Architect

```
"Invoke the API Architect to review api-tier/app/api/v1/endpoints/playground.py for security and best practices"
```

### Test DB Architect

```
"Invoke the DB Architect to review the migration file api-tier/alembic/versions/n0p1q2r3s4t5_add_insight_comparisons_table.py"
```

### Test UI Architect

```
"Invoke the UI Architect to review ui-tier components for design system compliance"
```

### Test Checker Agent

```
"Invoke the Checker Agent to perform Post_Check validation on the recent API changes"
```

---

## Verification Checklist

Use this checklist to verify the system is fully operational:

### ✅ Configuration
- [ ] `.claude/settings.local.json` has `hooks` configuration
- [ ] `/hooks` command shows PostToolUse hook registered
- [ ] `.claude/hooks/post-tool-use.sh` is executable (`-rwxr-xr-x`)

### ✅ Agent Templates
- [ ] `.claude/agents/04_validators/script-validator.md` exists
- [ ] `.claude/agents/04_validators/readme-validator.md` exists
- [ ] `.claude/agents/01_architecture/API_Architect_Agent.md` exists
- [ ] `.claude/agents/01_architecture/DB_Architect_Agent.md` exists
- [ ] `.claude/agents/01_architecture/UI_Architect_Agent.md` exists

### ✅ Context Files
- [ ] `.claude/context/agents/validator.json` exists and valid
- [ ] `.claude/context/agents/api_architect.json` exists and valid
- [ ] `.claude/context/agents/db_architect.json` exists and valid
- [ ] `.claude/context/agents/ui_architect.json` exists and valid

### ✅ Build Specs
- [ ] `.claude/specs/` directory exists with specifications
- [ ] At least `Phase2_APIs.md` present for API validation

### ✅ Hook Execution
- [ ] Edit a script file → Script Validator triggers
- [ ] Edit a README file → README Validator triggers
- [ ] Edit API route → API Architect triggers
- [ ] Edit DB migration → DB Architect triggers
- [ ] Edit UI component → UI Architect triggers

### ✅ Agent Output
- [ ] Validation messages appear in conversation
- [ ] Agent provides findings/recommendations
- [ ] Context files are updated after validation

---

## Expected Behavior Summary

### Auto-Triggered Agents (5)

| Agent | Trigger Pattern | Visual Indicator | Output |
|-------|----------------|------------------|---------|
| Script Validator | `scripts/**/*.{sh,py,js,ts}` | 🔍 Validating script: ... | Syntax, security, spec compliance |
| README Validator | `**/{README,SETUP}*.md` | 🔍 Validating readme: ... | Command accuracy, paths, formatting |
| API Architect | `api-tier/**/*.py` | 🏗️ Reviewing api-route: ... | Security, best practices, breaking changes |
| DB Architect | `data-tier/**/*.py` | 🏗️ Reviewing db-migration: ... | Schema design, migration safety, API sync |
| UI Architect | `ui-tier/**/*.{tsx,ts}` | 🏗️ Reviewing ui-component: ... | Design system, accessibility, API compat |

### Manual Agents (7)

| Agent | Invocation | Use Case |
|-------|-----------|----------|
| UX Specialist | `"Invoke UX Specialist..."` | Design system, accessibility audit |
| API QA | `"Run API QA tests..."` | API endpoint testing |
| UI QA | `"Run UI QA tests..."` | Playwright E2E testing |
| Doc Context Tracker | `"Invoke Doc Tracker..."` | Documentation sync |
| Auth Token Generator | `"Generate auth token..."` | Testing authentication |
| Checker Agent | `"Invoke Checker..."` | Final quality gate |

---

## Debug Mode

For detailed hook execution information:

```bash
# Set debug environment variable
export CLAUDE_DEBUG=1

# Or run with debug flag
claude --debug
```

This will show:
- Hook trigger events
- Command execution
- Agent invocation
- Task tool calls
- Agent responses

---

## Getting Help

If agents still aren't working after following this guide:

1. **Check Recent Changes**: Review `.claude/hooks/post-tool-use.sh` for syntax errors
2. **Test Hook Manually**: Run the hook script directly with test input
3. **Check Logs**: Look for error messages in VSCode Developer Tools (Help → Toggle Developer Tools)
4. **Verify Permissions**: Ensure script has execute permissions
5. **Restart VSCode**: Sometimes settings need a reload

---

**Status**: System Ready
**Total Agents**: 12 (5 auto-triggered, 7 manual)
**Configuration**: Complete
**Documentation**: Up to date
