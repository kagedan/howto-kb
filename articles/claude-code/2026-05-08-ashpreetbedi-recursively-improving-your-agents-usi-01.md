---
id: "2026-05-08-ashpreetbedi-recursively-improving-your-agents-usi-01"
title: "@ashpreetbedi: Recursively improving your agents using claude code One tri"
url: "https://x.com/ashpreetbedi/status/2052887277798597016"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "x"]
date_published: "2026-05-08"
date_collected: "2026-05-09"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Recursively improving your agents using claude code

One trick so simple and surprisingly effective is letting claude code rip on your agents (see image below). 

Here's my current workflow:
> cc creates new agent.
> cc improves agent against its own instructions.
> i drive and cc implements new capabilities

If your platform is set up for auto-improvement, everything can be done by coding agents. From creation to improvement to adding new capabilities. 

Let me walk you through it:

1. Creating an agent

This one is fairly common so we won't go too deep into it. I have a prompt that gives cc all the context it needs and tells it how to go about creating new agents. I just open claude code and type in:

> "Run docs/create-new-agent.md in a new branch"

and cc asks a few questions, figures out what i want to build and builds it. It will run smoke tests and basic validation.

Incredible how something that used to take a few days, even earlier this year, can now be fully automated.

2. Improving the agent

This is the loop I find myself running the most. Open cc and type in:

> "Run docs/improve-agent.md"

What it does under the hood is pretty cool. It reads the target agent's `INSTRUCTIONS`, then derives 8 to 12 probes from them. Some are golden-path, some are edge cases, some are tool-selection probes, plus a couple of adversarial ones thrown in for good measure. 

It runs each probe against the live container <- this is the big unlock from the platform. Reads the response along with the tool calls from the container logs, and judges PASS or FAIL against what the `INSTRUCTIONS` actually promise.

For every failure it picks a lever: tighten a rule, add a rule, swap a tool, bump `num_history_runs`, whatever fits the failure mode. It edits `agents/<slug>.py`, hot-reloads, and re-runs the probes that failed. 

Then it iterates.

The really nice thing here is that the agent itself is the spec. claude derives the test set from the spec, runs it, and fixes the failures. Zer
