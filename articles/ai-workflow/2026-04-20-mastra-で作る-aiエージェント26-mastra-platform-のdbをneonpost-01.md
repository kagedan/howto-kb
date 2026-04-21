---
id: "2026-04-20-mastra-で作る-aiエージェント26-mastra-platform-のdbをneonpost-01"
title: "Mastra で作る AIエージェント(26) Mastra Platform のDBをNeon（PostgreSQL）に切り替える"
url: "https://zenn.dev/shiromizuj/articles/3ed824b8d97648"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

Mastra で作る AI エージェント というシリーズの第26回です。

前回は、Mastra Platform にプロジェクトをデプロイするところまで試しました。エージェントも動き、Studio も使えるようになり、一通りのことはできています。
しかしここで一つ問題があります。今の構成では、各種ストレージに LibSQL（SQLite）と DuckDB のローカルファイルを使っています。これはローカル開発には便利なのですが、本番環境で使い続けると以下の 2 つの問題が生じます。


デプロイするたびにデータが初期化される — Mastra Platform はエフェメラルなファイルシ...
