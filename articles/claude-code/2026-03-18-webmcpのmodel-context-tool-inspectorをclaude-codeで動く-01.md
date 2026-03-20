---
id: "2026-03-18-webmcpのmodel-context-tool-inspectorをclaude-codeで動く-01"
title: "WebMCPのModel Context Tool InspectorをClaude Codeで動くようにした"
url: "https://zenn.dev/abalol/articles/9526128d199b80"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "Gemini", "zenn"]
date_published: "2026-03-18"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

TL;DR
Google の Model Context Tool Inspector は WebMCP ツールのテスト用 Chrome 拡張ですが、AI 連携が Gemini API のみでした。Claude Code のサブスクで使えるように、ローカルの Go サーバー経由で claude -p を呼ぶ版を作りました。
https://github.com/tomohiro-owada/webmcp-tool-inspector-with-claude

 WebMCP とは
AI がスクレイピングや DOM 解析なしに Web ページを操作できるようにする仕組みです。サイト側が...
