---
id: "2026-07-06-vandos-httpstcogs2k8d95mb-01"
title: "@__vandos__: https://t.co/Gs2k8d95mB"
url: "https://x.com/__vandos__/status/2074232828313620586"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "x"]
date_published: "2026-07-06"
date_collected: "2026-07-07"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

https://t.co/Gs2k8d95mB


--- Article ---
There's a shift happening in how people work with AI coding agents. The most productive users aren't prompting anymore — they're designing loops. Boris Cherny, who created Claude Code, put it simply: "I don't prompt Claude anymore. I create loops — and the loops do the work. My job is to create loops."

This guide covers the complete spectrum: from turn-based manual loops to fully autonomous schedules that run while you sleep. We'll cover when to use each pattern, how to manage token usage, and the emerging best practices from the community.

## What Makes a Loop a Loop?

On the Claude Code team, loops are defined as agents repeating cycles of work until a stop condition is met.  The shape of a perfect loop follows a pattern: **timer outside, condition inside, skill innermost.** /loop re-arms it on a schedule, /goal defines verified-done so it can't stop early, and the skill does the work well.

```plaintext
/loop 30m /goal all PR review comments resolved via /review, stop after 10 turns
```

Every prompt you send already starts a manual loop — you direct each turn, Claude gathers context, takes action, checks its work, repeats if needed, and responds. The progression is about handing off more of that control.

## The Loop Types

1. Turn-Based Loops (Your Default)

**Triggered by:** A user prompt.
**Stop criteria:** Claude judges it has completed the task or needs additional context.
**Best used for:** Shorter tasks not part of a regular process.

Every prompt you send starts a manual loop. You direct each turn, Claude gathers context, takes action, checks its work, repeats if needed, and responds. This is the baseline.

**The upgrade:** Improve verification by encoding your manual steps as a SKILL.md so Claude can check more of its own work end-to-end. Include tools or connectors to let Claude see, measure, or interact with the result. The more quantitative the checks, the easier it is for Claude to self-verify.

![](https:
