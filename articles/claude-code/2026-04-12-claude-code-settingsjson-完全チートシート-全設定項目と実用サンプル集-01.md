---
id: "2026-04-12-claude-code-settingsjson-完全チートシート-全設定項目と実用サンプル集-01"
title: "Claude Code settings.json 完全チートシート — 全設定項目と実用サンプル集"
url: "https://qiita.com/moha0918_/items/ef10d0e9beec96a4aee4"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

Claude Codeは `settings.json` 1つで動作を細かく制御できる。しかし設定項目が多すぎて「どこに何を書けばいい？」と迷う人は多い。この記事ではスコープの選び方から各設定項目の実用サンプルまでを一枚のリファレンスとしてまとめた。

## 設定スコープ早見表

「どのファイルに書くか」がClaude Codeの設定でいちばん最初に理解すべきポイントだ。

| スコープ | ファイルパス | 有効範囲 | Gitで共有 |
|:---|:---|:---|:---|
| **Managed** | MDM/レジストリ or `managed-settings.json` | マシン全ユーザー | IT管理者が配布 |
| **User** | `~/.claude/settings.json` | 自分のすべてのプロジェクト | されない |
| **Project** | `.claude/settings.json` | そのリポジトリの全員 | **される** |
| **Local** | `.claude/settings.local.json` | 自分・
