---
id: "2026-06-16-travisgautier-over-three-weeks-ago-now-i-was-runni-01"
title: "@travisgautier: Over three weeks ago now, I was running 6 concurrent Claude"
url: "https://x.com/travisgautier/status/2066682728792117695"
source: "x"
category: "claude-code"
tags: ["claude-code", "x"]
date_published: "2026-06-16"
date_collected: "2026-06-16"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Over three weeks ago now, I was running 6 concurrent Claude Code Opus 4.8 windows. That number of worktrees had been normal in my workflow for a while, but Opus 4.8 v2.1.158 started to hallucinate bash calls pretty badly. https://t.co/O9ibOkqftF

Tool calls were hitting the wrong parent, like they were confused which Claude instance to report to. Parallel calls would collide and cancel each other out. Also got hit with a Jest heap oom and a terminal crash that same night.

First I pinned the client to 2.1.153 because it felt stable. Turns out it was really just defaulting back to Opus 4.7. So I switched to latest client and pinned "model": "claude-opus-4-7" in ~/.claude/settings.json and things calmed down.

The issue was tracked upstream at /anthropics/claude-code#63538, and a couple of reddit threads all complaining about the same nasty regressions.

Scanning the changelog on 2.1.170, it says they fixed the batch cancel in 2.1.161. "Parallel tool calls: a failed Bash command no longer cancels the others." Hoping the main trigger is gone now.

For a couple of other reasons, I am choosing to remain pinned on Opus 4.7, however 4.8 should be safe again if you were also experiencing this hallucination.

Anyone still seeing tool calls go to the wrong place, weirdness on cancels, or Write/Edit glitches on Opus 4.8 after 2.1.161? Especially with 4+ sessions running.
