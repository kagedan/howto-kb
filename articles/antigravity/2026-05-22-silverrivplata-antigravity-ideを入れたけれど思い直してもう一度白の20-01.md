---
id: "2026-05-22-silverrivplata-antigravity-ideを入れたけれど思い直してもう一度白の20-01"
title: "@SilverRivPlata: Antigravity IDEを入れたけれど、思い直してもう一度白の2.0を入れ直したw Claude Desktopの"
url: "https://x.com/SilverRivPlata/status/2057768326101925932"
source: "x"
category: "antigravity"
tags: ["MCP", "Gemini", "antigravity", "x"]
date_published: "2026-05-22"
date_collected: "2026-05-23"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

Antigravity IDEを入れたけれど、思い直してもう一度白の2.0を入れ直したw
Claude Desktopのようなものなのな。ローカルで動く自作MCPサーバに接続することも出来たので、バイブコーディングだけでなく色々と使えそう。
そのうちIDEも共存できるように改修されるだろうと期待している。

#Antigravity

MCPサーバの設定方法がgemini-cliとは少し違っていて、

C:\Users\UserName\.gemini\antigravity\mcp_config.json

{
  "mcpServers": {
    "my-mcp-server": {
      "serverUrl": "http://127.0.0.1:8932/mcp"
    }
  }
}
