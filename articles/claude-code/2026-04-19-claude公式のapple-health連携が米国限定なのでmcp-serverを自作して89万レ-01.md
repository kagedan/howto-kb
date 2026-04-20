---
id: "2026-04-19-claude公式のapple-health連携が米国限定なのでmcp-serverを自作して89万レ-01"
title: "Claude公式のApple Health連携が米国限定なので、MCP Serverを自作して89万レコードを分析した"
url: "https://zenn.dev/at_sushi/articles/1a628f17dda8b1"
source: "zenn"
category: "claude-code"
tags: ["MCP", "zenn"]
date_published: "2026-04-19"
date_collected: "2026-04-20"
summary_by: "auto-rss"
query: ""
---

TL;DR

Claude公式のApple Health連携は米国Pro/Max限定。日本では使えない
自作した。89万レコードをSQLiteに格納 → Claude DesktopからMCP経由で自然言語クエリ
朝散歩のbefore/after: 歩数3倍、日光2.2倍、歩行非対称性-71%

コード公開中 → GitHub


対象読者: Claude Desktop/MCPに興味があるエンジニア、ヘルスデータを活用したい人

 なぜ自作したか
2026年1月、Claude公式がApple Health連携を発表した。試そうとしたら米国のPro/Maxプラン限定。日本では使えない...
