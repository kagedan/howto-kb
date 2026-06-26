---
id: "2026-06-26-ceoguy-i-gave-claude-code-one-prompt-and-didnt-tou-01"
title: "@CEOGuy: I gave Claude Code one prompt and didn't touch the keyboard"
url: "https://x.com/CEOGuy/status/2070306866471862546"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "AI-agent", "x"]
date_published: "2026-06-26"
date_collected: "2026-06-26"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

I gave Claude Code one prompt and didn't touch the keyboard again until the whole thing was built and QA'd.

It's a loop. You describe the goal once, it plans the phases, builds item by item, audits its own work, runs QA, and only comes back when it's actually done. No back-and-forth, no babysitting.

This is the sauce a solo founder uses to out-ship a whole team. Bookmark it.

Setup:
- Agent: Claude Code (Opus 4.8)
- Install: Obsidian + Obsidian Skills, Playwright MCP, Davia, Graphify, Claude in Chrome, Claude Preview, Figma, Notion, Vercel, superpowers, frontend-design, mempalace, taste-skill, skill, ai-seo, impeccable

The prompt:
```
/goal /loop /effort ultracode /workflow

{DESCRIBE IN FULL THE GOAL YOU WANT TO ACHIEVE}

That's the high level of what I'm trying to build. Analyze it, understand it,
and research it further so you can help me build a strong plan that's data and
value driven. Document everything in our local brain/wiki and on Notion. Here's
the master page to write in, create sub-pages as needed: {NOTION URL}.

Then do the following.

1. List every phase and every item needed to complete this goal in full, phase
   by phase, item by item. Audit the list, make improvements, repeat until the
   audit is clean and the list is finalized.

2. For each item, build a careful, strategic plan. Research and brainstorm hard
   first, be data and value driven. Write one plan at a time, not all at once.
   After each plan, audit it, improve it, repeat until the audit is clean.

3. Sort all phases and items by priority and the best order to reach the goal.

If at any point you hit a question or a decision: brainstorm hard, lay out the
best options, and pick the recommended one. You're fully authorized to decide on
auto mode without asking me.

For anything that needs a PRD (feature, product, UI/UX, flow, architecture):
first list all the PRDs needed, then write them one by one. After each PRD,
audit and improve, and loop until the audit is clean before the next
