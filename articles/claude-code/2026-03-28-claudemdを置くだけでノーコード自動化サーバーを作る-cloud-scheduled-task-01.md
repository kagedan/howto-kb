---
id: "2026-03-28-claudemdを置くだけでノーコード自動化サーバーを作る-cloud-scheduled-task-01"
title: "CLAUDE.mdを置くだけでノーコード自動化サーバーを作る — Cloud Scheduled Tasksのハック的活用法"
url: "https://qiita.com/milkmaccya2/items/cdc48d29ed5345a2377d"
source: "qiita"
category: "claude-code"
tags: ["CLAUDE-md", "qiita"]
date_published: "2026-03-28"
date_collected: "2026-03-30"
summary_by: "auto-rss"
---

## はじめに

GitHubリポジトリにソースコードは1行もありません。あるのは `CLAUDE.md` という「自然言語の指示書」が1ファイルだけ。

たったこれだけで、**「6時間ごとにNotionの未要約メモを検出し、内容を読んで300字以内で要約を書き込む」** という定期バッチ処理がAnthropicのクラウド上で動き続けています。

```text
notion-summary-task/
└── CLAUDE.md   ← これだけ（自然言語の指示が書かれている）
```

今回使ったのは、2026年2月にリリースされた **Cloud Scheduled Tasks** という機能です（Pro/Max/Team/Enterpriseで利用可能）。

https://code.claude.com/docs/en/web-scheduled-tasks

本来はリポジトリのコードに対して「依存関係をアップデートする」「テストを回す」といった開発ワークフローを定期実行するための機能です。しかし、**コードを一切置かず、CLAUDE.mdという指示書だけのリポジトリでMC
