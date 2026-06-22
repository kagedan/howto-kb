---
id: "2026-06-21-blum-og-andrej-karpathy-think-of-it-almost-like-an-01"
title: "@Blum_OG: Andrej Karpathy: think of it almost like an employee or an"
url: "https://x.com/Blum_OG/status/2068843959791870048"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "x"]
date_published: "2026-06-21"
date_collected: "2026-06-22"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Andrej Karpathy:

"think of it almost like an employee or an intern"

that line is the clean way to read GLM-5.2

GLM-5.2 is built for repo-scale coding loops:

give it the task, the repo, the tests, the constraints, and enough time to grind through the work

the appeal is cost

the guide’s core setup:

1. cloud first
- use the GLM Coding Plan if you want cheap interactive coding
- wire it into Claude Code with Zai’s Anthropic-compatible endpoint
- set API_TIMEOUT_MS=3000000 so long calls don’t get killed
- use glm-5.2[1m] when you need the full context window

2. pay-as-you-go when volume is unclear
- input is around $1.40/M
- cached input is around $0.26/M
- output is around $4.40/M
- stable prompt prefixes matter because cached context can cut repeat input hard

3. local only when you have the hardware reason
- full BF16 is around 1.5 TB
- FP8 is around 756 GB
- Unsloth 2-bit GGUF is around 239 GB
- a 256 GB Mac Studio is the cleanest consumer box
- expect around 3 to 9 tok/s, so batch work beats chat

the prompt style changes too

give it:
- one concrete objective
- repo map and files
- success criteria
- tests to run
- libraries it can use
- files it should leave alone

then let it work

use it for long coding jobs, migrations, frontend passes, test repair, repo reading, and tool-heavy loops

save Claude and Codex for the places where they still win

start with cloud, prove the workflow, then spend money on hardware only after the loop is already paying rent


--- 引用元 @hooeem ---
https://t.co/xTA9Mdowhi
