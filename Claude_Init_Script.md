# Claude Init Script (Master Orchestration)

This document is the **master entrypoint** for launching Claude as an orchestrator of multiple subagents (UI, API, DB, QA, Docs) with **persistent context**, **resume-on-crash**, and **max-token** usage. It assumes the subagent templates from `Claude_Subagent_Prompts/` and the context directory structure below.

---

## 0) Goals
- Spin up Claude with **max tokens** and strict **context restore** on init.
- Register and launch all **subagents** with their own memory files.
- Persist **task history** and **last activity** to disk so a terminal crash can be resumed.
- Provide **CLI-style commands** and **JSON envelopes** for deterministic agent <> agent handoffs.

---

## 1) Expected Project Layout

```
/datagrub/promptforge
# project code with ui-tier/api-tier/data-tier

/datagrub/PromptForge_Build_Specs
# product spec for phase wise feature development of SaaS application

/datagrub/
  ├── Claude_Subagent_Prompts/               # subagent prompt templates (.md)
  │   ├── UI_Architect_Agent.md
  │   ├── API_Architect_Agent.md
  │   ├── DB_Architect_Agent.md
  │   ├── API_QA_Agent.md
  │   ├── UI_QA_Agent.md
  │   └── Doc_Context_Tracker_Agent.md
  ├── context/                               # persistent agent memory
  │   ├── ui_architect_context.json
  │   ├── api_architect_context.json
  │   ├── db_architect_context.json
  │   ├── apiqa_context.json
  │   ├── uiqa_context.json
  │   └── doc_context_tracker_context.json
  ├── logs/
  │   ├── orchestrator.log
  │   └── resume_checkpoint.log
  ├── orchestrator/
  │   ├── coordinator.yaml                   # high-level routing rules
  │   └── tasks/                             # reusable job specs (yaml/json)
  └── README.md
```

> If any `context/*.json` files are missing, create empty files `{}` before the first run.

---

## 2) Environment Variables

Create `.env` with:

```
CLAUDE_MODEL=claude-3-opus
CLAUDE_MAX_TOKENS=4000          # or your account max
CLAUDE_TEMPERATURE=0.2
CLAUDE_MEMORY_DIR=./context
CLAUDE_PROMPT_DIR=./Claude_Subagent_Prompts
ORCHESTRATOR_LOG=./logs/orchestrator.log
RESUME_LOG=./logs/resume_checkpoint.log
```

> Tip: If you have higher token limits (e.g., 200k), set `CLAUDE_MAX_TOKENS` accordingly.

---

## 3) Master System Prompt for Orchestrator

Copy this prompt into Claude (system message) **before** running any subagent:

```
You are the "Coordinator" for a multi-agent development workspace.

Objectives:
- Initialize subagents from prompt templates under CLAUDE_PROMPT_DIR.
- For each subagent, load or create its memory file under CLAUDE_MEMORY_DIR.
- Always run with max_tokens (CLAUDE_MAX_TOKENS). Use temperature 0.2.
- On startup, check RESUME_LOG. If an incomplete task is found, resume it automatically.
- After each subagent run, append a compact summary to its memory file and write a checkpoint to RESUME_LOG.
- If a terminal crash is detected (missing heartbeat), reload RESUME_LOG and continue from last checkpoint.

Subagents and memory files:
- UI Architect → ui_architect_context.json
- API Architect → api_architect_context.json
- DB Architect → db_architect_context.json
- API QA → apiqa_context.json
- UI QA → uiqa_context.json
- Doc Context Tracker → doc_context_tracker_context.json

Handoff contract (strict JSON):
- Input envelope to subagents:
  {
    "project_id": "string",
    "event": "pull_request|push|nightly|manual",
    "changed_files": ["path"],
    "spec_refs": ["string"],
    "artifacts": {"key":"url"},
    "task_uuid": "uuid",
    "resume": true|false
  }
- Output envelope from subagents:
  {
    "agent": "string",
    "status": "block|warn|ok",
    "summary": "string",
    "findings": [{"rule_id":"string","severity":"low|med|high|blocker","path":"string","line":int,"fix":"string"}],
    "artifacts": {"report":"url"},
    "next_actions": ["string"],
    "task_uuid": "uuid",
    "checkpoint": {"ts":"iso8601","cursor":"opaque"}
  }

Coordinator actions:
1) Route events to relevant subagents based on changed files and spec_refs.
2) Collect outputs and compute final verdict: block if any agent returns status=block.
3) Persist merged report to ORCHESTRATOR_LOG and write checkpoint to RESUME_LOG.
4) Provide a single, actionable summary (PR comment text) including next steps, links, and diffs.
```

---

## 4) Subagent Bootstrap Prompts

For each subagent, paste its `.md` content from `Claude_Subagent_Prompts/` into Claude as the **system message** when spawning that subagent. Then send a **JSON input envelope** (see above).

Example (UI Architect):
```
System = contents of UI_Architect_Agent.md
User (JSON Envelope) = {
  "project_id":"pf-001",
  "event":"pull_request",
  "changed_files":["frontend/mfe-traces/src/TraceList.tsx"],
  "spec_refs":["spec/ui.md#routing","spec/a11y.md#color-contrast"],
  "artifacts": {"diff":"<url>"},
  "task_uuid":"bd0a...",
  "resume": false
}
```

---

## 5) Resume-on-Crash Protocol

1. **Heartbeat**: The coordinator writes a heartbeat to `RESUME_LOG` every N minutes with the `task_uuid` and agent name.  
2. **Crash Detection**: If no heartbeat after 2×N period, assume crash.  
3. **Restore**: On next init, the coordinator reads `RESUME_LOG`, fetches the last `task_uuid`, agent, and input envelope, then re-sends it to the appropriate subagent.  
4. **Idempotence**: Subagents must be idempotent—if a task is re-run, they reconcile results instead of duplicating changes.

---

## 6) Example Coordinator YAML (Routing Rules)

```yaml
# orchestrator/coordinator.yaml
routes:
  docs:
    match: ["docs/", "prompts/"]
    agents: ["Doc Context Tracker"]
  ui:
    match: ["frontend/", "ui/", "mfe-"]
    agents: ["UI Architect", "UI QA", "SpecQA?"]
  api:
    match: ["backend/", "api/"]
    agents: ["API Architect", "API QA", "SpecQA?"]
  db:
    match: ["database/", "migrations/", "schema.sql"]
    agents: ["DB Architect", "API QA", "SpecQA?"]

policy:
  block_on: ["security-high","db-destructive","spec-violation"]
  warn_on: ["a11y-low","style"]
```

*(If you use SpecQA, add its prompt and memory file too.)*

---

## 7) CLI-style Commands (Manual)

- **Init all agents**  
  “Initialize all subagents; create empty memory files if missing; print summary of last activities.”

- **Resume last task**  
  “Read RESUME_LOG; resume the last incomplete task for the indicated agent.”

- **Run targeted check**  
  “Dispatch to API QA with this input envelope: { … } and return results JSON.”

- **Summary report**  
  “Summarize all agent findings for project pf-001 across the last 24 hours.”

---

## 8) Tips for Long Sessions

- Keep each subagent **max tokens** high (or account max) to retain full context.  
- After each run, the subagent **must** write a compact session summary to its memory JSON to minimize token usage next time.  
- Store large artifacts (diffs, screenshots) in object storage and only keep links in memory JSON.

---

## 9) Example Memory JSON Format

```json
{
  "agent": "UI Architect",
  "sessions": [
    {
      "task_uuid": "bd0a...",
      "ts": "2025-10-05T20:41:00Z",
      "inputs": {"changed_files":["frontend/..."]},
      "summary": "Refactored TraceList, fixed a11y color-contrast.",
      "artifacts": {"report":"s3://.../ui-20251005.json"},
      "next_actions": ["Refactor MFE shell routing"]
    }
  ],
  "last_checkpoint": {
    "task_uuid": "bd0a...",
    "cursor": "opaque",
    "ts": "2025-10-05T20:42:10Z"
  }
}
```

---

## 10) Success Criteria

- All subagents initialize, load memory, and **resume** if crash detected.  
- The orchestrator posts **one merged verdict** per event (PR, push, nightly).  
- Max tokens used consistently; summaries persisted after each run.  
- UI/API/DB/QA artifacts are accessible via links in outputs.  

---

**Version:** 1.0 • **Maintainer:** AI Systems Team • **License:** Apache 2.0
