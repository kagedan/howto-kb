---
id: "2026-06-08-lcseekers-i-stopped-writing-50-prompts-by-hand-one-01"
title: "@LCSeekers: I stopped writing 50 prompts by hand. One workflow does what"
url: "https://x.com/LCSeekers/status/2063787909115715892"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "JavaScript", "x"]
date_published: "2026-06-08"
date_collected: "2026-06-08"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

I stopped writing 50 prompts by hand. One workflow does what I used to spend hours on

Dynamic Workflows shipped in Claude Code on May 28. Most builders haven't tried it once

Here's what changed for me

Before: chain prompts manually. Copy output. Paste into next prompt. Fix what went wrong. Repeat 50 times

After: describe the goal. Claude writes its own custom harness for the task - in JavaScript - and coordinates everything automatically

The three failure modes it fixes structurally:

Agentic laziness - Claude stops early and calls partial progress "done." Separate agents with isolated goals fix this

Self-preferential bias - Claude can't fairly verify its own work. Separate verifier agents that never saw the original output fix this

Goal drift - constraints quietly disappear after turn 47. Fresh context windows per agent fix this

The 6 patterns that do most of the work:

Fan-out-and-synthesize - split a task into parallel agents, one per item, merge everything at the end. 50 files reviewed simultaneously instead of one at a time

Adversarial verification - for every agent doing work, a separate agent tries to break its output. Never the same Claude judging itself

Tournament - pairwise comparison beats absolute scoring every time. Especially for taste-based work

Loop until done - keep spawning agents until the stop condition is met. Not a fixed number of passes. Actually done

Generate-and-filter - 20 options generated, then a verifier kills the weak ones. You see 3

Classify-and-act - route different work to different models. Haiku for cheap exploration. Opus only where complexity demands it

Mention "workflow" in a prompt or type ultracode and Claude builds the harness for your specific task

One workflow. Not fifty prompts


--- 引用元 @0xCodez ---
https://t.co/RSly7N44jl
