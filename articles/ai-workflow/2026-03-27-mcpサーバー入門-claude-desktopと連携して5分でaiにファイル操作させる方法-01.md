---
id: "2026-03-27-mcpサーバー入門-claude-desktopと連携して5分でaiにファイル操作させる方法-01"
title: "MCPサーバー入門 — Claude Desktopと連携して5分でAIにファイル操作させる方法"
url: "https://qiita.com/NakajimaSH/items/a886675458963b96c89d"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "qiita"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

:::note info
**動作確認環境**
- Claude Desktop：最新版（2025年3月時点）
- Node.js：v18以上（推奨 v20 LTS）
- `@modelcontextprotocol/sdk`：v1.x（2025年3月時点の最新安定版）
- OS：Windows 11 / macOS 14 Sonoma
:::

## 1. はじめに — 「MCPって聞くけど、自分に関係ある？」

「MCP」という言葉、最近よく目にしませんか？

エンジニアのブログ、X（旧Twitter）のタイムライン、AI系のニュースサイト……でも「なんか難しそう」「サーバーって聞くと身構える」と感じて、読み飛ばしてしまっている方も多いのではないでしょうか。

この記事はそんな方に向けて書きました。

**この記事を読み終わったら：** `claude_desktop_config.json` を1箇所書き換えるだけで、AIがあなたのデスクトップのファイルを一覧してくれる体験ができます。設定は10分以内に完了します。

**この記事を読むと分かること：**

- MCPとは何か、
