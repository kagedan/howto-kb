---
id: "2026-03-26-claude-code-で複数行プロンプトを快適に入力する-terminal-setup-コマンド-01"
title: "Claude Code で複数行プロンプトを快適に入力する `/terminal-setup` コマンド"
url: "https://qiita.com/tacker530i/items/72ed6ad1438f29dbe2ba"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

Claude Code を使い始めて最初に戸惑うのが「**Enter を押すと即座に送信されてしまい、複数行の指示が書けない**」という問題です。

通常のチャットツール（Slack や Discord など）では Enter が改行、Shift+Enter が送信という操作が一般的ですが、Claude Code はターミナルツールであるため、**Enter がそのまま実行**になっています。(できればShift+Enterに統一してほしい...)

この記事では、公式が用意している `/terminal-setup` コマンドを使った改行設定の方法と、環境別の対処法をまとめます。

## 動作環境

| 項目 | 内容 |
|---|---|
| ツール | Claude Code（最新版） |
| 対応ターミナル | VS Code、iTerm2、WezTerm、Ghostty、Kitty、Alacritty、Zed、Warp 他 |

---

## 問題：Enter を押すと即送信されてしまう

Claude Code のインタラクティブモードでは、Enter キーの動作は「*
