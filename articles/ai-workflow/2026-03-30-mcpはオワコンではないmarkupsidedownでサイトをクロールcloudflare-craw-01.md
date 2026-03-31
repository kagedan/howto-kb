---
id: "2026-03-30-mcpはオワコンではないmarkupsidedownでサイトをクロールcloudflare-craw-01"
title: "MCPはオワコンではない。MarkUpsideDownでサイトをクロール（Cloudflare /crawl endpoint）した話。"
url: "https://zenn.dev/jphfa/articles/markupsidedown-mcp-crawl-events"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "zenn"]
date_published: "2026-03-30"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

Before: curl → ポーリング → JSON取得 → 手動変換 → 保存 → バリデーション（8ステップ）
After:  /crawl-events gewoelbe.ticket.io（1コマンド）
ケルンのクラブのイベントカレンダーを更新するのに8ステップの手作業を踏んでいました。環境変数の管理、curlコマンドの組み立て、ポーリング、JSONの手動変換。やりたいことは「URLを渡してイベントデータを得る」だけなのにインフラの都合に付き合わされていました。
これを1コマンドに変えた話です。使ったのは自作のMarkdownエディタMarkUpsideDownのMCP機能と、...
