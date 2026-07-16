---
id: "2026-07-16-claudedevs-claude-codes-code-review-now-has-effort-01"
title: "@ClaudeDevs: Claude Code's /code-review now has effort levels, with the r"
url: "https://x.com/ClaudeDevs/status/2077840057130692886"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "x"]
date_published: "2026-07-16"
date_collected: "2026-07-17"
summary_by: "auto-x"
query: "@ClaudeDevs"
---

Claude Code's /code-review now has effort levels, with the review rewritten at every one.

Low effort beats other code review tools on findings at a fraction of the token cost. High effort delivers significantly higher recall when you want to go deeper.

You pick the tradeoff. https://t.co/uT2K7jfXqQ

Previously, /code-review ran one fixed prompt no matter the effort. Now, each level gets a different review strategy. 

It picks up your session effort setting automatically, or you can pass a level explicitly (e.g. "/code-review high").

Low effort runs a single pass over the diff. It's fast and cheap enough to run before every push.

Medium effort reads the changed code in context, runs multiple finder passes from different angles, then verifies every finding before surfacing it.

High effort runs the finders and verifiers as subagents with fresh context, so they aren't anchored on the reasoning of the agent that just wrote the code.

X-high goes even further, sweeping for impacts to code outside of the change itself.

There's one more level above high: /code-review ultra. 

It spawns a fleet of reviewer agents and independently reproduces every finding.  The same severe-issue coverage as high, with far fewer false positives.

We run this on every PR at Anthropic.

https://t.co/NhIw6ayYXZ

Available in all Claude Code sessions. Update Claude Code and run /code-review on your next PR.
