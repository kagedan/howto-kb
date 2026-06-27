---
id: "2026-06-27-stretchcloud-the-hidden-cost-in-coding-agents-isnt-01"
title: "@stretchcloud: The hidden cost in coding agents isn't the reasoning. It's t"
url: "https://x.com/stretchcloud/status/2070668433339891861"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "Gemini", "x"]
date_published: "2026-06-27"
date_collected: "2026-06-27"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

The hidden cost in coding agents isn't the reasoning. It's the logs.

This is the pattern I keep noticing in how coding agent costs actually break down: the expensive part isn't the model doing clever things. It's the model reading its own noise back.

Rohit built RTK after finding ~80% of his coding-agent token spend was going to something he never audited: the agent re-reading its own command output. Every cargo test failure, every git diff, every build log lands in context at full token cost. A 30-minute Claude Code session burns roughly 118k tokens on that alone.

RTK is a Rust binary that intercepts those commands before they reach the context window. It applies four compression strategies: filtering boilerplate, grouping similar items, truncating repeated noise, deduplicating log lines. Single binary. Zero dependencies. 100+ supported commands. git push drops from 15 lines to one. cargo test failure goes from 200 lines to 20.

The broader situation across the category: context bloat is not a model problem, it's a tooling problem. Every DevOps team learned to filter log verbosity before it hit their dashboards. The agent context window is now that destination. Teams that curate what lands in it will have a real cost advantage.

RTK integrates with Claude Code, Cursor, Copilot, Gemini CLI, Windsurf, and Cline via transparent hook rewrites. No workflow changes needed.

My read: the bottleneck in coding agent economics isn't intelligence per token. It's what you're spending tokens on.

https://t.co/KFZWl6Vs5b


--- 引用元 @rohit4verse ---
This CLI proxy reduced my LLM token consumption by 60-90%.

For months I blamed the model for my coding-agent bill. 

~80% of those tokens went to something I never audited: the agent re-reading its own command output.

Every test log and git diff lands in context at full token cost. A 30-minute Claude Code session burns ~118k tokens on it.

rtk is one Rust binary that filters that output before it hits the window. 

git push drops
