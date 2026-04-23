---
id: "2026-04-22-備忘録salesforce-hosted-mcp-server-を使い始める-claude-desk-01"
title: "【備忘録】Salesforce Hosted MCP Server を使い始める ― Claude Desktop から sobject-reads まで繋ぐまでの流れ"
url: "https://qiita.com/Tadataka_Takahashi/items/5fc44899426563c03966"
source: "qiita"
category: "claude-code"
tags: ["MCP", "qiita"]
date_published: "2026-04-22"
date_collected: "2026-04-23"
summary_by: "auto-rss"
---

## はじめに

![fig_intro.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2648069/62bc5fda-176b-4778-be34-f6524a147b3b.png)


Salesforce が提供する **Hosted MCP Server** の初期セットアップ方法について、公式ブログを読みながら自分なりに整理した備忘録です。

MCP（Model Context Protocol）対応のクライアント（Claude / ChatGPT / Cursor など）から、Salesforce のデータや自動化機能に接続できるようになるという機能で、一度 Salesforce 側で設定すれば、複数の AI クライアントから同じサーバーを使い回せる点が特徴だと理解しました。

本記事では、次の順で整理します。

- Hosted MCP Server がどういう位置付けの機能か
- 設定の全体フロー
- 外部クライアントアプリケーションの作り方（OAuth 周りのハマりどころ）
- MC
