---
id: "2026-04-04-aiエージェント-zeroclaw-のmcp設定-01"
title: "AIエージェント ZeroClaw のMCP設定"
url: "https://zenn.dev/mizugeeks/articles/30d0878e44a233"
source: "zenn"
category: "antigravity"
tags: ["MCP", "antigravity", "zenn"]
date_published: "2026-04-04"
date_collected: "2026-04-05"
summary_by: "auto-rss"
---

はじめに
OpenClaw系のAIエージェント「ZeroClaw」を利用し始めたのですがセキュリティ制限が厳しく、コマンドの実行にかなり制限があります。特定のコマンド実行を許可しても、コマンドが作成するテンポラリファイルの場所も制限対象になるので使えないことがほとんどです。
そこでMCPを使おうとしたのですが ZeroClawに関する情報が非常に乏しく、検索しても具体的な方法が出てきません。
ZeroClawのソースを Google Antigravity に読み込ませ解析させ、試行錯誤してようやくMCPを利用することができるようになったので、メモとして残しておきます。

 利用環境...
