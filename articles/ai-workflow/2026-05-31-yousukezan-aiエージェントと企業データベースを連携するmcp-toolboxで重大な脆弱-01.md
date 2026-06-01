---
id: "2026-05-31-yousukezan-aiエージェントと企業データベースを連携するmcp-toolboxで重大な脆弱-01"
title: "@yousukezan: AIエージェントと企業データベースを連携するMCP Toolboxで、重大な脆弱性CVE-2026-9739が発見された"
url: "https://x.com/yousukezan/status/2061065365732692091"
source: "x"
category: "ai-workflow"
tags: ["MCP", "x"]
date_published: "2026-05-31"
date_collected: "2026-06-01"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

AIエージェントと企業データベースを連携するMCP Toolboxで、重大な脆弱性CVE-2026-9739が発見された。CVSSスコアは9.4で、悪意のあるWebサイトから企業データへの不正アクセスを許す恐れがある。

問題はServer-Sent Events（SSE）機能の実装にあり、開発時に残されたハードコード済みのCORS許可設定が原因だ。本来のアクセス制御設定を無効化し、外部サイトからローカルのMCP Toolboxへ接続できる状態になっていた。

この脆弱性を悪用されると、攻撃者は正規ユーザーになりすましてツールを実行したり、MCP Toolboxをプロキシとして利用したりできる。その結果、PostgresやBigQueryなど接続されたデータベースから情報を窃取される可能性がある。主に旧プロトコル仕様「v2024-11-05」を利用する環境が影響を受ける。

対策としては、問題のハードコードされたヘッダーを削除し、管理者が設定したCORSポリシーを正しく適用することが推奨されている。CVE-2026-9739のCVSSスコアは9.4である。
https://t.co/WI8GJ9C9Rs
