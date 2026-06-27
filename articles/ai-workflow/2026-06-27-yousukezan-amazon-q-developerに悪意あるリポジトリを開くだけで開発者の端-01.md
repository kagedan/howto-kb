---
id: "2026-06-27-yousukezan-amazon-q-developerに悪意あるリポジトリを開くだけで開発者の端-01"
title: "@yousukezan: Amazon Q Developerに、悪意あるリポジトリを開くだけで開発者の端末上で任意コードを実行し、AWS認証情報"
url: "https://x.com/yousukezan/status/2070798127121215562"
source: "x"
category: "ai-workflow"
tags: ["MCP", "API", "x"]
date_published: "2026-06-27"
date_collected: "2026-06-28"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

Amazon Q Developerに、悪意あるリポジトリを開くだけで開発者の端末上で任意コードを実行し、AWS認証情報を盗める脆弱性が見つかった。CVE-2026-12957とCVE-2026-12958として公開され、Amazonは修正を配布した。

問題は、Amazon QがModel Context Protocol（MCP）サーバー設定を扱う処理にあった。ワークスペース内の.amazonq/mcp.jsonを読み込み、利用者への確認や信頼性の検証なしに、そこに定義されたローカルプロセスを起動していた。

MCPサーバーはAPIやデータベース、ローカル資源と連携するための仕組みだが、起動されたプロセスは開発者の環境変数を引き継ぐ。そのため、AWSアクセスキー、セッショントークン、APIキー、SSHエージェントソケットなどにアクセスできる可能性があった。

Wizは、悪意ある設定ファイル内のBashコマンドでAWSの認証情報を確認し、攻撃者のサーバーへ送信できることを実証した。攻撃者は細工したリポジトリをcloneさせ、Amazon Qが有効なIDEで開かせるだけでよい。

Amazonは5月12日に初期修正を配布し、6月26日に公表した。修正版はLanguage Servers for AWS 1.69.0以降、VS Code版2.20以降などで提供される。
https://t.co/Xcr6gCDeHD
