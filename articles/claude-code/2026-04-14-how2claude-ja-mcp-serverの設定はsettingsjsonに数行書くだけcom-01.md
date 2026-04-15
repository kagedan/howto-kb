---
id: "2026-04-14-how2claude-ja-mcp-serverの設定はsettingsjsonに数行書くだけcom-01"
title: "@how2claude_ja: MCP Serverの設定はsettings.jsonに数行書くだけ。commandとargsで起動コマンドを指定し、e"
url: "https://x.com/how2claude_ja/status/2044147387506229385"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "x"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-x"
---

Claude Codeのデフォルト機能はローカルファイルとターミナルに限られています。データベース照会、Slack検索、内部API呼び出し——これを可能にするのがMCPです。🧵

MCP（Model Context Protocol）はAnthropicのオープンプロトコル。Claude Code ↔ MCP Server ↔ 外部システムという構成で、接続したものはすべてClaudeが操作できます。

MCP Serverの設定はsettings.jsonに数行書くだけ。commandとargsで起動コマンドを指定し、envでAPIキーを渡します。公式のFilesystem Serverから試してみるのがおすすめです。

MCPとHooksの違い：Hooksは「Claudeの動き方」を制御（保存時フォーマット、コミット前チェック）。MCPは「Claudeにできること」を拡張（DB照会、外部API呼び出し）。両者は補完関係にあります。

公式のGitHub・PostgreSQL・Slack・ファイルシステム用サーバーに加え、Notion・Linear・Jiraなどコミュニティ実装も豊富。次回はPostgreSQLへの接続と独自MCP Server作成を解説します。
