---
id: "2026-04-11-goでclaude-cliを自作した-claude-codeが18-issueを自律実装した記録-01"
title: "GoでClaude CLIを自作した — Claude Codeが18 Issueを自律実装した記録"
url: "https://qiita.com/kai_kou/items/f5220a9aa84e075180ac"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

<!-- IMAGE_SLOT: hero | GoでClaude CLIを自作するイメージ図：ターミナル上でclaude-cliコマンドを実行し、AIの応答がストリーミングされる様子 -->


> **ソースコードは GitHub で公開中です**
> https://github.com/kai-kou/go-claude-code
> `go install github.com/kai-kou/go-claude-code/cmd/claude-cli@latest` で今すぐ使えます。


## はじめに

ターミナルからClaude AIを素早く呼び出せるCLIツールが欲しかった。`curl` でAPIを叩くたびにJSONを手書きするのは非効率で、繰り返し作業になる。シングルバイナリで動き、パイプやファイルと組み合わせられるツールがあれば、日々の作業効率が上がる。

そこでGoを使ったCLIツール **claude-cli** を作成しました。さらに面白いのは、その実装の大部分を **Claude Code** が自律的に行ったという点です。

### この記事で紹介す
