---
id: "2026-03-28-nextjs-16-anthropic-claude-apiでトレード日記ai分析ツールを個人開発し-01"
title: "Next.js 16 + Anthropic Claude APIでトレード日記AI分析ツールを個人開発した話【5言語対応・PWA】"
url: "https://qiita.com/tradejournal/items/6ce1b9b3959c8f722075"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

# Next.js 16 + Anthropic Claude APIでトレード日記AI分析ツールを個人開発した話

## はじめに

個人トレーダーとして数年間FXと株を続ける中で、ずっと感じていた課題がありました。「なぜ同じ失敗を繰り返すのか」という問いへの答えが、スプレッドシートや手書き日記では得られなかったのです。

その課題を解決するために作ったのが **[TradeJournal](https://tradejournal.company)** です。トレード記録を蓄積し、週次でAIがプロのコーチのような分析レポートを自動生成するWebアプリです。

> **デモページを公開しています。** アカウント登録不要でUIと機能を確認できます。
> https://tradejournal.company/demo

本記事では技術選定の意図から実装の詳細まで、エンジニア視点で解説します。

### 主な特徴

| 機能 | 概要 |
|---|---|
| AI週次レビュー | Claude APIが数値根拠付きのコーチングを自動生成 |
| ルール違反検知 | 自分で設定した
