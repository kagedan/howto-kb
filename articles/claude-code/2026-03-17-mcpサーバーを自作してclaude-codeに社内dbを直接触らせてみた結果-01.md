---
id: "2026-03-17-mcpサーバーを自作してclaude-codeに社内dbを直接触らせてみた結果-01"
title: "MCPサーバーを自作して、Claude Codeに社内DBを直接触らせてみた結果"
url: "https://qiita.com/miruky/items/ea9c7e6d882502cbbf7c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "Python", "qiita"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

## はじめに

こんばんは、mirukyです。

今回は、**MCP（Model Context Protocol）サーバーをPythonで自作**して、Claude Codeから自然言語で社内データベースを検索・分析できる環境を構築してみました。

「売上トップの社員を教えて」と入力するだけで、Claude CodeがSQLを自動生成→実行→結果を要約してくれます。MCPサーバーの自作は難しそうに聞こえますが、実際にやってみると **Pythonコード約90行** で完成しました。本記事では、構築手順から実行結果までをまとめています。

## MCPとは？ ― AIの「USB-C」ってよく言われますよね

**MCP（Model Context Protocol）** は、AIアプリと外部ツールを繋ぐオープン標準プロトコルです。

```
従来:  AIアプリ ←→ 個別API実装 ←→ 各ツール（N×M問題）
MCP:   AIアプリ ←→ MCP ←→ 各ツール（N+M で解決）
```

（よく聞く例えですが）USB-Cが充電ケーブルを統一したように、MCPはAIと外部システ
