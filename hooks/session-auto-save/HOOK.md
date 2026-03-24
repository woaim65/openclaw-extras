---
name: session-auto-save
description: "Automatically save session context to memory periodically (every 15 minutes), capturing silence periods without explicit /new or /reset"
homepage: https://docs.openclaw.ai/automation/hooks
metadata:
  openclaw:
    emoji: "💾"
    events: ["gateway:startup"]
    requires:
      config: ["workspace.dir"]
    install:
      - id: "bundled"
        kind: "bundled"
        label: "Custom (qiqi)"
---

# Session Auto-Save Hook

Periodically saves session context to memory at 15-minute intervals, plus on each incoming message (debounced).

## What It Does

1. **On gateway startup**: Starts a 15-minute periodic timer
2. **On each message received**: Saves session context (debounced to once per minute)
3. **Output**: Writes to `<workspace>/memory/autosave/YYYY-MM-DD-HH:MM.md`

## Why This Exists

The built-in `session-memory` hook only saves on `/new` or `/reset`. This hook captures insights from silence periods — when you step away or when there's a long gap between interactions.

## Events

- `gateway:startup`: Start the periodic save timer
- `message:received`: Capture incoming message and save context
