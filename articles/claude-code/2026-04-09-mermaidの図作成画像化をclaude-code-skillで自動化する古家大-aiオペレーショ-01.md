---
id: "2026-04-09-mermaidの図作成画像化をclaude-code-skillで自動化する古家大-aiオペレーショ-01"
title: "mermaidの図作成・画像化をClaude Code Skillで自動化する｜古家大 | AIオペレーションマネージャー"
url: "https://note.com/masaru_furuya/n/n18ff1c4d6b8b"
source: "note"
category: "claude-code"
tags: ["claude-code", "note"]
date_published: "2026-04-09"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

ブログ記事やObsidianノート、PRの説明、設計ドキュメントに「フローチャートを1枚挟みたい」と思うことはよくあります。そのたびにdraw.ioを立ち上げてポチポチやるのは面倒ですし、GUIで作った図は後から差分管理がしづらいです。  そこで、Mermaid記法をテキストで書いて、mmdc でPNG化するワークフローを回しています。テキストなのでGitで差分管理できますし、AIに「この内容で図にして」と頼めば .mmd ファイルを吐いてくれます。あとは1コマンドでPNGになります。  ただ、毎回AIに「Mermaidで縦フローで色分けして、横1600pxで書き出して…」と指示するの
