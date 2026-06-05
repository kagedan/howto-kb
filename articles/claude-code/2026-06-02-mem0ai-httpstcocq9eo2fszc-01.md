---
id: "2026-06-02-mem0ai-httpstcocq9eo2fszc-01"
title: "@mem0ai: https://t.co/cQ9EO2FSzc"
url: "https://x.com/mem0ai/status/2061822612398014782"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "x"]
date_published: "2026-06-02"
date_collected: "2026-06-05"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/cQ9EO2FSzc


--- Article ---
Agent harnesses are where AI software actually runs. Cursor, Devin, Claude Code, Codex: these environments handle context, orchestrate tools, coordinate agents, and increasingly, manage memory. The harness, not the model, is increasingly the product that ships software.

Memory is where harness design gets hard. 

Where does it sit? What persists when a session ends? It is a largely unsolved problem, and every major harness is solving it differently. 

This post covers what each shipped, where each falls short, and what that gap says about what memory infrastructure has to do.

---

**What Agent Memory Actually Is**

Three different things get called memory, and the distinction matters because each has different failure modes.

1. **Working memory** is what lives in the context window during a session. It resets on session end; the compaction problem (what survives when the window fills) belongs here.
1. **External memory** is anything persisted outside the weights: vector stores, knowledge graphs, files. It survives sessions; the weights don't change. This is where essentially all production memory lives in 2026.
1. **Parametric memory** is knowledge encoded into weights via gradient descent, shaped by the training loop the harness feeds. It generalizes by applying rules rather than retrieving examples. Zero production deployments in 2026.
(The cognitive-science split, semantic / episodic / procedural, describes *what kind* of information is stored; the three tiers above describe *where* it lives.) 

The paper "Contextual Agentic Memory is a Memo, Not True Memory" (arXiv:2604.27707) formalizes the ceiling: retrieval needs Ω(k²) stored examples to match what parametric memory does with O(d) weight updates. Every system below operates within it.

---

**What Major Harnesses Shipped [Overview]**

![](https://pbs.twimg.com/media/HJ0MFa6b0AAsAN-.jpg)

---

**1.**@AnthropicAI**: Claude Code**

Two tracks. [**CLAUDE.](http://claud
