---
id: "2026-07-15-superdoccimo-mcp-server-を増やす時怖いのは接続できるかだけではなく同じ設定を-01"
title: "@superdoccimo: MCP server を増やす時、怖いのは「接続できるか」だけではなく、同じ設定を複数のAI clientにばらまき、巨"
url: "https://x.com/superdoccimo/status/2077366425849626931"
source: "x"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "x"]
date_published: "2026-07-15"
date_collected: "2026-07-16"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

MCP server を増やす時、怖いのは「接続できるか」だけではなく、同じ設定を複数のAI clientにばらまき、巨大なtool定義を毎回contextへ押し込むことです。

tsouth89/toolport は、READMEを見る限り、MCP server群を一度ローカルで設定し、Claude、Cursor、Codexなどのclientから一つのgatewayとして共有するOSS。

面白いのは、単なるプロキシではなく、lazy tool discovery、tool integrity check、quarantine、OS keychainでのsecret管理まで同じ境界に置いているところです。

僕の見方では、これは「便利なMCP集約」より、agent運用で膨らむcontext費用と信頼境界を一か所で検収する道具に近い。
ただし、今回はREADME/API確認です。接続する各serverの権限、実行ログ、人間承認の粒度は、Toolport側だけでなく個別server側でも確認した方がいいです。

情報元: GitHub / Hacker News
