---
id: "2026-04-17-claude-codeのコスト最適化costだけで終わる話じゃないopus-47時代の完全チートシー-01"
title: "Claude Codeのコスト最適化、/costだけで終わる話じゃない。Opus 4.7時代の完全チートシート"
url: "https://qiita.com/moha0918_/items/b004c2f6070ee1c34d85"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "qiita"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

Opus 4.7が来てから、デフォルトのeffort levelが`xhigh`に変わりました。気づかずに使い続けると、Opus 4.6時代より明らかにトークンを食います。設定の組み合わせを棚卸ししたので、リファレンスとして残しておきます。

## まずはコスト把握の4コマンド

何もしないうちは何も最適化できません。最初に覚えるのはこの4つです。

| コマンド | 用途 | 対象ユーザー |
|---|---|---|
| `/cost` | 現セッションのAPIトークン使用量と推定コスト | API課金ユーザー |
| `/stats` | 使用量パターンの確認 | Claude Max/Pro契約者 |
| `/context` | コンテキスト消費の内訳(MCP・CLAUDE.md・履歴) | 全員 |
| `/status` | 現在のモデルとeffort level | 全員 |

:::note info
`/cost`の金額はローカル推定です。正確な請求はClaude Consoleの`Usage`ページで確認してください。Claude MaxやProはサブスク内で完
