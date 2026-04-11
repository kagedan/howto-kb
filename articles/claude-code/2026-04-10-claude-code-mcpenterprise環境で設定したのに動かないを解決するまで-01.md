---
id: "2026-04-10-claude-code-mcpenterprise環境で設定したのに動かないを解決するまで-01"
title: "Claude Code × MCP、Enterprise環境で設定したのに動かないを解決するまで"
url: "https://qiita.com/namic/items/391a84760012e4112baf"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

## はじめに

Claude CodeのEnterprise/Team環境でMCPサーバーを設定したにもかかわらず、エラーも出ずに無視される現象に遭遇しました。個人アカウントでは同じ設定で動作するため、Enterprise環境固有の制御が原因でした。

本記事では、この現象の原因であるClaude Codeの設定ファイル体系とEnterprise固有の組織制御の仕組みを整理し、Amazon Bedrock経由でClaude Codeを利用することで組織制御の課題を解決した方法を説明します。Enterprise/Team環境でClaude CodeのMCP連携に苦労している方や、組織管理者としてClaude Codeの制御設計を検討している方の参考になれば幸いです。

---

## Enterprise環境でMCP設定が無視される現象

Claude CodeでMCPサーバーを使うには、`.mcp.json`に設定を書くのが基本です。公式ドキュメント通りに記述し、`claude mcp list`で確認、接続テストもOKという状態でした。

しかしEnterprise環境のClaud
