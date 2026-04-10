---
id: "2026-04-09-mcpの仕様理解のためにinspectorを自作してみた-01"
title: "MCPの仕様理解のためにInspectorを自作してみた"
url: "https://zenn.dev/watabean/articles/mcp-inspector-cli"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

はじめに
Claude Desktop や Claude Code に MCP サーバーをつないで使っていると、内部で何が起きているのか気になることがあります。公式の @modelcontextprotocol/inspector を使えば GUI で挙動を確認できますが、SDK が多くを吸収してくれるぶん、プロトコルそのものを意識する場面はあまりありません。
そこで今回は、MCP の通信を JSON-RPC レベルで可視化する CLI ツールを自作しました。最初は「MCP はツールを呼び出すための共通インターフェース」くらいの理解でしたが、実装してみると、実際にはクライアント側にも...
