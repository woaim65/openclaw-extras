---
name: session-startup
description: "Run session startup checklist and write marker when new session begins. Ensures SOUL.md, USER.md, memory files, and MEMORY.md are read before processing messages."
homepage: https://docs.openclaw.ai/automation/hooks#session-startup
metadata:
  {
    "openclaw": {
      "emoji": "🚀",
      "events": ["session:start", "command:new"],
      "requires": { "config": ["workspace.dir"] },
    },
  }
---

# Session Startup Hook

Ensures the agent reads critical workspace files before processing any messages in a new session.

## What It Does

When a new session starts (`session:start`) or `/new` command is issued (`command:new`):

1. **Reads startup files** (in order):
   - `SOUL.md` — agent identity
   - `USER.md` — human context
   - `memory/YYYY-MM-DD.md` — today's and yesterday's daily notes
   - `MEMORY.md` — long-term curated memory
   - `~/proactivity/session-state.md` — active task state

2. **Writes startup marker** to `~/.openclaw/workspace/.startup_marker`:
   ```
   LAST_STARTUP=<unix_timestamp>
   LAST_SESSION=<session_key>
   ```

3. **Sends confirmation** to user (optional, via `event.messages`)

## Why This Matters

Without this hook, the agent can "forget" to read memory files and make decisions without context. This hook enforces the startup checklist by writing a marker that the agent's AGENTS.md rules then check on every message.

## Events

- `session:start` — When a new session begins
- `command:new` — When `/new` command is issued

## Requirements

- Workspace directory must be configured (`workspace.dir`)
- Files must exist at standard paths within workspace
