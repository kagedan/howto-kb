---
id: "2026-06-22-dkare1009-most-teams-use-10-of-claude-code-the-res-01"
title: "@dkare1009: Most teams use 10% of Claude Code. The rest is where the re"
url: "https://x.com/dkare1009/status/2069200550684488140"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "AI-agent"]
date_published: "2026-06-22"
date_collected: "2026-06-23"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Most teams use 10% of Claude Code.

The rest is where the real control sits:

Claude Code is built around 5 layers.

Most people stay at the prompt layer.

That is why their setup feels powerful one day and messy the next.

1️⃣ CLAUDE.md

This is the rules layer.

Use it for:
→ Architecture rules the agent should follow every session
→ Naming conventions, test expectations, and repo maps
→ Global rules in ~/.claude/ and project rules in .claude/

Check:
↳ If you repeat the same instruction twice, it belongs in CLAUDE.md

2️⃣ Skills

This is the expertise layer.

Use it for:
→ SKILL.md files with task-specific instructions
→ Reusable workflows for testing, refactoring, writing, or documentation
→ Narrow knowledge the agent can call only when the task needs it

The risk:
↳ Loading everything upfront bloats the main context window
↳ Skills keep the work focused without making the session heavy

3️⃣ Hooks

This is the guardrail layer.

Hooks are event-driven shell commands.

Use them for:
→ Auto-lint after every Write
→ Block dangerous commands like rm -rf before they run
→ Run checks on PreToolUse, PostToolUse, SessionStart, Stop, and SubagentStop
→ Send a Slack ping when a session ends

Why it matters:
↳ You stop trusting the model to remember every rule
↳ Quality gets enforced by infrastructure

4️⃣ Subagents

This is the delegation layer.

Each subagent gets its own:
→ Context window, model, tools, and permissions

How it works:
↳ The main agent sends work down
↳ The subagent sends results back
↳ Subagents cannot spawn more subagents

That keeps the system easier to control.

5️⃣ Plugins

This is the team layer.

Use plugins for:
→ Bundling skills, subagents, hooks, and commands
→ Installing the same behavior across multiple projects
→ Giving the whole team one shared agent setup

Think npm packages, but for agent behavior.

Then the outer system connects everything.

🤖 MCP Servers connect Claude Code to GitHub, databases, APIs, and internal tools.

🧠 Agent Teams le
