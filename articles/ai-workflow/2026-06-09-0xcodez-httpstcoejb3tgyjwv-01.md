---
id: "2026-06-09-0xcodez-httpstcoejb3tgyjwv-01"
title: "@0xCodez: https://t.co/eJB3TgyJwV"
url: "https://x.com/0xCodez/status/2064374643729773029"
source: "x"
category: "ai-workflow"
tags: ["prompt-engineering", "AI-agent", "x"]
date_published: "2026-06-09"
date_collected: "2026-06-21"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/eJB3TgyJwV


--- Article ---
Most developers still prompt their coding agents by hand. They type, they wait, they read the diff, they type again. **9**out of 10 builders have never written a single loop that prompts the agent for them.

No **automation**, no **state file**, no **verifier**, no **schedule**. The leverage point has moved - from *typing prompts* to *designing systems that prompt*. This is the 14-step roadmap from prompter to loop designer.

> Follow my Linkedin to get fresh AI alpha: linkedin.com/in/lev-deviatkin

This is the 14-step roadmap to make that shift - sourced from Anthropic’s engineering docs, Addy Osmani’s long-form on loop engineering, and recent measurement studies. 

Three tiers: figure out if you actually need a loop, learn the five building blocks, then build the smallest one that works without hurting you.

![](https://pbs.twimg.com/media/HKYTPjUX0AAJooq.png)

**14 steps. 3 tiers. Stop prompting. Start designing.**

---

PART 1 **· The Why & The Test**

## 01. Loop engineering is replacing yourself *as the prompter*.

For two years, the way you got something out of a coding agent was: write a prompt, share the context, read what came back, write the next prompt. The agent was a tool and you held it the entire time. **That part is ending.**

Loop engineering is building a small system that *finds* the work, *hands* it to the agent, *checks* the result, *records* what happened, and *decides* the next move - on its own. You design that system once. The system prompts the agent from then on.

Addy Osmani breaks it into six parts:

![](https://pbs.twimg.com/media/HKYT-XBXEAI0yYt.png)

Anthropic engineers now merge eight times as much code per day as they did in 2024 - a figure Anthropic itself calls “almost certainly an overstatement of the true productivity gain.” 

The number is debated. The mechanism isn’t: **the leverage point moved from typing prompts to designing the loop that prompts**.

---

## 02. Run the 4-condition
