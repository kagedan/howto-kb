---
id: "2026-05-27-r-alx-z-claude-code-workflow-thats-been-getting-me-01"
title: "@r_alx_z: claude code workflow that's been getting me through entire e"
url: "https://x.com/r_alx_z/status/2059430622503002289"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "x"]
date_published: "2026-05-27"
date_collected: "2026-05-27"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

claude code workflow that's been getting me through entire epics in a couple hours:

1. plan deeply. write short and long term docs to /plans in the project root and keep them updated (folders: future, active, complete). list review concerns up front: dry/dedupe, security, testing, error handling, perf, observability.

2. have the plan call /subagent-team. each subagent gets its own context window, so the parent session just coordinates merging in completed work.

3. /code-review at the end. it walks the diff hunting for bugs, dead code, missing tests, security holes, perf footguns. catches stuff missed during execution.

the planning is what makes it work. agents are only as good as the brief.

img inspo https://t.co/gwHsfhty8M
