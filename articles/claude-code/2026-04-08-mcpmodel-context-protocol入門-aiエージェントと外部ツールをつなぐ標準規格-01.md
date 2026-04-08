---
id: "2026-04-08-mcpmodel-context-protocol入門-aiエージェントと外部ツールをつなぐ標準規格-01"
title: "MCP（Model Context Protocol）入門 — AIエージェントと外部ツールをつなぐ標準規格"
url: "https://qiita.com/76Hata/items/6ce2cde9826f5c3a1de2"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-04-08"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

## MCPとは何か

MCP（Model Context Protocol）は、Anthropicが開発した**AIツールと外部データソースを接続するためのオープンプロトコル**です。

AIエージェントがSlack、Google Drive、PostgreSQL、Jiraなどの外部サービスにアクセスする際、サービスごとに個別のアダプターを書く必要がありました。MCPはこの問題を解決する「共通規格」として設計されています。

よく使われるたとえで言えば、**USB-C**のようなものです。USB-Cがさまざまなデバイスを1つのコネクタで統一したように、MCPはAIと外部ツールの接続を1つのプロトコルで標準化します。

## MCPのアーキテクチャ

MCPは**クライアント-サーバーモデル**を採用しています。

```mermaid
graph LR
    A[AIエージェント<br/>例: Claude Code] --> B[MCP Client]
    B -->|プロトコル通信| C[MCP Server A<br/>例: Slack]
    B -->|プロトコル通
