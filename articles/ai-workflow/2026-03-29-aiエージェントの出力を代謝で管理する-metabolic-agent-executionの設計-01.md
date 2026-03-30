---
id: "2026-03-29-aiエージェントの出力を代謝で管理する-metabolic-agent-executionの設計-01"
title: "AIエージェントの出力を代謝で管理する — Metabolic Agent Executionの設計"
url: "https://zenn.dev/zima11/articles/6622f0a55896e0"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-03-29"
date_collected: "2026-03-30"
summary_by: "auto-rss"
---

はじめに
AIエージェントに何かを生成させるとき、あなたはその出力を信用できますか？
「生成した→OK」ではなく、「生成した→検証した→問題があれば修復した→それでも駄目なら巻き戻した」という流れをコードレベルで保証する仕組みが欲しくなった。
そこで辿り着いたのが、生物の「代謝」をモデルにした実行パターン——Metabolic Agent Executionだ。
この記事では、broadcast-os（AI放送局を自律制作するOS）に実装したMetabolic Agent Executionの設計を紹介する。実装の中心となるのがrun_metabolic_parallel（Metab...
