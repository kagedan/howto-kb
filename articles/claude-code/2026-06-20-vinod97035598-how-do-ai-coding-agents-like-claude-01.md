---
id: "2026-06-20-vinod97035598-how-do-ai-coding-agents-like-claude-01"
title: "@vinod97035598: How do AI coding agents (like Claude Code and OpenAI Codex)"
url: "https://x.com/vinod97035598/status/2068129485904306390"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "LLM"]
date_published: "2026-06-20"
date_collected: "2026-06-20"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

How do AI coding agents (like Claude Code and OpenAI Codex) actually work? 🤖

The secret isn't just the model—it's the 𝗔𝗴𝗲𝗻𝘁 𝗟𝗼𝗼𝗽.

Contrary to popular belief, the model is not "running code" by itself. 
Instead, a host program, CLI, or IDE extension sits in a continuous loop: repeatedly asking the model what to do, executing approved tool calls, feeding the output back, and repeating until a final answer is reached.

An AI agent is built of 𝗧𝗵𝗿𝗲𝗲 𝗣𝗶𝗹𝗹𝗮𝗿𝘀:

𝟭. 𝗠𝗼𝗱𝗲𝗹: The reasoning engine (like Claude or GPT).
𝟮. 𝗛𝗮𝗿𝗻𝗲𝘀𝘀 / 𝗥𝘂𝗻𝘁𝗶𝗺𝗲: The coordinator that owns the loop, permissions, context compaction, state, subagents, and UI.
𝟯. 𝗧𝗼𝗼𝗹𝘀: The interface to the system (file I/O, terminal command shell, web search, and MCP tools).

How the two leading implementations stack up:

• 𝗖𝗼𝗱𝗲𝘅: Open-source CLI using Responses API. Configured via `AGENTS.md`. Employs sandbox boundaries + custom approval policies + auto-review.

• 𝗖𝗹𝗮𝘂𝗱𝗲 𝗖𝗼𝗱𝗲: CLI and Agent SDK. Configured via `CLAUDE.md`. Employs read-only defaults + manual permissions + lifecycle hooks + nested subagents.

🧠 𝗧𝗵𝗲 𝗠𝗲𝗻𝘁𝗮𝗹 𝗠𝗼𝗱𝗲𝗹:
Think of these agents as a senior-ish developer sitting inside a controlled workflow:

`Think -> Inspect -> Act -> Observe -> Adjust -> Verify -> Report`

The true magic is the 𝗛𝗮𝗿𝗻𝗲𝘀𝘀. It manages the context window, filters tools, enforces safety limits, and keeps the model grounded in actual repository feedback.

What are your thoughts on CLI-based coding agents? 👇

#AICoding #ClaudeCode #OpenAICodex #SoftwareEngineering #DevTools #GenerativeAI #CodingAgents #LLM #DeveloperProductivity
