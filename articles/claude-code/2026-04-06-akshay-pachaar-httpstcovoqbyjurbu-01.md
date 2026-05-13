---
id: "2026-04-06-akshay-pachaar-httpstcovoqbyjurbu-01"
title: "@akshay_pachaar: https://t.co/VoQByJUrBU"
url: "https://x.com/akshay_pachaar/status/2041146899319971922"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "OpenAI", "x"]
date_published: "2026-04-06"
date_collected: "2026-05-13"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/VoQByJUrBU


--- Article ---
A deep dive into what Anthropic, OpenAI, Perplexity and LangChain are actually building. Covering the orchestration loop, tools, memory, context management, and everything else that transforms a stateless LLM into a capable agent.

---

You've built a chatbot. Maybe you've wired up a ReAct loop with a few tools. It works for demos. Then you try to build something production-grade, and the wheels come off: the model forgets what it did three steps ago, tool calls fail silently, and context windows fill up with garbage.

The problem isn't your model. It's everything around your model.

LangChain proved this when they changed only the infrastructure wrapping their LLM (same model, same weights) and jumped from outside the top 30 to rank 5 on TerminalBench 2.0. A separate research project hit a 76.4% pass rate by having an LLM optimize the infrastructure itself, surpassing hand-designed systems.

That infrastructure has a name now: **the agent harness**.

# What Is the Agent Harness?

The term was formalized in early 2026, but the concept existed long before. The harness is the complete software infrastructure wrapping an LLM: orchestration loop, tools, memory, context management, state persistence, error handling, and guardrails. Anthropic's Claude Code documentation puts it simply: the SDK is "**the agent harness that powers Claude Code.**" OpenAI's Codex team uses the same framing, explicitly equating the terms "**agent**" and "**harness**" to refer to the **non-model infrastructure** that makes the LLM useful.

I really liked the canonical formula, from LangChain's Vivek Trivedy: **"If you're not the model, you're the harness."**

Here's the distinction that trips people up. The "agent" is the emergent behavior: the goal-directed, tool-using, self-correcting entity the user interacts with. The harness is the machinery producing that behavior. When someone says "I built an agent," they mean they built a harness and pointed it
