---
id: "2026-04-01-react-reasonact-パターンを-typescript-だけで実装する-01"
title: "ReAct (Reason+Act) パターンを TypeScript だけで実装する"
url: "https://zenn.dev/kt3k/articles/74785af8436b1e"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "LLM", "TypeScript", "zenn"]
date_published: "2026-04-01"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

この記事では AI Agent の代表的な実装パターンの1つである ReAct (Reason+Act) を TypeScript
を使って実装してみます。
ReAct パターンは多くの場合、LangChain、Mastra
などのフレームワーク経由で使われますが「実際に中で何が起きているのか」はブラックボックスになりがちです。
この記事では、フレームワークを一切使わずに、 TypeScript だけで ReAct
エージェントをゼロから実装し、その仕組みを理解します。

 ReAct パターンとは
ReAct は LLM
が「考える(Reason)」と「行動する(Act)」ステップを交...
