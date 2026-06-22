---
id: "2026-06-21-takuma-uemura-freee-mcp-claudeの連携バックオフィス業務が劇的に自動化で-01"
title: "@Takuma_Uemura_: freee MCP × Claudeの連携、バックオフィス業務が劇的に自動化できる手応えがあります。 ただ、「セキュリテ"
url: "https://x.com/Takuma_Uemura_/status/2068589987830899023"
source: "x"
category: "ai-workflow"
tags: ["MCP", "API", "x"]
date_published: "2026-06-21"
date_collected: "2026-06-22"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

freee MCP × Claudeの連携、バックオフィス業務が劇的に自動化できる手応えがあります。
ただ、「セキュリティ」の注意喚起をさせてください。

MCPはClaudeが直接freeeのAPIを叩きます。
たとえば「自社の財務分析をして」と指示するだけで、口座残高や財務数値などの機密情報が自動でAnthropicのサーバーを経由します。

弊所としても、現在は慎重に以下の対応としています。

・Anthropic APIの規約（学習利用なし）、TLS暗号化、SOC2 Type II取得は確認済
・使い心地の確認のため自社やダミー環境でのみ使用

今後はAnthropicのサーバーを経由しない、ローカル処理する設計も検討中です。
AIの活用は徹底した「ガバナンスとセット」ですね。
便利だからとむやみに使うのはNGです！
