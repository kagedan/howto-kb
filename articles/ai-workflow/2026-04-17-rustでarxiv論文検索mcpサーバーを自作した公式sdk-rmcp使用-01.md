---
id: "2026-04-17-rustでarxiv論文検索mcpサーバーを自作した公式sdk-rmcp使用-01"
title: "RustでarXiv論文検索MCPサーバーを自作した（公式SDK rmcp使用）"
url: "https://zenn.dev/aisumairu/articles/1f0933af3b1969"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "zenn"]
date_published: "2026-04-17"
date_collected: "2026-04-18"
summary_by: "auto-rss"
query: ""
---

はじめに
AIエージェント全盛期に今更ですが、MCPサーバーを作りましたので記事にします！
後々、Google Cloud Runで運用しようと思い、公式のSDKがあったので、Rustで書いてみました。
GitHubに公開してます。chunsu1002/mcp-arxiv-server

 何を作ったか
arXiv APIを叩いて論文を検索し、JSON形式で返すシンプルなツールを作りました。(要約やダウンロードなどは、気が向いたら追加するかもしれません。)

 Rust用のMCP SDK
rmcp（公式）のものを利用しました。
https://github.com/modelcont...
