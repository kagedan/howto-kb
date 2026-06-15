---
id: "2026-06-15-corevicellc-claude-code-added-a-fork-command-june-01"
title: "@CoreviceLLC: Claude Code added a /fork command (June 13). Branch a sessio"
url: "https://x.com/CoreviceLLC/status/2066318555046703431"
source: "x"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "x"]
date_published: "2026-06-15"
date_collected: "2026-06-15"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Claude Code added a /fork command (June 13). Branch a session into a parallel copy, A/B two implementation approaches against the same context, and keep the better one. Paired with nested subagents, the model is: branch to explore alternatives, delegate sub-tasks, merge the best result.

Parallel exploration just became table-stakes in the raw tool. But forking is only half the story. The hard question is who decides which branch survives, and what stops a branch from reaching main.

Codens runs the branches across model lanes, not one session. Claude via the raw Anthropic API, self-hosted Qwen, and Cursor Composer race the same task. Swapping the model is changing one alias, and every product picks it up.

A branch isn't kept on vibes. Each runs through a verify chain (implement -> test -> fix, up to 3 retries), and what lands on main is decided by a per-workflow merge mode: human-gated PR-only by default, or auto-merge. Per-workflow budget caps keep parallel branches from blowing the bill.

Branching is the new baseline. The value moves to deciding which branch is safe to keep, through verification, gating, and cost control.

https://t.co/KZ8nrqutz6

https://t.co/zvNd4HPuaB
