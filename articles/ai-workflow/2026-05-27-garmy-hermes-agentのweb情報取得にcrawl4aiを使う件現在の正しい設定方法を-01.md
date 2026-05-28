---
id: "2026-05-27-garmy-hermes-agentのweb情報取得にcrawl4aiを使う件現在の正しい設定方法を-01"
title: "@garmy: Hermes AgentのWeb情報取得にCrawl4AIを使う件、現在の正しい設定方法を書いたサイトがないしHerme"
url: "https://x.com/garmy/status/2059594636130439627"
source: "x"
category: "ai-workflow"
tags: ["MCP", "AI-agent", "x"]
date_published: "2026-05-27"
date_collected: "2026-05-28"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

Hermes AgentのWeb情報取得にCrawl4AIを使う件、現在の正しい設定方法を書いたサイトがないしHermes自身も適切な回答ができないが、両方が対応している通信方式Server-Sent Events (SSE)で接続すればよい。

mcp_servers:
  crawl4ai:
    url: http://IPアドレス:11235/mcp/sse
    transport: sse

参考
https://t.co/am9ypHtNad
https://t.co/H9XQZB55SS
