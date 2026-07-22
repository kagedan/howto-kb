---
id: "2026-07-21-dani-avila7-claude-code-v21217-subagents-no-longer-01"
title: "@dani_avila7: Claude Code v2.1.217, subagents no longer spawn nested subag"
url: "https://x.com/dani_avila7/status/2079703790257578117"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "x"]
date_published: "2026-07-21"
date_collected: "2026-07-23"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

Claude Code v2.1.217, subagents no longer spawn nested subagents by default

To allow nesting again, set CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH to the depth you want to run

Same release also caps concurrent subagents at 20 (CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS) https://t.co/rW7PBZKEix


--- 引用元 @dani_avila7 ---
Claude Code subagents can nest 5 levels deep now 

@bcherny announced it, and today I finally got to try it, Here's the full chain running end to end:

- main 
   - project-auditor                      // level 1
     - structure-checker              // level 2
       - import-validator               // level 3
         - dependency-tracer       // level 4
           - style-sync                       // level 5

Each level runs in its own context window

Only the top-level summary returns to main, depth 5 is the hard cap, that agent can't spawn further

Repo to reproduce in the thread:

https://t.co/MuEQuKNkF7

4 scenarios: 
- noisy main context 
- clean subagent 
- fork subagent  
- 5-level nested chain from the video https://t.co/6cr3qzJnKX
