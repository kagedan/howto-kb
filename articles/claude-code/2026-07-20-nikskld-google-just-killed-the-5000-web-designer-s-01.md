---
id: "2026-07-20-nikskld-google-just-killed-the-5000-web-designer-s-01"
title: "@nikskld: GOOGLE JUST KILLED THE $5,000 WEB DESIGNER. Stitch + Claude"
url: "https://x.com/nikskld/status/2079308107683938431"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "Gemini"]
date_published: "2026-07-20"
date_collected: "2026-07-21"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

GOOGLE JUST KILLED THE $5,000 WEB DESIGNER.

Stitch + Claude Code via MCP just automated the entire design-to-code pipeline.

Design and code are now split between two specialists:

•Stitch (Gemini 3) generates the full multi-page design: layouts, colors, typography, DESIGN.md with every token
•Claude Code pulls it through MCP and turns it into production code
•No screenshots, no “make it look like this” prompts. Claude reads the exact hex values instead of guessing them

Setup is one command:

claude mcp add stitch –transport http –header “X-Goog-Api-Key: YOUR_KEY” https://t.co/31SfWlAlIP

Google also shipped 7 free agent skills for this workflow (google-labs-code/stitch-skills). Devs report idea → deployed app in ~23 minutes.

And Stitch is 100% free right now: 350 generations/month, no credit card. Paid tiers expected by end of 2026 — this window closes.

Old way: pay an agency, wait 3 weeks, get 2 revisions.
New way: one tool owns the design, one owns the logic, MCP translates.

I put my full Claude Code setup here 👇


--- 引用元 @nikskld ---
https://t.co/2xMvsRUlx0
