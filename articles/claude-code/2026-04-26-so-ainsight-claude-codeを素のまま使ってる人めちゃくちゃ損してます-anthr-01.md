---
id: "2026-04-26-so-ainsight-claude-codeを素のまま使ってる人めちゃくちゃ損してます-anthr-01"
title: "@so_ainsight: Claude Codeを素のまま使ってる人、めちゃくちゃ損してます。 Anthropic公式のプラグインに「claud"
url: "https://x.com/so_ainsight/status/2048386675332804982"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "x"]
date_published: "2026-04-26"
date_collected: "2026-04-28"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

Claude Codeを素のまま使ってる人、めちゃくちゃ損してます。

Anthropic公式のプラグインに「claude-code-setup」っていうのがあって、リポジトリをスキャンして必要な設定を全部教えてくれます。

・有効化すべきhooks
・入れるべきskills
・自分のスタックに合うMCPサーバー
・立ち上げるべきsubagents
・1つずつの設定手順

しかも0円。

どう動くのか、詳しく解説します👇

インストールはこのコマンド1つ。

/plugin install claude-code-setup@claude-plugins-official

これを叩くだけで、ベテランエンジニアがリポジトリをレビューするように、環境構築の方針を一気に提案してくれます。

このプラグインがすごいのは、自分のプロジェクトを丸ごと読んでから提案してくれるところ。

・どんなファイル構成か
・どの言語・フレームワークを使っているか
・既存の設定はどうなっているか

その上で「あなたのスタックならこれを入れるべき」と教えてくれます。

出てくるアウトプットがこれ。

・どのhooksを設定するか
・どのskillsをインストールするか
・どのMCPサーバーが合うか
・どのsubagentsを立ち上げるか

しかも各項目に「ステップごとの設定手順」がついてくるので、コピペするだけで使える状態になります。

特におすすめしたいのがこういう人。

・Claude Codeを入れて何から始めるか迷っている人
・設定が面倒で素のまま使っている人
・新しいプロジェクトに入って環境を整えたい人
・チーム共通の設定を作りたい人

「何を入れればいいか分からない」を一発で解消してくれます。

詳しくはこちら👇
https://t.co/vltqmgM7oK
