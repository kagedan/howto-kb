---
id: "2026-03-29-tut-ml-if-youre-learning-claude-code-follow-this-o-01"
title: "@tut_ml: If you’re learning Claude Code, follow this order. It saves"
url: "https://x.com/tut_ml/status/2038176640929501570"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "x"]
date_published: "2026-03-29"
date_collected: "2026-04-10"
summary_by: "auto-x"
query: ""Model Context Protocol" tutorial OR "Claude MCP" integration"
---

If you’re learning Claude Code, follow this order.

It saves you a lot of trial and error.

1/ Understand what Claude Code actually is

It’s not a chatbot. It’s a CLI that runs locally with:

→ Full file system access
→ Parallel agent execution
→ API integrations

No upload limits. No session expiry. You can run tasks for hours.

Plans:

→ Pro: $20/month
→ Max: $100–200/month

Pick based on how heavy your usage is.

2/ Install it properly

Mac/Linux: curl -fsSL https://t.co/ThHwGVBvsm | sh
Windows: irm https://t.co/0PnKuhEf9s | iex

VS Code:
→ Install extension
→ Click icon
→ Authenticate

Done.

Small but important: You’re already using ~15–20% of context before typing anything.

→ /context to check
→ /compact at ~50%

3/ Set up CLAUDE.md (this changes everything)

Claude does not remember across sessions. This file becomes its memory.

→ Project details
→ Commands
→ Coding style
→ Workflows

Run: /init

Then customize it.

Locations:

→ Global: ~/.claude/CLAUDE.md
→ Project: inside your repo

Keep the most important instructions at the top.

4/ Learn permission modes early

→ Ask First — safest, approves everything
→ Auto Edit — edits freely, asks for new files
→ Plan Only — read + plan, no changes
→ Full Bypass — full automation

Start safe. Move up as you gain trust.

Always run: /plan

before executing anything.

5/ Use the commands that matter daily

→ /plan — before building
→ /context — track usage
→ /compact — manage tokens
→ /rewind — undo
→ /clear — reset
→ /effort high — deeper reasoning
→ /loop — recurring tasks
→ /agents — parallel workflows

And one simple trick:

→ “Think harder” → better reasoning output

6/ Connect everything with the MCP

MCP = integration layer.

It connects Claude Code to:
→ GitHub
→ Notion
→ Slack
→ Jira
→ Postgres
→ Gmail
→ and more

Example:

claude mcp add --transport http notion https://t.co/zv9tdGIr90

Start with:
→ Context7
→ Playwright
→ Excalidraw
→ DeepWiki

That covers most real use cases.

Simple roadmap
Setup → CLAU
