---
id: "2026-07-21-claudedevs-httpstcorx3fqsosu0-01"
title: "@ClaudeDevs: https://t.co/rx3FQSosu0"
url: "https://x.com/ClaudeDevs/status/2079654423828304282"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "Python", "TypeScript", "x"]
date_published: "2026-07-21"
date_collected: "2026-07-22"
summary_by: "auto-x"
query: "@ClaudeDevs"
---

https://t.co/rx3FQSosu0


--- Article ---
Code migrations, projects that port a production codebase to a new language, were multi-year endeavors until recently.

In the last month, individual developers at Anthropic migrated 10 code packages consisting of tens to hundreds of thousands of lines of code using Claude Fable 5, Claude Opus 4.8, and[ dynamic workflows](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code).

Jarred Sumner (@jarredsumner), co-founder of Bun and Member of Technical Staff at Anthropic, used Claude Code to[ migrate Bun from Zig to Rust](https://bun.com/blog/bun-in-rust). A million lines of code were produced in less than two weeks, with 100% of Bun's existing test suite passing in CI before merge. Nineteen regressions surfaced after merge and have all been fixed. The Rust port was shipped inside Claude Code in June.

Mike Krieger (@mikeyk), co-lead of Anthropic Labs, migrated a Python codebase to 165,000 lines of TypeScript over a weekend. This included hundreds of agents, eight phase gates, three adversarial review rounds, and a final parity check that diffed every command's output against the Python original.

Claude Code's new capabilities change the math for these long-deferred projects. Below is the six-step process we now use, drawn from what these migrations taught us.

The core insight is that you don't fix the code. You fix the process (loop) that produced the code.

---

## **Why and when to migrate languages**

Teams launch migrations because of landscape changes between their initial build and current project. Either a known trade-off has become limiting, a better approach has emerged, or the original ecosystem is shrinking.

For example, Jarred originally chose Zig because it offered C-level performance with radical simplicity, ideal for a solo founder "writing Bun in 1 year in a cramped Oakland apartment pre-LLM." This simplicity came with known tradeoffs,[ which he writes about here](https://bun.com/blog/bun-in-r
