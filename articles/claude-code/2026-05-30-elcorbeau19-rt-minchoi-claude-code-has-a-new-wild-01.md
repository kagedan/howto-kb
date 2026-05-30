---
id: "2026-05-30-elcorbeau19-rt-minchoi-claude-code-has-a-new-wild-01"
title: "@elcorbeau19: RT @minchoi: Claude Code has a new wild feature... dynamic w"
url: "https://x.com/elcorbeau19/status/2060527665946271880"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "x"]
date_published: "2026-05-30"
date_collected: "2026-05-30"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

RT @minchoi: Claude Code has a new wild feature... dynamic workflow.

How to try:

set /model to opus 4.8
set /effort to "ultracode" 😂
use…


--- 引用元 @ClaudeDevs ---
New in Claude Code (research preview): dynamic workflows.

Claude writes an orchestration script on the fly, then spins up a large fleet of coordinated subagents in parallel to take on your most complex tasks.

Use the word "workflow" in a prompt to get started. https://t.co/re4SG3AyDm

Dynamic workflows are useful for tasks that are too big for a single agent loop, such as service-wide bug hunts, large migrations, or stress-testing a design.

They're powerful and can be expensive, consuming a lot of tokens fast. Start with a scoped task to get a feel for it.
You can also set "/effort ultracode", a new effort level that runs at xhigh and lets Claude decide on its own when a task warrants a dynamic workflow.
Dynamic workflows are reusable. Save one as a slash command in your project to share with the team, or in your home directory to use it everywhere.
More on how the orchestration works, and what early users have built with it, on the blog:

https://t.co/SGCXuermDS
Available today on Max, Team, Enterprise, and via the API — including Bedrock, Vertex AI, and Foundry. 

On by default for Max and Team plans, Enterprise admins can opt in via managed settings.

Docs: https://t.co/s2rGZ9xiYP
