---
id: "2026-06-27-connect24h-信頼設計重要リポジトリを開くだけを甘く見たら負けamazon-q-develo-01"
title: "@connect24h: 信頼設計重要。リポジトリを開くだけ、を甘く見たら負け。Amazon Q DeveloperのCVE-2026-12957"
url: "https://x.com/connect24h/status/2070797495580664268"
source: "x"
category: "claude-code"
tags: ["MCP", "x"]
date_published: "2026-06-27"
date_collected: "2026-06-28"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

信頼設計重要。リポジトリを開くだけ、を甘く見たら負け。Amazon Q DeveloperのCVE-2026-12957はCVSS 8.5、.amazonq/mcp.json経由でMCP serverを起動し、AWS keysやCLI tokensを抱えた開発端末に触れる筋だった。
MCPそのものより、repo内設定を実行扱いにする信頼境界。Amazonは修正済みだが、情シスはVS Code 2.20、JetBrains 4.3、Eclipse 2.7.4、Visual Studio toolkit 1.94.0.0以上とLanguage Servers for AWS 1.69.0を棚卸ししてほしい。直近cloneしたrepoの.amazonq/mcp.jsonと不審な外向き通信をSWGなどで見よう。開発端
末はが新たな攻撃面なの勘弁してほしい。
https://t.co/a706hUhwTq #セキュリティ
