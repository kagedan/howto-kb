---
id: "2026-06-26-therobertta-arizes-aparna-dhinakaran-published-wha-01"
title: "@therobertta_: Arize's Aparna Dhinakaran published What is an Agent Harnes"
url: "https://x.com/therobertta_/status/2070311582496882776"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "x"]
date_published: "2026-06-26"
date_collected: "2026-06-26"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Arize's Aparna Dhinakaran published "What is an Agent Harness?" this week and directly called out LangChain: "LangChain is not a harness." She identified 9 components that real harnesses implement.

Stop assembling. Start shipping. Here is the exact approach.

1. The problem with framework assembly:

2. Every LangChain project I have seen follows the same arc. Week 1: excitement. Week 3: plumbing. Week 6: debugging integration issues. Week 10: questioning whether to scrap and start over.

3. 80% of the time goes to infrastructure. 20% goes to workflows. This is what I call "the plumbing inversion." The ratio should be flipped.

What to do instead:

Step 1: Pick an opinionated harness (Claude Code, Codex, Cursor)
Step 2: Ship your first workflow in 48 hours or less
Step 3: Add tools only when a production problem demands them
Step 4: Build evals before building features
Step 5: Let the harness architecture emerge from real usage

This reverses the plumbing inversion. 80% workflows, 20% infrastructure.

Think about what Dhinakaran's 9 components actually mean for your time allocation:

1.

When I was Lead Product Architect at Workday, I saw this pattern in every platform adoption cycle. The teams that fought the platform wasted months on custom plumbing. The teams that adopted the platform and focused on business logic shipped faster every single time.

Agent harnesses are the platform layer of AI. Stop fighting it.

The compound effect of this principle accelerates with every production cycle.

My production harness has 70 MCP tools. Here is how long each category took to build:

Infrastructure (loop, context, safety): 0 hours. The harness handles it.
Skills and tools: roughly 200 hours across 18 months.
Evals and quality gates: roughly 40 hours.

100% of my build time went to domain value. Zero went to plumbing.

The data is consistent across every deployment I have observed. Small architectural decisions create large downstream effects over production timelines.

T
