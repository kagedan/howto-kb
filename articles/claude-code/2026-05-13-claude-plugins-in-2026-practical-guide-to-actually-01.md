---
id: "2026-05-13-claude-plugins-in-2026-practical-guide-to-actually-01"
title: "Claude Plugins in 2026: Practical Guide to Actually Useful Extensions"
url: "https://zenn.dev/neotechpark/articles/3a806ff8364664"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "AI-agent"]
date_published: "2026-05-13"
date_collected: "2026-05-14"
summary_by: "auto-rss"
query: ""
---

So you've been using Claude Code for a while. You know the basics type a task, watch it write code, maybe cringe a little when it does something unexpected. That's fine. But there's a whole layer underneath that most people skip: the plugin system.

This article breaks down what Claude Code plugins actually are, how each piece fits together, and which ones are worth installing right now. No fluff, just the stuff that works.

## Why Plugins Even Matter

Here's the honest version: Claude Code without plugins is already good. You can write code, fix bugs, run terminal commands, manage git, all through natural language. But there's a ceiling.

Without plugins, you end up doing a lot of copy-pasting. The same 200-word prompt for every code review. The same workflow explained from scratch every session. The same context that Claude forgets the moment the session ends.

Plugins kill that repetition. One colleague's demo where he asked Claude to pull a week of unread emails, find anything with a deadline, draft replies, and add calendar blocks was apparently enough to convince even the most skeptical developers. That's what this ecosystem enables when it clicks.

## The Four Building Blocks

Before jumping to what to install, you need to understand what's actually inside a plugin. Because "plugin" is a container, what matters is what it bundles.

![](https://static.zenn.studio/user-upload/6b4d597c795f-20260513.png)

### 1. Skills: the instruction layer

Skills are markdown files (`SKILL.md`) that teach Claude a repeatable workflow. Think of them like macros. Instead of typing the same long prompt every single time you want a code review, you write a `SKILL.md` once and call `/code-review` forever.

What makes skills interesting is auto-invocation. If a skill's description matches the current task context, Claude loads and follows it without you explicitly calling it. You mention "testing the login flow" and Claude quietly activates the Playwright skill in the background.

```
.claude/skills/
└── code-review/
    └── SKILL.md
```

![](https://static.zenn.studio/user-upload/f74ed2665b4c-20260513.png)

The content of `SKILL.md` is just markdown, instructions written for the model. Clear, specific, and focused on one workflow.

### 2. Agents (Subagents): the parallel workers

Subagents are isolated Claude sessions that the main agent can spin up for specific tasks. Each gets its own context window, tools, and permissions. The parent Claude coordinates; the subagents do the actual work in parallel.

Where this gets practical: a checkout page refactor can run four agents at once, backend logic, frontend components, test writing, and code review instead of doing it sequentially in one bloated context.

> Note: subagents do not inherit the parent's skills. You have to preload them explicitly in the agent's YAML config.

### 3. Hooks: the enforcement layer

Hooks are scripts that fire automatically at lifecycle events inside Claude Code. Unlike everything else, hooks are deterministic. they cannot hallucinate.

![](https://static.zenn.studio/user-upload/16715b53dca6-20260513.png)

Real examples of what hooks actually do in practice:

* Block `rm -rf` before it runs
* Auto-run linting after every file edit
* Inject project context at session start
* Run tests before Claude considers a task complete
* Log every tool call for audit trails

There are 25 lifecycle points where hooks can fire. The ones most people use day-to-day: `PreToolUse`, `PostToolUse`, `SessionStart`, and `Stop`.

### 4. MCP Servers: the connection layer

MCP (Model Context Protocol) is what lets Claude actually touch the outside world. Without it, Claude is limited to whatever's in the context window. With it, Claude can query your Postgres database, create GitHub PRs, post to Slack, and call any API using real live data instead of guessing.

Think of it as USB-C for AI. One standard protocol, and thousands of connectors already exist for it. The same MCP server works across Claude Code, Cursor, and other AI tools. it's portable in a way that plugins aren't.

```
# Add an MCP server via CLI
claude mcp add --transport http github https://mcp.github.com/mcp \
  --header "Authorization: Bearer $GITHUB_TOKEN"
```

![](https://static.zenn.studio/user-upload/dc7db8b56f5b-20260513.png)

Once added, you don't need to invoke it by name. Just ask: "Get the recent bug reports from the auth module" Claude picks the right tool.

## How a Plugin Bundles All of This

A plugin is just a folder with a manifest and components:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json       ← required manifest
├── skills/
│   └── code-review/
│       └── SKILL.md
├── agents/
│   └── reviewer.yaml
├── hooks/
│   └── pre-commit.sh
├── .mcp.json              ← optional MCP config
└── README.md
```

![](https://static.zenn.studio/user-upload/88326af5bcd0-20260513.png)

When you install a plugin, all of this becomes available immediately. Skills appear in autocomplete. Agents show up in `/agents`. Hooks start firing. MCP servers register their tools. One install, everything wired up.

The rule from the Nimbalyst guide puts it well: build an MCP server when the integration adds tools any client could use. Build a plugin when the integration is specific to your Claude Code workflow.

## Where Plugins Come From

There are three trust levels, and this matters when deciding what to install.

**Anthropic official marketplace** (`claude-plugins-official`) is pre-configured inside Claude Code. As of early 2026 it has 101 plugins 33 built by Anthropic directly (language servers, dev workflow tools, output styles) and 68 from verified partners like GitHub, Playwright, Supabase, Figma, Vercel, Linear, Sentry, Stripe.

**Community marketplaces** are GitHub repos with a `marketplace.json`. Quality varies a lot. Always read the manifest and source before installing anything that includes hooks or MCP servers those execute code on your machine.

To browse and install:

```
/plugin          ← open plugin manager
/plugin install code-review@claude-plugins-official
/plugin marketplace add owner/repo   ← add a community source
```

## Plugins Worth Installing Right Now

These are the ones consistently mentioned by people who actually use Claude Code daily, based on community feedback through early 2026.

### For development workflow

**`code-review@claude-plugins-official`**  
Five parallel Sonnet agents for automated PR review checks CLAUDE.md compliance, detects bugs, pulls historical context, scans PR history, and posts comments. Confidence-based scoring filters the false positives.

```
/plugin install code-review@claude-plugins-official
# Then: /code-review
```

**`feature-dev@claude-plugins-official`**  
Guided feature development through three agents: code-explorer (understands the codebase), code-architect (designs the approach), code-reviewer (quality check). One report said it eliminated four unnecessary database tables before a single line of code was written.

**`security-guidance@claude-plugins-official`**  
OWASP guidelines and secure coding patterns baked in as skills. Claude pulls them automatically when working on auth, API design, or anything involving user data.

**`security-sweep` (community)**  
More aggressive than `security-guidance` actively scans your codebase against OWASP Top 10 (2025), Mobile Top 10, and LLM Top 10. Checks for hardcoded secrets, injection flaws, auth issues, and AI-specific vulnerabilities.

**`connect-apps` (ComposioHQ)**  
Lets Claude send emails, create issues, post to Slack, update databases, and take real actions across 500+ services. Auth is handled by Composio. This is the "Claude does things, not just talks" plugin.

```
git clone https://github.com/composiohq/awesome-claude-plugins.git
cd awesome-claude-plugins
claude --plugin-dir ./connect-apps
```

**Linear plugin (`linear@claude-plugins-official`)**  
Pull tickets, update status, break tasks into subtasks all without leaving your coding session. Ask Claude to summarize your current sprint tickets and it just does it.

### For long-running autonomous work

**`ralph-loop@claude-plugins-official`**  
Named after the Simpsons character, this implements a stop-hook pattern that lets Claude keep working across multiple tasks without losing context. It's the "leave it running overnight" plugin. Claude resets its context between tasks to avoid bloat, then picks up the next one automatically.

### For memory across sessions

**`claude-mem` (community)**  
Adds persistent memory so Claude remembers your codebase structure, preferences, and ongoing project context across sessions. Uses SQLite and vector embeddings for search. Without something like this, you're re-briefing Claude at the start of every session.

## The Security Bit You Can't Skip

This part is short but important.

Plugins that include hooks or MCP servers execute code on your machine. A malicious skill in a community marketplace could run a keylogger, exfiltrate data, or do things you didn't ask for. This actually happened with the ClawHub marketplace (for OpenClaw) about 12% of the registry was compromised at one point with credential stealers and clipboard hijackers.

Claude Code's `claude-plugins-official` marketplace requires review and security standards. Community repos don't have the same guarantee.

Before installing anything outside the official marketplace:

* Read the `plugin.json` manifest
* Check what's in `hooks/` those scripts run automatically
* Look at the `.mcp.json` that's what external services Claude can reach
* Verify the repo has real activity and a real author

The `ecc-agentshield` tool (from the Claude Code Hackathon) can scan your Claude Code config for vulnerabilities, misconfigurations, and injection risks:

---

## Quick Reference: What to Use When

| You want to... | Use |
| --- | --- |
| Automate a repeated prompt | **Skill** |
| Run tasks in parallel | **Subagent / Agent Team** |
| Enforce rules automatically | **Hook** |
| Connect to external APIs / databases | **MCP Server** |
| Share a workflow with your team | **Plugin** (bundles all of the above) |

## Getting Started in 5 Minutes

If you want to just try this and see what it feels like:

```
# 1. Open Claude Code
# 2. Browse what's available
/plugin

# 3. Install something from official marketplace
/plugin install code-review@claude-plugins-official
/plugin install security-guidance@claude-plugins-official

# 4. Use it
/code-review
```

![](https://static.zenn.studio/user-upload/80cb010da047-20260513.png)

For MCP, start with GitHub if you're doing any dev work:

```
claude mcp add --transport http github https://mcp.github.com/mcp \
  --header "Auth![](https://static.zenn.studio/user-upload/80cb010da047-20260513.png)orization: Bearer $GITHUB_TOKEN"
```

![](https://static.zenn.studio/user-upload/f9b4e447bd16-20260513.png)

Then just ask: "What issues are open in the repo right now?" Claude will use it automatically.

## Final Thought

The plugin system isn't about doing something completely new. It's about stopping the repetition. Skills kill the copy-paste. MCP kills the hallucinated data. Hooks kill the "I forgot to run tests" problem. Agents kill the sequential bottleneck.

You don't need to install everything. Pick one workflow that you repeat constantly, find or write a skill for it, and see if it actually helps. Most people who try this end up going much deeper pretty quickly.
