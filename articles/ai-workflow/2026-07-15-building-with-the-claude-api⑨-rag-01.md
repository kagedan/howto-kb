---
id: "2026-07-15-building-with-the-claude-api⑨-rag-01"
title: "Building with the Claude API⑨ | RAG"
url: "https://note.com/konitan_ai/n/n889695d88372"
source: "note"
category: "ai-workflow"
tags: ["API", "note"]
date_published: "2026-07-15"
date_collected: "2026-07-15"
summary_by: "auto-rss"
query: ""
---

この記事は、有料マガジン「Claude検定：Building with API」の1本です。Claude APIで作るための全11レッスンを、マガジン（¥1,980）でまとめて読めます。Anthropic公式の修了クイズ「Claude検定」に日本語で備えるための一冊です。

<https://note.com/konitan_ai/m/m2a0f30242e35>

> 800ページの文書のように大きすぎる資料をClaudeに渡すためのRAGを実装します。意味の近さで探すsemantic searchと、識別子の完全一致に強いBM25を合成した頑健な検索の作り方を学びます。この記事は、Anthropic公式コース「Building with the Claude API」の第9回を、原典を読まなくても学べる日本語教材として書き直したものです。シリーズの入口は[はじめに](https://note.com/konitan_ai/n/nbb4b9f79ebda)、全体の地図は[対策マップ](https://note.com/konitan_ai/n/nd267433454ab)から。

このレッスンを終えると、次の5つができるようになります。

1. RAGが解く問題と、そのトレードオフを説明できる
2. 4つのchunking戦略を使い分けられる
3. embeddingsとcosine similarityでsemantic searchを実装できる
4. BM25でlexical searchを補完できる
5. reciprocal rank fusionでhybrid searchに合成できる

所要時間の目安は35分です。
