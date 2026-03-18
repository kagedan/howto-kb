---
id: "2026-03-17-スマホの-telegram-から-claude-に話しかけられる環境を自作した-01"
title: "スマホの Telegram から Claude に話しかけられる環境を自作した"
url: "https://zenn.dev/acropapa330/articles/zenn_article_telegtam_to_claude"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

スマホの Telegram から Claude に話しかけられる環境を自作した

 はじめに
「スマホから Claude に指示を送れたら便利じゃないか？」
そんな思いつきから始まり、気づいたら Google Drive との PPTX 連携まで実装していました。本記事では、Telegram Bot × Claude Agent SDK を Windows PC 上に構築した手順と、その途中で詰まったポイントを丁寧に紹介します。
プログラミング経験はあるけど Claude Agent SDK は初めて、という方を想定して書いています。


 完成したシステムの概要
最終的に以下のこと...
