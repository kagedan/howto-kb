---
id: "2026-04-17-claude-code-スラッシュコマンドの-model-指定が-compact-を誤発火させる落と-01"
title: "Claude Code: スラッシュコマンドの `model` 指定が /compact を誤発火させる落とし穴"
url: "https://zenn.dev/genda_jp/articles/9228f64c472e98"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-17"
date_collected: "2026-04-18"
summary_by: "auto-rss"
query: ""
---

はじめに
AIでの並列開発用に、「マージ済み worktree を削除してデフォルトブランチを最新に同期するだけ」の小さなスラッシュコマンドを用意していました。処理自体は数秒で終わる bash なので、軽量モデルで十分だろうとフロントマターに model: haiku を書いていました。
ところが、長時間動かしている Opus 4.7 (1M) セッションからこのコマンドを呼ぶと、毎回のように /compact プロンプトが出るという現象に遭遇しました。Opus 基準ではコンテキストはまだ十分余っているはずです。
原因はフロントマターの model: haiku その 1 行でした。...
