---
id: "2026-04-21-mastra-で作る-aiエージェント27-mastra-platform-で-workspace-01"
title: "Mastra で作る AIエージェント(27) Mastra Platform で Workspace 機能を動かす"
url: "https://zenn.dev/shiromizuj/articles/b7692eb3e87c80"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

Mastra で作る AI エージェント というシリーズの第27回です。

第25回では Mastra Platform にプロジェクトをデプロイするところまで試しました。第26回では会話履歴や RAG のストレージを LibSQL / DuckDB から外部の PostgreSQL サービス（Neon）に切り替えました。
今回は、第15回 で取り上げた「Mastra Workspaces」機能を Mastra Platform 上で動かすことに挑戦します。Workspace 機能のおさらいも兼ねて、サンドボックス（コード実行）と ワークスペース検索（Grep / BM25 / Vect...
