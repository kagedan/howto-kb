---
id: "2026-04-02-claude-codeとsnowflake-mcpを使ってdbtモデルのパフォーマンスチューニングを-01"
title: "Claude CodeとSnowflake MCPを使って、dbtモデルのパフォーマンスチューニングを自動化した話"
url: "https://zenn.dev/dely_jp/articles/9962b33ad86bc3"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-04-02"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

はじめに
こんにちは、クラシル社のレシチャレBUのKOHです。データエンジニアをしています。
突然ですが、データエンジニアの業務は幅広いです。


パイプライン構築 — ソースからDWHへのデータ取り込み・変換

データモデリング — スタースキーマ設計、ファクト/ディメンション構築

データ品質 — テスト実装、異常値検知

コスト管理 — Snowflakeクレジットの監視・最適化

BI連携 — Lightdash等へのデータ提供

パフォーマンスチューニング — 遅いクエリの原因特定と改善

この中でもチューニングは、Snowflakeのアーキテクチャや原理原則を知っていない...
