---
id: "2026-05-08-chick-flutter-メモ-vscodeでaws-mcp-serverを使うには-1-aws-01"
title: "@chick_flutter: メモ: VSCodeでAWS MCP Serverを使うには 1. AWS CLI / uvx を用意 2. AWS"
url: "https://x.com/chick_flutter/status/2052707517600592313"
source: "x"
category: "claude-code"
tags: ["MCP", "AI-agent", "VSCode", "x"]
date_published: "2026-05-08"
date_collected: "2026-05-09"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

メモ: VSCodeでAWS MCP Serverを使うには

1. AWS CLI / uvx を用意
2. AWS CLIプロファイル or SSOで認証
3. VSCodeで MCP: Open User Configuration
4. mcp.json にAWS MCP設定を追加
5. VSCodeをReload
6. Copilot AgentからAWS情報を参照

{
  "servers": {
    "awsMcp": {
      "type": "stdio",
      "command": "uvx",
      "args": [
 "mcp-proxy-for-aws@latest",
 "https://t.co/GtpLDNQVPB",
 "--metadata",
 "AWS_REGION=ap-northeast-1"
      ],
      "env": {
        "AWS_PROFILE": "your-profile"
      }
    }
  }
}
