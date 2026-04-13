---
id: "2026-04-13-imjoshchang-he-architecture-if-anyones-curious-glm-01"
title: "@imJoshChang: he architecture if anyone's curious: - GLM-5.1 as the LLM ($"
url: "https://x.com/imJoshChang/status/2043495213893914760"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "LLM", "Python", "x"]
date_published: "2026-04-13"
date_collected: "2026-04-13"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Wanted a reliable cron job for Claude Code. Didn't want to burn $200/mo Max tokens on it.

Wired up GLM-5.1 via https://t.co/BlBkNc989b. Added custom skills. Built a heartbeat scheduler. Hooked up a Telegram listener.

Looked up and realized I'd accidentally rebuilt OpenClaw.

he architecture if anyone's curious:
- GLM-5.1 as the LLM ($18/mo)
- Claude Code skills for each workflow
- Python heartbeat dispatcher on cron
- Telegram bot for notifications + replies
- Brave Search MCP for web access

All running on a $10 VPS + my laptop.
