---
id: "2026-03-25-nextjs-16-anthropic-claude-apiでトレード日記ai分析ツールを作った話-02"
title: "Next.js 16 + Anthropic Claude APIでトレード日記AI分析ツールを作った話"
url: "https://qiita.com/tradejournal/items/2dd43da6c697ae0565e2"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

# Next.js 16 + Anthropic Claude APIでトレード日記AI分析ツールを作った話

## はじめに

個人トレーダーとして数年間FXと株を続ける中で、ずっと感じていた課題がありました。「なぜ同じ失敗を繰り返すのか」という問いへの答えが、スプレッドシートや手書き日記では得られなかったのです。

その課題を解決するために作ったのが **TradeJournal**（https://tradejournal.company）です。トレード記録を蓄積し、週次でAIがプロのコーチのような分析レポートを自動生成するWebアプリです。

本記事では技術選定の意図から実装の詳細まで、エンジニア視点で解説します。

---

## 1. なぜ作ったか

トレードにおける最大の敵は「感情」と「自分のルール違反」です。勝てるトレーダーの多くは、厳密なルールと記録管理によってこれを克服しています。しかし一般的なトレーダーのジャーナル管理は以下のような問題を抱えています。

- Excelで記録しても「分析」は自分でやらなければならない
- 手書き日記は書くのが面倒で続かない
- 勝
