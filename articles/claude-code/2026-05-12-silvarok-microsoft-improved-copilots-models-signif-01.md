---
id: "2026-05-12-silvarok-microsoft-improved-copilots-models-signif-01"
title: "@silvarok_: Microsoft improved Copilot’s models. Significantly. That’s n"
url: "https://x.com/silvarok_/status/2054341507344466249"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "Python", "x"]
date_published: "2026-05-12"
date_collected: "2026-05-13"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Microsoft improved Copilot’s models. Significantly. That’s not the problem.

The problem is what happens when you move into Copilot Studio and try to build an actual agent workflow. Better models don’t help with that at all.

The assumption is reasonable on the surface: better models mean better AI products. Upgrade the foundation, improve the building on top.

Microsoft’s roadmap is built on this logic. Each release leads with benchmarks. The demos get sharper. The sales pitch gets easier.

But Copilot Studio is a different product from Copilot chat. It’s the platform for building real agents: workflows that connect to business systems, take actions, run without a human in the loop.

That’s not a model problem. That’s a harness problem.

The harness is everything around the model: routing, context, connectors, error handling. Copilot Studio’s harness is opaque, hard to debug, and built on Power Automate logic that takes serious time to learn

You also can’t call Python scripts outside Azure. That’s a hard ceiling

What this looks like in practice: you build something that works three times and fails on the fourth. The error message tells you nothing useful. The failure surface is large and the tooling wasn’t designed for the kind of inspection the problem requires.

Compare to Claude Code or Codex. Write what you want, get a script. If it fails, you get an actual error telling you what broke and where. You can read the code. The workflow is auditable, portable, not trapped in a vendor’s connector ecosystem.

The people who get Copilot Studio working seriously are, functionally, developers. They’ve learned Power Platform’s abstractions, its connector quirks, its expression language.

That’s exactly the audience Copilot Studio was supposed to not require.

Better models won’t fix this. Model quality and harness quality are different variables; they don’t improve on the same schedule.

If your team has flat Copilot Studio adoption, the model isn’t the problem. 

Full
