---
id: "2026-03-30-aakashgupta-andrej-karpathy-said-it-himself-the-hi-01"
title: "@aakashgupta: Andrej Karpathy said it himself. The hierarchy for connectin"
url: "https://x.com/aakashgupta/status/2038723705237631414"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "x"]
date_published: "2026-03-30"
date_collected: "2026-03-31"
summary_by: "auto-x"
---

Andrej Karpathy said it himself. The hierarchy for connecting tools to Claude Code: CLI at the top, API in the middle, MCP at the bottom.

MCPs eat context the moment they connect. Every MCP you load is sitting in your context window doing nothing until you call it. You could have five MCPs connected and lose 15-20% of your usable context before you've typed a single message.

CLIs use zero context until the moment you need them. The GitHub CLI, Vercel CLI, Firecrawl CLI. The AI calls them direc
