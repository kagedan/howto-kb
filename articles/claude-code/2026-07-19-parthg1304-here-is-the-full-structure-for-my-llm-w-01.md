---
id: "2026-07-19-parthg1304-here-is-the-full-structure-for-my-llm-w-01"
title: "@parthg1304: Here is the full structure for my LLM WIKI setup👇 Three fol"
url: "https://x.com/parthg1304/status/2078934547761381467"
source: "x"
category: "claude-code"
tags: ["CLAUDE-md", "LLM", "x"]
date_published: "2026-07-19"
date_collected: "2026-07-20"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Here is the full structure for my LLM WIKI setup👇

Three folders. That's the whole system.

sources/ holds the raw stuff — articles, transcripts, old repos — and nothing ever touches it once it lands. It's the paper trail.

But raw files aren't useful sitting there on their own, so wiki/ is where the AI actually writes: markdown pages, one per topic, every one tagged and cross-linked to the others. This is the layer I actually read.

And because an AI with no rules will happily contradict itself by next Tuesday, there's CLAUDE.md — the rulebook it re-reads at the start of every single session, so "how do I file this" isn't a decision it's making fresh each time.

Two spine files hold it together: index.md, the catalog of everything, and log.md, a timestamped record of every single ingest and query, no exceptions.

Three verbs run the whole thing — ingest, query, lint. That's it. That's the entire engine.
