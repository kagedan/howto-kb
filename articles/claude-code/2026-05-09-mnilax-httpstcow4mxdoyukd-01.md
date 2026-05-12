---
id: "2026-05-09-mnilax-httpstcow4mxdoyukd-01"
title: "@Mnilax: https://t.co/W4MxdOyUKD"
url: "https://x.com/Mnilax/status/2053116311132155938"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "AI-agent", "x"]
date_published: "2026-05-09"
date_collected: "2026-05-12"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/W4MxdOyUKD


--- Article ---
In late January 2026, Andrej Karpathy posted a thread complaining about how Claude writes code. Three failure modes: silent wrong assumptions, over-complication, orthogonal damage to code it shouldn't have touched.

Forrest Chang read the thread, packaged the complaints into 4 behavioral rules in a single CLAUDE.md file, and dropped it on GitHub. **It hit 5,828 stars in the first day. 60,000 bookmarks in two weeks. 120,000 stars today.** The fastest-growing single-file repo of 2026.

![](https://pbs.twimg.com/media/HH4cAobXQAcrmek.jpg)

Then I tested it on 30 codebases over 6 weeks.

The 4 rules work. Mistakes that used to happen ~40% of the time dropped to under 3% on tasks that played to their strengths. But the template was built to fix code-writing mistakes from January.

The Claude Code ecosystem in May 2026 has different problems — agent fights, hook cascades, skill loading conflicts, multi-step workflows that break across sessions.

So I added 8 more rules. Below: t**he full 12-rule CLAUDE.md, why each one earned its place, and the 4 places where the original Karpathy template silently breaks.**

If you want to skip the explanations and just paste,** the full file is at the end.**

# Why this matters

Claude Code's CLAUDE.md is the most under-leveraged file in the entire AI coding stack. Most developers either:

- Treat it as a dump for every preference they've ever had, bloated to 4,000+ tokens, compliance drops to 30%
- Skip it entirely and prompt every time — 5x token waste, no consistency between sessions
- Copy a template once and forget. Works for two weeks, then breaks silently as their codebase shifts
The official Anthropic docs are explicit: **CLAUDE.md is advisory. Claude follows it about 80% of the time. Past 200 lines, compliance drops sharply because important rules get buried in the noise.**

Karpathy's template solved this in one file, 65 lines, 4 rules. That's the floor.

The ceiling is higher. With 8
