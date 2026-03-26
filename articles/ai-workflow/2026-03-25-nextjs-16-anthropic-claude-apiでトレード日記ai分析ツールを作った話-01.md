---
id: "2026-03-25-nextjs-16-anthropic-claude-apiでトレード日記ai分析ツールを作った話-01"
title: "Next.js 16 + Anthropic Claude APIでトレード日記AI分析ツールを作った話"
url: "https://zenn.dev/tradejournal/articles/f886154a9f1ec8"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

はじめに
個人トレーダーとして数年間FXと株を続ける中で、ずっと感じていた課題がありました。「なぜ同じ失敗を繰り返すのか」という問いへの答えが、スプレッドシートや手書き日記では得られなかったのです。
その課題を解決するために作ったのが TradeJournal（https://tradejournal.company）です。トレード記録を蓄積し、週次でAIがプロのコーチのような分析レポートを自動生成するWebアプリです。
本記事では技術選定の意図から実装の詳細まで、エンジニア視点で解説します。


 1. なぜ作ったか
トレードにおける最大の敵は「感情」と「自分のルール違反」です。勝...
