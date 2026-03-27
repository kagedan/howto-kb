---
id: "2026-03-26-googleスプレッドシートでclaude-apiを使う方法gasで実装コード付き-01"
title: "GoogleスプレッドシートでClaude APIを使う方法【GASで実装、コード付き】"
url: "https://zenn.dev/ino38/articles/claude-api-google-sheets-gas"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

はじめに
Anthropicが提供するClaude APIをGoogle Apps Script（GAS）から呼び出すことで、Googleスプレッドシート上で翻訳・要約・分類・感情分析などのAI処理を実行できます。=CLAUDE_TRANSLATE(A1) のようなカスタム関数として使えるようにすると、ExcelのVLOOKUPと同じ感覚でAI処理をセル関数として書けるようになります。
この記事では、GASからClaude APIを呼び出す基本コードから、スプレッドシートのカスタム関数として使えるようにするところまで実装方法を解説します。


 前提

Anthropicのアカウント...
