---
id: "2026-07-15-gsemetfr-httpstco4qoi3pzpfo-01"
title: "@gsemetfr: https://t.co/4qoI3PZpFo"
url: "https://x.com/gsemetfr/status/2077498943085117460"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "x"]
date_published: "2026-07-15"
date_collected: "2026-07-16"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

https://t.co/4qoI3PZpFo


--- Article ---
*This article was published first on [medium*](https://medium.com/@gsemet/building-agentic-project-harness-0254797a0236).

Every coding agent (Claude Code, Copilot) ships with a built-in “Harness”:
tool routing, permission checks, context management, error recovery.
This harness accounts for roughly 98% of the coding agent’s codebase, while less than 2% is the “Agent Loop”, a “while” loop calling LLM until the LLM decide it work is finished.

When using a Coding Agent, any project needs its own layer on top of it: the project harness.

This article presents a simple taxonomy for its components, openly inspired from [Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html) article:  how to organise guides to keep the context lean, how to use sensors in quality gates in your project to catch the mistakes that agent will make, and why setting up regular Maintenance Agentic Tasks allows to keep small harness drift under control.

## The economics changed

In 2024, AI-assisted coding cost a few dollars per month per engineer.
Flat subscription were the norm, GitHub had Premium Request.

In 2026, serious agentic coding session can consume $100 to $200 in tokens. That is per engineer, per day. Flat plans are disappearing or highly limited, without access to some models.

The relevant metric is no longer “lines of code AI generates”, or worst "token-maxing", but *outcome per token*: how much verifiable engineering value each dollar of model inference produces. That's way more difficult to evaluate, that's why companies focussed on what they pay rather on what they will sell.

Optimising tokens consumption, ensuring heavy agentic development workflow delivers real value means Project has to keep the coding agent under tight control.

SDD frameworks try to make this part is easy (like SpecKit "constitution" skill), but I do not agree this should be outsourced.

Project mainteneurs have to
