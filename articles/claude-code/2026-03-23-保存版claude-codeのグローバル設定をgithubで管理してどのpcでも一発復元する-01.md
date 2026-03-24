---
id: "2026-03-23-保存版claude-codeのグローバル設定をgithubで管理してどのpcでも一発復元する-01"
title: "【保存版】Claude Codeのグローバル設定をGitHubで管理して、どのPCでも一発復元する"
url: "https://qiita.com/LingmuSajun/items/f0756783e36fa3fc142d"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "qiita"]
date_published: "2026-03-23"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

# 【保存版】Claude Codeのグローバル設定をGitHubで管理して、どのPCでも一発復元する

## はじめに

Claude Codeを使い込んでいくと、`~/.claude/` 配下にどんどん設定が溜まっていきます。

- CLAUDE.md（グローバルルール）
- settings.json（権限・MCP設定）
- commands/（カスタムスラッシュコマンド）
- skills/（カスタムスキル）
- plugins/（プラグイン設定）

これらを**PCの入れ替え・クリーンインストール・チームメンバーへの共有**のたびに手動コピーするのは面倒ですし、漏れが発生します。

本記事では、**dotfilesリポジトリ + シンボリックリンク**という定番の手法で、Claude Codeのグローバル設定をGitHub管理し、新しい環境でも **`clone` → `./install.sh` の2ステップで即復元**できる仕組みを構築します。

### この記事で得られるもの

- `~/.claude/` 配下の全ファイルについて「Git管理すべきか否か」の判定基準
