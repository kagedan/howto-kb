---
id: "2026-03-24-claude-code-を使ってみた個人開発で感じた-ai-コーディングの進化-01"
title: "Claude Code を使ってみた：個人開発で感じた AI コーディングの進化"
url: "https://qiita.com/threebottoles/items/3a537c30b1aaffecd033"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-24"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

# はじめに

最近、開発体験を大きく変えてくれたツールに出会いました。
Anthropic が提供する AI コーディングツール **Claude Code** です。

個人開発（Next.js + MicroCMS のブログ）でがっつり使い始めてから、「これは別物だ」と感じる場面が何度もありました。

本記事では、

- Claude Code の概要
- 使い始めたきっかけ
- 1 年前に触った Cline との比較
- 実際に使って感じたこと

を書いていきます。

# Claude Code とは

Claude Code は、Anthropic が提供する **CLI ベースの AI コーディングアシスタント**です。
ターミナルから起動し、会話形式でコードの作成・編集・レビュー・リファクタリングなどを依頼できます。

主な特徴は以下の通りです。

- **コードベースを丸ごと理解する**：プロジェクト全体のファイルを読み込み、文脈を把握した上で作業する
- **ファイルの読み書きを自律的に行う**：指示するだけで、必要なファイルを自分で開いて編集してくれる
- **CL
