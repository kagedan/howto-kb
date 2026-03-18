---
id: "2026-03-17-cloudflare-zero-trustでclaude-in-chromeが繋がらない問題の原因と-01"
title: "Cloudflare Zero TrustでClaude in Chromeが繋がらない問題の原因と解決策"
url: "https://zenn.dev/hiroe_orz17/articles/a586cf0d586ef1"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "zenn"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

はじめに
Claude Desktop（MCP）とChromeの拡張機能「Claude in Chrome」を組み合わせて使っていたところ、Cloudflare Zero Trust（WARP）を有効にすると接続できなくなるという問題に遭遇しました。


 環境

macOS
Claude Desktop（MCP）
Claude in Chrome（Chrome拡張機能）
Cloudflare Zero Trust（WARP クライアント）



 最初の仮説：ローカルアドレスの問題
Claude DesktopとChrome拡張はlocalhost経由でWebSocket通信してい...
