---
id: "2026-06-21-oludelehal36103-when-youre-building-a-project-that-01"
title: "@OludeleHal36103: When you're building a project that starts getting big, lett"
url: "https://x.com/OludeleHal36103/status/2068499971146420412"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "AI-agent", "LLM", "x"]
date_published: "2026-06-21"
date_collected: "2026-06-21"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

When you're building a project that starts getting big, letting an AI just code without guardrails completely breaks.

I experienced this scaling Vectorless (the engine for vectorless rag). I had the core engine, SDKs, MCPs, and docs all moving at once. It gets messy fast. https://t.co/BToWVTs9l7

Before this, I would plan things out in standard LLM chats. Ideas would pop up, I'd throw them in, some got executed, some didn't.

And the AI never fully followed the PLAN.md files it generated anyway. Tracking them across folders is just mentally exhausting.

So I stopped doing that. I wanted systems that scale and take my workflow to another level of productivity.

I designed a system connecting the tools we already have:
- Linear (Central Brain)
- Claude Code (Local Execution via MCP)
- GitHub (PR Reviews)

First: Planning. I configured my local claude.md file with strict rules.

Claude is forbidden from keeping plan state locally. It must query Linear to seed initiatives, create projects, establish milestone timelines, and break features down into tight, unmissable tickets. https://t.co/FjR2x0nXSJ

Next: Git Hygiene.

When AI makes changes to a lot of files, it loves to lump them under one messy "shotgun commit."

I force sequential commits. Changes for a specific feature are grouped logically step-by-step with clean explanations, keeping test suites and benchmarks isolated

And code reviews? Even as a solo dev, you cannot push directly to main.

Every PR goes through our review agents (Sourcery, CodeRabbit, Jules). They do line-by-line security checks and map out sequence diagrams so we can visually verify that flows are correct.
