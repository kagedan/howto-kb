---
id: "2026-07-04-paulsolt-httpstcoiasgza0xcp-01"
title: "@PaulSolt: https://t.co/IasgZA0xCp"
url: "https://x.com/PaulSolt/status/2073470146115490230"
source: "x"
category: "claude-code"
tags: ["prompt-engineering", "AI-agent", "x"]
date_published: "2026-07-04"
date_collected: "2026-07-05"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

https://t.co/IasgZA0xCp

My current draft, which you can try as a prompt to help your agents focus, is here.

Ask an agent to apply it, so you can test-drive the process. Ask it to clarify anything about your setup.

---
This workflow gives coding agents an operating model inside a real software project.

Instead of asking one agent to “fix the bug” and hoping it understands the repo, you use manager threads, focused worker threads, QA proof, code review, CI, and project memory.

The goal is to turn AI from a code generator into a managed engineering team.

## The Core Idea

Use separate agent threads for separate responsibilities.

- **Human Owner**: decides priorities, approves merges, and makes product calls.
- **Manager Thread**: coordinates the work, delegates, checks progress, reviews evidence, and keeps threads from getting stuck.
- **Worker Thread**: implements one focused change.
- **QA Thread**: proves behavior at the app/system boundary.
- **Reviewer/CI**: catches code issues, test failures, regressions, and missing proof.
- **Learnings File**: captures hard-won lessons so future agents do not repeat mistakes.

The manager thread is the key. It acts like a chief of staff for the project.

It does not just ask “is the code done?” It asks:

- Is the branch correct?
- Is the task scoped?
- Did the worker start from the right commit?
- Are tests focused and meaningful?
- Is there app-level proof where needed?
- Did code review happen?
- Are CI failures resolved?
- Is the PR actually ready to merge?
- Is any worker stuck, stale, or frozen?

## Recommended Files

Keep this simple.

Start with one file:

- `AI_ENGINEERING_WORKFLOW.md`

If the project grows, split into:

- `AGENTS.md`
Permanent rules for coding agents in this repository.

- `docs/LEARNINGS.md`
Durable lessons from bugs, regressions, failed reviews, bad tests, and workflow mistakes.

- `docs/CORE_BEHAVIORS.md`
Optional. Product behavior that must not regress.

Use whatever planning system already
