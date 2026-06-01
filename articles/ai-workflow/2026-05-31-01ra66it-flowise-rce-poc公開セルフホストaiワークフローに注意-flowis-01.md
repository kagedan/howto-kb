---
id: "2026-05-31-01ra66it-flowise-rce-poc公開セルフホストaiワークフローに注意-flowis-01"
title: "@01ra66it: 【Flowise RCE PoC公開、セルフホストAIワークフローに注意】 FlowiseのCVE-2026-4093"
url: "https://x.com/01ra66it/status/2061218085944836109"
source: "x"
category: "ai-workflow"
tags: ["MCP", "API", "LLM", "x"]
date_published: "2026-05-31"
date_collected: "2026-06-01"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

【Flowise RCE PoC公開、セルフホストAIワークフローに注意】

FlowiseのCVE-2026-40933について、技術情報とPoCが公開されました。

この脆弱性は、悪性chatflowのインポートをきっかけに、MCP stdio server設定を通じてサーバー上で任意コマンドが実行され得るものです。

FlowiseはLLMフローやAIエージェントを構築する基盤であり、本番環境ではDB、API、クラウドアカウント、Secretsと接続されていることが多いため、侵害時の影響範囲が大きくなります。

セルフホストFlowiseはバージョン確認、3.1.0以降への更新、インポート機能の制限、保存済み認証情報の棚卸しを優先してください。

#Flowise #CVE202640933 #RCE #AIセキュリティ #MCP #DevSecOps #脆弱性対応

https://t.co/jzF4Mz4Ft8
