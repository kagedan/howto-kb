---
id: "2026-03-19-claude-in-chrome-をローカル開発で使う-01"
title: "Claude in Chrome をローカル開発で使う"
url: "https://zenn.dev/yuyu_496/articles/c250d4037d3325"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-19"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

記事概要
Claude in Chrome拡張機能とClaude Code CLIを組み合わせてコードのフィードバックループを回す方法と、localのみのアクセス制限などセキュアな設定手順をまとめています。
対象読者
Claude Codeを使ってWeb開発をしていて、AI出力コードの質向上とテスト・デバッグの効率化に興味がある方を対象としています。


 1. サイトアクセスをlocalのみに絞る
Claudeがアクセスできるサイトを localhost だけに制限します。

 手順

Chromeのツールバーで拡張機能アイコンを右クリック
「拡張機能を管理」→「サイトへのアクセス」
...
