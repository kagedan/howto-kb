---
id: "2026-06-01-hanakoxbt-httpstcor5icvbploa-01"
title: "@hanakoxbt: https://t.co/r5icVbPLoa"
url: "https://x.com/hanakoxbt/status/2061428221271286048"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "x"]
date_published: "2026-06-01"
date_collected: "2026-06-09"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/r5icVbPLoa


--- Article ---
One Claude session doing everything is like one employee who writes the code, reviews their own pull request, and pushes to production at 3am. Every engineering manager knows why that fails.

Boris Cherny does it differently. The creator of Claude Code runs hundreds of agents in parallel from his phone. Each one has a specific job. Each one feeds results to the next. He hasn't written a single line of code in 2026.

The architecture is not complicated. It is three agents with three separate claude-md files and one pipeline connecting them.

This article shows you the exact setup: one agent writes code, one reviews it, one deploys it. Code goes from idea to production with you as the oversight, not the bottleneck.

---

## Why One Agent Is Not Enough

When one agent writes and reviews its own code, it misses the same things a human would miss reviewing their own pull request. No second pair of eyes. No separation of concerns.

When you split across multiple agents, each one operates with a different system prompt and a different job. The writer optimizes for speed. The reviewer optimizes for correctness. The deployer optimizes for safety.

That separation is what turns a chatbot into a team.

![](https://pbs.twimg.com/media/HJpuJnhXYAQ07lI.jpg)

---

## The Architecture: Three Agents, Three Jobs

Each agent gets its own claude-md file with its own role, constraints, and workflow.

**Agent 1 - The Writer**

You are a code writer. Your only job is to implement features and fixes.

Write clean, readable code. Follow existing patterns in the codebase.

Never refactor code you were not asked to change.

Never write tests. That is not your job.

Do not review your own work. Another agent handles that.

The writer moves fast. It does not second-guess itself. It writes the implementation and moves on.

**Agent 2 - The Reviewer**

You are a code reviewer. Your only job is to find problems.

Read every diff carefully. Check for bugs, e
