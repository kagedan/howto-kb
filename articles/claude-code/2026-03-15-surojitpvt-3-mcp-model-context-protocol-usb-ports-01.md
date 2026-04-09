---
id: "2026-03-15-surojitpvt-3-mcp-model-context-protocol-usb-ports-01"
title: "@surojitpvt: 3/ MCP (Model Context Protocol) : USB ports for Claude. by"
url: "https://x.com/surojitpvt/status/2033280991629099060"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "Python"]
date_published: "2026-03-15"
date_collected: "2026-04-09"
summary_by: "auto-x"
---

I spent 2 weeks confused about MCP vs Claude API vs Claude Code vs Agent SDK.

but guess what turns out they're all connected. 

Here's the 2-minute map I wish I had 燥ｧｵ https://t.co/JbTLsiyvSW

1/ Think of Claude API as the engine at the center.

Everything else MCP, Claude Code, Agent SDK either builds on top of it or plugs into it.

Learn the API first. The rest becomes obvious. https://t.co/sZjFKSpNKf

2/ Claude API: start here.

you send a message over HTTP you get a response back

That's it. That's the whole thing.

竊? go to https://t.co/oTDh2PtAYs
竊? pick python or JS
竊? run the Hello World example

You'll be up in 5 minutes.

core idea: send messages, get content back. https://t.co/NkfoXybd0Q

3/ MCP (Model Context Protocol) : USB ports for Claude.

by default Claude only knows what you type, MCP lets Claude fetch data itself your files, Gmail, Slack, databases.

instead of copy-pasting context into every prompt, you plug in a server and Claude just knows

easiest start: use an existing MCP server before building your own.

will post a full tutorial on this soon!!

4/ Claude Code: a senior dev in your terminal.

It reads your codebase, writes code, runs commands, and fixes bugs. All from `$ claude`.

Step 1 竊? grab a free API key at https://t.co/hc5EjuYQYu
Step 2 竊? npm install -g @anthropic-ai/claude-code
Step 3 竊? navigate to any project, type `claude`

That's it. Ask it anything about your code.

note - free API key: the key itself is free to generate, but API usage is pay-per-token. First $5 of credits is free when you sign up, which is plenty to test Claude Code properly.

5/ Claude Agent SDK: come here last.

This is for building autonomous agents. You give Claude one goal. It figures out the steps, loops through tools, manages memory, and hands you the result.

it's just structured scaffolding around the API, once the API clicks, the SDK feels natural.

6/ The learning order that actually works:

&gt; Claude API : understand the core
&gt; Claude Code : build
