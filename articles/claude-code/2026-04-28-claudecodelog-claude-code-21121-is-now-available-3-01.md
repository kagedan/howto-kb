---
id: "2026-04-28-claudecodelog-claude-code-21121-is-now-available-3-01"
title: "@ClaudeCodeLog: Claude Code 2.1.121 is now available. 39 CLI changes, 3 sys"
url: "https://x.com/ClaudeCodeLog/status/2048927542703280609"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "LLM", "x"]
date_published: "2026-04-28"
date_collected: "2026-04-28"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Claude Code 2.1.121 is now available.

39 CLI changes, 3 system prompt changes

Highlights:
• Added MCP server option alwaysLoad: when true, that server's tools skip search deferral and load immediately
• Bash tool drops shell state between runs and adds rerun-footer tokens, so commands don't share prior context
• PostToolUse hooks can replace output for all tools, letting hooks override tool results (was MCP-only)

Complete details in thread ↓

Claude Code CLI 2.1.121 changelog:

New features:
• Added alwaysLoad option to MCP server config — when true, all tools from that server skip tool-search deferral and are always available
• Added claude plugin prune to remove orphaned auto-installed plugin dependencies; plugin uninstall --prune cascades
• Added a type-to-filter search box to /skills so you can find a skill in long lists without scrolling
• OpenTelemetry: added stop_reason, gen_ai.response.finish_reasons, and user_system_prompt (gated behind OTEL_LOG_USER_PROMPTS) to LLM request spans

Fixes:
• Fixed unbounded memory growth (multi-GB RSS) when processing many images in a session
• Fixed /usage leaking up to ~2GB of memory on machines with large transcript histories
• Fixed memory leak when long-running tools fail to emit a clear progress event
• Fixed Bash tool becoming permanently unusable when the directory Claude was started in is deleted or moved mid-session
• Fixed --resume crashing on startup in external builds
• Fixed --resume failing on large sessions when a transcript line was corrupted by an unclean shutdown — the corrupt line is now skipped
• Fixed thinking.type.enabled is not supported error when using Bedrock application inference profile ARNs
• Fixed Microsoft 365 MCP OAuth failing with duplicate or unsupported prompt parameter
• Fixed scrollback duplication when pressing Ctrl+L or triggering a redraw in non-fullscreen mode on tmux, GNOME Terminal, Windows Terminal, and Konsole
• Fixed https://t.co/ldz5BaC3j0 MCP connectors silently disappearing
