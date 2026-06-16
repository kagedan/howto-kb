---
id: "2026-06-13-openrouter-introducing-the-fusion-api-the-smartest-01"
title: "@OpenRouter: Introducing the Fusion API, the smartest compound model in t"
url: "https://x.com/OpenRouter/status/2065856853989270011"
source: "x"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "Gemini", "GPT", "x"]
date_published: "2026-06-13"
date_collected: "2026-06-16"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

Introducing the Fusion API, the smartest compound model in the market.

Fusion achieves Fable-level intelligence at half the price.

How it works 👇 https://t.co/OTUQAdTQjU

We benchmarked Fusion on 100 hard research tasks and found:

1. Panels of models consistently outperform individual models
2. Beyond-frontier performance can be achieved with frontier panels
3. Panels of budget models can surpass frontier models at a much lower cost

By testing different combinations of models, we found that roughly three quarters of the lift that Fusion provides comes from synthesis, and one quarter from diversity. https://t.co/XFySlDphtL

Notably, the budget panel was comparable with Claude Fable 5 in performance.

A panel of Gemini 3 Flash, Kimi K2.6, and DeepSeek V4 Pro, fused together, beat solo GPT-5.5 and solo Opus 4.8 outright.

And it landed within 1% of Fable 5 while costing roughly half the price.

How does it work?

When you send a prompt to Fusion, we fan it out to a panel of models in parallel, each with web search and bash tools enabled.

A judge model reads every response and extracts the structure: consensus points, contradictions, partial coverage, unique insights, blind spots.

Chatroom: https://t.co/0HkAUmBCJ7

Then a synthesizer writes the final answer grounded in that analysis

Fusion runs server-side, so developers can call it exactly like a single model slug: "openrouter/fusion"

Or let the model decide when to reach for it by adding  {"type": "openrouter:fusion"} to your tools array.

We ran it on the DRACO deep research benchmark by Perplexity: 100 deep research tasks across 10 domains, from law and medicine to finance and product comparison.

Each task is graded against ~39 weighted criteria, and wrong answers carry negative weight. (You can't bluff your way to a high score by being verbose.)

https://t.co/RIiTdy1pFP

One detail we want to call out: when we first gave the panel web search, models started surfacing the DRACO rubric online.

We excluded t
