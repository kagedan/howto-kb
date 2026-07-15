---
id: "2026-07-15-hoshino-popopo-amazon-opensearch-serviceがagent-too-01"
title: "@hoshino_popopo_: 📢 Amazon OpenSearch Serviceが、Agent Toolkit for AWSに対応したよ！ K"
url: "https://x.com/hoshino_popopo_/status/2077450366703321130"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "x"]
date_published: "2026-07-15"
date_collected: "2026-07-16"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

📢 Amazon OpenSearch Serviceが、Agent Toolkit for AWSに対応したよ！

Kiro、Claude Code、CursorなどのAIコーディングエージェントから、OpenSearch ServiceのドメインやOpenSearch Serverlessのコレクションを自然言語で構築、管理、検索できるようになったよ！

🤖 AIコーディングエージェントとの連携

今回の連携では、AWS MCP Serverと専用スキル「amazon-opensearch-service」を利用するよ。

自然言語で目的を伝えると、専用スキルが依頼内容を適切な機能へ振り分けて、AWS MCP Serverが必要なAWS APIを呼び出してくれるんだ。

「何を実現したいか」を伝えるところから、実際のAWS操作までつながるのが便利だよね〜

🧩 5つの対応分野

専用スキルは、OpenSearchに関する次の5分野をカバーしているよ。

・移行：セルフマネージドのOpenSearchから、OpenSearch ServiceやOpenSearch Serverlessへの移行
・運用：ドメインやコレクションのプロビジョニングと管理
・検索：ベクトル検索、セマンティック検索、ハイブリッド検索、RAG検索の構築
・ログ分析：PPLとOpenSearch Ingestionを使ったログ分析
・トレース分析：OpenTelemetryを使った分散トレースの調査

構築だけじゃなくて、移行や運用、検索基盤、オブザーバビリティまで扱えるのいいよね

🔎 自然言語による検索基盤の構築

ベクトル検索やセマンティック検索、キーワード検索を組み合わせたハイブリッド検索に加えて、RAG向けの検索も対象だよ。

生成AIアプリの検索基盤をOpenSearchで作りたいときに、Kiroなどのエージェントへ相談しながら作業を進めやすくなりそうだと思うんだ〜

🛠 既存インフラへの変更不要

この連携は、マネージドドメインとOpenSearch Serverlessのコレクションの両方に対応しているよ。

すべてのバージョンで利用できて、既存インフラを変更する必要もないんだって。

🚀 導入方法

使い始めるには、AIコーディングエージェントへ「aws-data-analytics」プラグインをインストールするよ。

このプラグインにはAWS MCP Serverの設定とOpenSearch専用スキルが含まれているから、1回の手順で導入できるんだ〜

💰 料金と対応リージョン

この連携機能に追加料金はかからないよ。

Amazon OpenSearch ServiceとOpenSearch Serverlessが提供されている、すべてのAWSリージョンで利用できるんだ。

OpenSearchの移行や運用、RAG検索の構築、ログやトレースの調査をKiroから進めたい人には、試してみたいアップデートだと思うんだ〜👀

Amazon OpenSearch Service now supports the Agent Toolkit for AWS with a curated skill

https://t.co/IfANNRba18
