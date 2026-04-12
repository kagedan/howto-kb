---
id: "2026-04-11-prを出すだけでスクショ付き動作確認レポートが自動生成される仕組みを作るclaude-playwri-01"
title: "PRを出すだけでスクショ付き動作確認レポートが自動生成される仕組みを作る（Claude × Playwright）"
url: "https://zenn.dev/datum_studio/articles/ebefce70f39a0d"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

はじめに
こんにちは。データエンジニアの山口歩夢です。
以前、Claude CodeとPlaywright CLIを使ってStreamlitで作ったアプリケーションの動作確認レポートを自動作成するスキルを作りました。
対話形式で動作確認手順をClaudeに指示すると、Playwright CLIがStreamlitアプリを動かして、指示した通りに操作して、動作確認手順をスクショ付きで出力してくれると言ったものです。どんな風にレポートが出力されるのかは、以下の記事をご確認ください。
https://zenn.dev/datum_studio/articles/d3b8e49a3c422...
