---
id: "2026-07-07-claudedevs-a-few-patterns-we-frequently-use-with-f-01"
title: "@ClaudeDevs: A few patterns we frequently use with Fable 5: Use Fab"
url: "https://x.com/ClaudeDevs/status/2074606058128224365"
source: "x"
category: "ai-workflow"
tags: ["AI-agent", "x"]
date_published: "2026-07-07"
date_collected: "2026-07-09"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

A few patterns we frequently use with Fable 5: 
    
Use Fable 5 as an "advisor."
 
An executor (Sonnet 5) calls Fable 5 for guidance.

Most tokens are billed at the lower executor rate. https://t.co/JIiZ2gm99Y

On SWE-bench Pro, Sonnet 5 + a Fable 5 advisor tool gets ~92% of Fable 5's score at ~63% of the price.

Fable 5 is called rarely (~once) per task to steer while Sonnet 5 executors the majority of the work.

See our docs to learn more:
https://t.co/f8Rdxn2gwe https://t.co/pzzxCDAwDE

A second strategy: use Fable 5 as an orchestrator.

Fable 5 plans and delegates to workers (Sonnet 5).

Most tokens are billed at the lower worker rate. https://t.co/cwDZJSXekn

On BrowseComp, we tested Claude Managed Agents w/ Fable 5 orchestrator + Sonnet 5 worker sub-agents.

The Fable 5 orchestrator achieves 96% of Fable 5 performance at 46% of the price.

Token-heavy research is delegated to Sonnet 5.

See our cookbook:
https://t.co/zDGXCK79N3 https://t.co/my1ETEQN6u

Claude Managed Agents supports both patterns with sub-agents.

Escalate up to a Fable 5 advisor, or delegate down to Sonnet 5 workers.

Each sub-agent keeps its own cache, so repeat calls don't pay in full for the same context twice.

https://t.co/mspPDDlWHI
