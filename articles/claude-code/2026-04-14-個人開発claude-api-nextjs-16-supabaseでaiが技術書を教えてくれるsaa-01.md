---
id: "2026-04-14-個人開発claude-api-nextjs-16-supabaseでaiが技術書を教えてくれるsaa-01"
title: "【個人開発】Claude API × Next.js 16 × Supabaseで「AIが技術書を教えてくれるSaaS」を2日で作った"
url: "https://qiita.com/shunnosuke-dev/items/c9c609fe35017c0f9218"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

:::message
この記事は [CodeSensei](https://codesensei-iota.vercel.app)の開発記録です。個人開発で、着想から本番デプロイまで2日間で Phase 1〜3 +ユーザー獲得施策までを一気に構築しました。技術選定と「早く出す」ための意思決定を共有します。
:::

## 何を作ったか

**CodeSensei — あなたのコードが教科書になる AI 学習プラットフォーム**

- 15コース・188レッスン・95冊の技術書の知見を内蔵
- ユーザーの GitHub リポジトリ（or 手動ペースト）を題材に、Claude AI が技術書の概念を解説
- 「コードから学ぶ」「バグから学ぶ」「カスタムカリキュラム」など AI 機能を 5 種類搭載
- 日本語 + 英語の i18n、チーム機能、Stripe 決済まで実装済み

https://codesensei-iota.vercel.app

## なぜ作ったか

Claude Code や Cursor を使って開発していて、ある違和感がありました。

「コードは前より10倍速く書
