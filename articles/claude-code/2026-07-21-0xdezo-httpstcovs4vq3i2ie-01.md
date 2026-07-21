---
id: "2026-07-21-0xdezo-httpstcovs4vq3i2ie-01"
title: "@0xDezo: https://t.co/vs4VQ3I2Ie"
url: "https://x.com/0xDezo/status/2079595162955571339"
source: "x"
category: "claude-code"
tags: ["LLM", "x"]
date_published: "2026-07-21"
date_collected: "2026-07-22"
summary_by: "auto-x"
query: ""Model Context Protocol" tutorial OR "Claude MCP" integration"
---

https://t.co/vs4VQ3I2Ie


--- Article ---
In April 2026, Andrej Karpathy published a GitHub gist called the LLM Wiki pattern. The idea was simple: stop treating AI as a chat window that forgets you. Feed it your notes once. Let it structure, link, and index everything. Then only work against the clean base, never re-read raw files.

The gist hit 6,800 stars in weeks. Thousands of people built the exact same setup: Obsidian for storage, Claude for the brain on top. And it works. Sort of.

The problem nobody's discussing: at real usage, that setup burns tokens on a workload it was never designed for. Every question re-scans the same vault. Every /autoresearch round fires multiple full-context calls. Every weekly lint reads the entire graph.

On July 16, Moonshot AI released Kimi K3. A 2.8 trillion parameter open-weight model with a 1 million token context window, priced at Sonnet levels on paper but 3-4x cheaper on this specific workload because of how caching works. Weights drop under Modified MIT on July 27. That's 6 days.

If you're building a second brain this month, this is the article to read before you commit to a stack.

**Follow @0xDezo. Here's the full breakdown.**

---

## 1/ THE PATTERN 

Karpathy's insight was mechanical, not philosophical. Raw notes are source code. The wiki is the compiled product. You don't recompile a program every time you run it.

```
Traditional AI chat                Second brain (Karpathy pattern)
─────────────────────────────────────────────────────────────
Session starts cold                Loads full context per session
Re-reads raw files every time      Reads clean index once
No cross-references                Auto-links every new note
Answers from working memory        Answers from whole graph
Forgets when tab closes            Compounds every day
Every query = full re-parse        Every query = index lookup
```

**The setup:** Obsidian holds every note as plain Markdown on your disk. An AI model reads the whole vault throug
