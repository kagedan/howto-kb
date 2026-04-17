---
id: "2026-04-16-claudemdが200行超えたら読む記事claude-code拡張6種の使い分け-01"
title: "CLAUDE.mdが200行超えたら読む記事、Claude Code拡張6種の使い分け"
url: "https://qiita.com/moha0918_/items/b55226af0c21c4b7780c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "AI-agent", "qiita"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

Claude Codeのカスタマイズ手段、意外と多いです。CLAUDE.md、Skills、Hooks、MCP、Subagents、Plugins。6種類ある。

とりあえず全部CLAUDE.mdに書いていませんか。公式ドキュメントによると、200行を超えると指示の遵守率が下がります。適材適所に振り分けるだけで、レスポンスの質が変わる。

## 6種の早見表

| 機能 | やること | コンテキストコスト | 使い所 |
|---|---|---|---|
| **CLAUDE.md** | 毎セッション読まれるルール | **高い**（毎リクエスト全文） | 「常にこうしろ」系の短い指示 |
| **Skills** | 必要時に読み込まれる知識・手順書 | 低い（呼ぶまでは説明文だけ） | 参照ドキュメント、ワークフロー |
| **MCP** | 外部サービス接続 | 低い（Tool Searchで遅延読み込み） | DB、Slack、ブラウザ操作 |
| **Subagents** | 隔離コンテキストで動く別働隊 | ゼロ（メインと完全に独立） | 重い調査、並列作業 |
