---
id: "2026-07-01-claudecodelog-claude-code-21198-has-been-released-01"
title: "@ClaudeCodeLog: Claude Code 2.1.198 has been released. 32 CLI changes High"
url: "https://x.com/ClaudeCodeLog/status/2072425697629343845"
source: "x"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "x"]
date_published: "2026-07-01"
date_collected: "2026-07-02"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Claude Code 2.1.198 has been released.

32 CLI changes

Highlights:
• Claude in Chrome is generally available, offering direct browser access to sessions and agents with no install
• Background agents auto-commit, push, and open draft PRs in worktree after finishing code, automating delivery
• Docs now advise grep for searches and clarify head_limit/unlimited/offset semantics to reduce surprises

Complete details in thread ↓

Claude Code CLI 2.1.198 changelog:

New features:
• Added background agent notifications in claude agents — sessions that need input or finish now fire the Notification hook (agent_needs_input / agent_completed)
• Added /dataviz skill for chart and dashboard design guidance with a runnable color-palette validator
• Gateway: added Claude Platform on AWS (anthropicAws) as an upstream provider; model-not-found responses now advance the failover chain

Fixes:
• Fixed brief network drops mid-response aborting the turn — transient errors like ECONNRESET now retry with backoff instead of failing
• Fixed excessive background classifier requests when sandboxed processes repeatedly accessed the same network host
• Fixed background tasks in web, desktop, and VS Code task panels getting stuck on "Running" after they finish or after resuming a session
• Fixed agent teams: a teammate that dies on an API error now reports "failed" to the lead, and messaging a stuck teammate wakes it to retry immediately
• Fixed the /diff panel not refreshing when you switch branches or commit outside the session
• Fixed markdown tables overflowing and wrapping their right border when rendered in fullscreen mode
• Fixed Claude Platform on AWS and Mantle sessions dead-ending with "Please run /login" when the STS token expires — awsAuthRefresh now runs automatically
• Fixed "no route to host" for local-network hosts in macOS background agent sessions by declaring Local Network entitlements
• Fixed /desktop failing with "Cannot determine working directory" after entering and exit
