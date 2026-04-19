---
id: "2026-04-18-gas-claude-api-search-console-で作るseo週次レポート自動生成システム-01"
title: "GAS + Claude API + Search Console で作る、SEO週次レポート自動生成システム"
url: "https://zenn.dev/bentenweb_fumi/articles/seo-weekly-20260418"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-04-18"
date_collected: "2026-04-19"
summary_by: "auto-rss"
query: ""
---

はじめに
「SEOをやっているけど、毎週どのキーワードを狙って記事を書くかの判断材料がない」
これは中小規模のオウンドメディアを運用していると必ず突き当たる壁です。Search Console を毎週開いてエクセルに転記して、競合と比較して、改善案を考えて……というのを手作業でやっていると、本業を圧迫します。
そこで、毎週土曜の朝にレポートが自動でDiscordに届く仕組みを Google Apps Script + Claude API で構築しました。レポートを朝コーヒーを飲みながら見て、その週に書く記事のキーワードを判断するだけで済みます。
本記事では、その構成と実装のポイント...
