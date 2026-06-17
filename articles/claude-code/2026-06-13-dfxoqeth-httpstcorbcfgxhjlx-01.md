---
id: "2026-06-13-dfxoqeth-httpstcorbcfgxhjlx-01"
title: "@DfxoqEth: https://t.co/rbcFGxhJLx"
url: "https://x.com/DfxoqEth/status/2065776570267054559"
source: "x"
category: "claude-code"
tags: ["MCP", "prompt-engineering", "AI-agent", "Python", "x"]
date_published: "2026-06-13"
date_collected: "2026-06-17"
summary_by: "auto-x"
query: ""Model Context Protocol" tutorial OR "Claude MCP" integration"
---

https://t.co/rbcFGxhJLx


--- Article ---
Almost everyone who tries to build an agent quits at step zero. They open a tutorial, see "tool calling" and "MCP servers" and "hooks" and "subagents," close the tab, and go back to pasting into the chat box

![](https://pbs.twimg.com/media/HKsUhNLXQAAAVyj.jpg)

That is the gap this guide closes. A first agent is not a pile of frameworks. It is nine small moves that turn one repetitive task into a process that runs without you. Each move is one hour. You do not need all nine on day one. You need step N+1

The spine of this is Anthropic's own playbook for building agents: start with the simplest thing that works, add machinery only when it pays for itself (@AnthropicAI, *Building Effective Agents*, Dec 2024). We follow that ladder

> **What you will build:** a desktop agent that reads incoming emails, drafts replies for the routine ones, and pings you in Slack for the ones it cannot handle. **Stack:** Python plus Claude Agent SDK plus one MCP server. **Models:** claude-haiku-4-5-20251001 for routing, claude-sonnet-4-6 for drafting

---

**Part 1. Foundation
**
Before tools and loops, get the boring part right. One task, one prompt, one clean output. Skip this and every later step inherits the mess

**01. Pick a task you actually do every day**

Do not build a generic "AI assistant." Pick one repetitive job you would pay someone $10 to take off your plate. Triage incoming emails. Tag invoices. Summarize standup notes. Move tickets between columns

The rule. If you cannot describe the task in one sentence, you are not ready to automate it. Agents amplify clarity. They also amplify confusion

**Use it when:** you are starting. Every other step depends on this one being narrow

**02. Solve it once by hand in the chat**

Open claude.ai. Solve the task manually with prompting alone. No code, no tools. Iterate the prompt until you get the right output three times in a row

This is your baseline. You are finding the exact wording tha
