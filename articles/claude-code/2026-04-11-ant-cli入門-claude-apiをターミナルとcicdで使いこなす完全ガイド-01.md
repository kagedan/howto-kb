---
id: "2026-04-11-ant-cli入門-claude-apiをターミナルとcicdで使いこなす完全ガイド-01"
title: "ant CLI入門 — Claude APIをターミナルとCI/CDで使いこなす完全ガイド"
url: "https://qiita.com/kai_kou/items/ae85e3ea3e3e4be84e20"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "qiita"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

<!-- IMAGE_SLOT: hero | ant CLIでClaude APIをターミナルから操作するイメージ図 -->

## はじめに

AnthropicはClaude API専用の公式コマンドラインツール **ant CLI** をリリースしました。`curl` でAPIを叩くより大幅に少ないコードで、Claude APIのすべてのリソースをターミナルから操作できます。

### この記事で学べること

- ant CLIのインストールとセットアップ
- Messages APIへのメッセージ送信とレスポンス整形
- エージェント・セッションのCLI操作（beta:リソース）
- `--transform` を使った出力フィルタリング
- YAML定義ファイルによるAPIリソースのGit管理
- Claude Codeとant CLIの連携

### 対象読者

- Claude APIをターミナルやスクリプトから利用したいエンジニア
- Claude Managed Agentsをコマンドラインで管理したい方
- curlを使ったAPI呼び出しをより効率化したい方
