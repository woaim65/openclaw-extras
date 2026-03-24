---
name: memory-daily-bootstrap
description: "Inject today's and yesterday's memory files into bootstrap context on agent:bootstrap"
homepage: https://docs.openclaw.ai/automation/hooks
metadata:
  openclaw:
    emoji: "📅"
    events: ["agent:bootstrap"]
    requires:
      config: ["workspace.dir"]
---

# Memory Daily Bootstrap Hook

Injects today's and yesterday's memory files into the bootstrap context during `agent:bootstrap`.

This ensures the agent always has recent memory content in context from the first message, without requiring explicit memory reads.

## Events

- `agent:bootstrap`: Fires before bootstrap files are injected; hook adds memory files to `context.bootstrapFiles`.
