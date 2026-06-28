---
id: "2026-06-28-archiveexplorer-httpstco7ckc4zjo4q-01"
title: "@ArchiveExplorer: https://t.co/7CKc4ZJO4q"
url: "https://x.com/ArchiveExplorer/status/2071192832455430283"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "AI-agent", "x"]
date_published: "2026-06-28"
date_collected: "2026-06-29"
summary_by: "auto-x"
query: ""Model Context Protocol" tutorial OR "Claude MCP" integration"
---

https://t.co/7CKc4ZJO4q


--- Article ---
**Most builders fight the loop. The loop is fine. The folder underneath isn't set up.**

Open *.claude/* in any working Claude Code project and you find roughly seven things doing the actual work: CLAUDE.md, settings.json, hooks/, agents/, skills/, .mcp.json, and a state file like MEMORY.md.

Most builders have opened one of those files. Maybe two. That is why their loops stall on the third iteration.

By the end of this article you will know what each file does, the five loop steps that ride on top, the three failure modes that kill most first attempts, and the single next file to add tonight.

No framework. No subscription. One walkthrough with exact paths and exact contents.

The harness is the floor. Pour it first.

# Two layers, one setup

The harness is the .claude/ folder. It does not change between runs.

The loop is what runs inside it: a goal, an action, a verification step, a memory write, and a decision to keep going or stop.

The harness is the kitchen. The loop is the recipe.

Both fail without the other. A kitchen with no recipe is unused space. A recipe with no kitchen is wishful thinking.

Most builders treat the whole thing as one blob ("my agent setup") and miss that failures live in different layers.

Token blowups, prompt fatigue, dropped permissions: harness problems. Loops that never converge, verifications that pass garbage, scheduled runs that drift: loop problems.

Naming the layer fixes the diagnosis. You stop rewriting prompts when the real bug is a missing permission.

I thought building the loop first would teach me which harness files I needed. It was the other way around.

The harness sets what each iteration is allowed to do. Permissions decide whether the loop can write to disk. Subagents decide whether verification runs in a clean context.

Skills decide whether the loop can specialize. Hooks decide whether the loop even gets to fire on the trigger you wanted.

Without those decisions locke
