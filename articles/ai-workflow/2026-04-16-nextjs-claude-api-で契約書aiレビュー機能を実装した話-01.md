---
id: "2026-04-16-nextjs-claude-api-で契約書aiレビュー機能を実装した話-01"
title: "Next.js + Claude API で契約書AIレビュー機能を実装した話"
url: "https://zenn.dev/ze1ny/articles/nextjs-claude-api-contract-review"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

運送業向けの契約書管理SaaSに、Claude Sonnet 4.6 を使った「契約書AIレビュー」機能を1日で実装した記録です。法務の専門家がいない中小企業が、受け取った契約書の問題点を即座に把握できるようになります。


 この記事で分かること

Next.js 16 の API Route で Claude API を呼ぶ方法
契約書レビューに特化したプロンプトの設計
構造化されたJSON出力を安定して得るコツ
有料プラン限定機能のゲーティング実装
Adaptive Thinking の使い方


 背景：なぜ契約書AIレビューが必要だったか
僕は個人開発で、中小運送会社向けの「...
