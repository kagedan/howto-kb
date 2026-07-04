---
id: "2026-05-25-akshay-pachaar-httpstcovw9eyoiy4z-01"
title: "@akshay_pachaar: https://t.co/VW9EyOiy4Z"
url: "https://x.com/akshay_pachaar/status/2058976178908885210"
source: "x"
category: "ai-workflow"
tags: ["AI-agent", "LLM", "x"]
date_published: "2026-05-25"
date_collected: "2026-07-05"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/VW9EyOiy4Z


--- Article ---
Your agent remembers everything and understands nothing.

Agent memory started with vector databases. Store facts as chunks, retrieve by similarity.

It works until a query needs to connect facts across chunks. Then it falls apart. The problem isn't similarity. It's structure.

Knowledge graphs were the fix. Entities as nodes, relationships as edges, traversal instead of matching.

But most teams hit a different wall.

When you give an agent a knowledge graph for memory, the default behavior is that the LLM handling extraction decides the structure on its own.

It picks the entity types, the relationship labels, and the attributes.

The results are generic.

For example, you’re building a customer support agent. You feed it 50 support conversations covering customers, tickets, features, and escalation history.

You ask: *“Which enterprise customers have open sev-1 tickets?”*

The graph has the data. But every support ticket is stored as a “Topic” node. Every customer is an “Object.” Every relationship is “RELATES_TO.”

There’s no way to filter by type, severity, or plan tier. The query returns noise.

The agent didn’t forget anything. Nobody told it what to pay attention to.

![](https://pbs.twimg.com/media/HJKtp0JaAAA0zu9.jpg)

The fix is straightforward: **define the schema upfront.** Tell the extraction model what types of entities exist in your domain, what relationships are valid, and what attributes each one carries.

That organizational blueprint is called an **ontology**. Think of it as the **schema for your agent’s brain**.

Let’s walk through why this matters, what breaks without it, and how to implement it it using a [**100% open-source soluti](https://github.com/getzep/graphiti)on**.

# Why flat retrieval breaks on multi-hop reasoning

Vector-based memory stores facts as text chunks and retrieves them by semantic similarity. That works until a query requires connecting facts that don’t appear in the same chunk.
