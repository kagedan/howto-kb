---
id: "2026-03-22-maestro-mcpとclaudeでandroidアプリのe2eテストを実装してみた-01"
title: "Maestro MCPとClaudeでAndroidアプリのE2Eテストを実装してみた"
url: "https://zenn.dev/banananana/articles/maestro-mcp-android-e2e-test"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "zenn"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

はじめに
こんにちは、しがないモバイルエンジニアです。フリーランスしてます。
モバイルアプリのE2Eテスト、実際にプロジェクトで実行しているところはほぼないと思います。
「やった方がいいのはわかってるけど、ハードルが高い」というのが現実ではないでしょうか。

 モバイルE2Eテストのハードルが高い理由


環境構築が面倒 — エミュレータ/シミュレータのセットアップ、テストフレームワークの導入、CIとの連携...

テストコードの記述コストが高い — Espresso や UI Automator のAPIを覚える必要がある。セレクタの指定が煩雑

メンテナンスが大変 — UIを変更...
