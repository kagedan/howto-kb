---
id: "2026-04-01-openclawの必要な部分だけをclaude-codeで再現する-01"
title: "OpenClawの必要な部分だけをClaude Codeで再現する"
url: "https://zenn.dev/kikuriyou/articles/2603301911_openclaw-on-claude"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "zenn"]
date_published: "2026-04-01"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

はじめに
自律型AIエージェントのOpenClaw、個人的にも壁打ち相手として気に入っていたのですが、実際に使っていくと、OpenClaw固有の設定体系やツール群の理解に時間がかかったり、モデル利用にAPIキーが必要であるために費用が気になってきます。
そこで、OpenClawの設計思想をClaude Codeや標準エコシステム上で必要な機能だけを再現するというアプローチを試みています。Claude Codeには CLAUDE.md、Skills、MCPなど、柔軟にカスタマイズするための仕組みが揃っています。これらはAnthropicの公式ドキュメントやコミュニティの情報が豊富で、新...
