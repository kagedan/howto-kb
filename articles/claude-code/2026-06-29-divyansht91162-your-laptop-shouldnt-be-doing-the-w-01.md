---
id: "2026-06-29-divyansht91162-your-laptop-shouldnt-be-doing-the-w-01"
title: "@DivyanshT91162: Your laptop shouldn't be doing the work anymore. Mine isn't"
url: "https://x.com/DivyanshT91162/status/2071684602482319367"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "x"]
date_published: "2026-06-29"
date_collected: "2026-06-30"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Your laptop shouldn't be doing the work anymore.

Mine isn't.

I moved all my Codex + Claude Code agents from my Mac to a Linux VPS...

And it completely changed how I build.

Here's why it's one of the biggest 10x upgrades I've made:

→ My Mac stays cool while the VPS handles every build, agent, API, and terminal session.

→ Instead of spending $3,000+ on a new machine, I rent powerful Linux compute that scales whenever I need more.

→ Agents never stop running. Close the laptop, lose Wi-Fi, battery dies—it doesn't matter. tmux keeps everything alive.

→ My workflow is finally clean:

• Mac → SSH
• VPS → Codex, Claude Code, APIs, builds & tests
• tmux/cmux → persistent agent sessions
• GitHub → source of truth
• Production → protected deployment

Setup takes less time than you'd expect:

1. Get an Ubuntu 24.04 VPS
2. Add your SSH key
3. SSH into the server
4. Install Git, Node, pnpm, Docker, tmux & cmux
5. Clone your repo
6. Connect with VS Code Remote SSH or Codex
7. Run every AI agent directly on the VPS
8. Forward ports for local testing

The crazy part?

You can literally ask Codex to set up most of this for you.

Once you move your agents off your laptop...

Going back feels impossible.


--- 引用元 @DivyanshT91162 ---
John Carmack has said the same brutal thing for 30 years:

"Most programmers don't actually know what their code is doing. They guess, then pray."

No guessing. Profile first. Reason from the metal up. Understand the machine instead of fighting it.

He's now chasing AGI from scratch at his own lab — building intelligence up from first principles while everyone else just scales.

So I gave Claude Opus 4.8 one job: teach me to engineer the Carmack way.

The way I write code changed permanently. 8 prompts

Prompt 1: Profile Before You Pray

Carmack's first commandment: never optimize what you haven't measured. This kills your guessing habit.

"You are John Carmack reviewing my performance problem.

Here's my code and what feels slow: [PASTE CODE + SYM
