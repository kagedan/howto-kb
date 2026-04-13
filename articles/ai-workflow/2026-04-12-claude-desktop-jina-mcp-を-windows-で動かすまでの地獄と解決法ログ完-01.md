---
id: "2026-04-12-claude-desktop-jina-mcp-を-windows-で動かすまでの地獄と解決法ログ完-01"
title: "Claude Desktop × Jina MCP を Windows で動かすまでの地獄と解決法（ログ完全公開）"
url: "https://zenn.dev/ikahan/articles/a723fd0e084a70"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "zenn"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

対象読者

Claude Desktop の MCP を使いたい人
Jina MCP (API) を導入したい人
runningにならなくて詰んでいる人



 結論（これで動く）
{
  "mcpServers": {
    "jina-mcp-server": {
      "command": "C:\\Program Files\\nodejs\\node.exe",
      "args": [
        "C:\\Program Files\\nodejs\\node_modules\\npm\\bin\\npx-cli.js",
        "-y",
...
