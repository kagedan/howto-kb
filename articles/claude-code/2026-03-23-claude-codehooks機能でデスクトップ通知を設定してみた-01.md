---
id: "2026-03-23-claude-codehooks機能でデスクトップ通知を設定してみた-01"
title: "【Claude Code】Hooks機能でデスクトップ通知を設定してみた"
url: "https://qiita.com/pro-tein/items/49e5dbec705c3497dd51"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "qiita"]
date_published: "2026-03-23"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

# はじめに
※今回はMacOS環境での例を紹介します。
Claude Codeを使用していると、以下のようなケースで**気づいたら処理が止まっている**といったことがあると思います。
・（ファイルの操作権限が必要であれば）ファイル操作のために必要な権限付与の許可待ち
・（質問であれば）質問の回答待ちもしくは深堀りのための逆質問
・（タスクを依頼していたら）タスク完了時
こまめに処理が止まっていないかを確認するのも大変です。
そこで、今回はClaude Codeの**Hooks**機能を使用して、上記のようなケースにデスクトップ通知させる設定方法を紹介します。



# Hooksとは
簡潔にまとめると、「Claude Codeセッション中の**特定のポイント**に、カスタム処理を差し込める仕組み」です。
まずは、これらの公式ドキュメントを読むことをおすすめします。

https://code.claude.com/docs/ja/hooks

https://code.claude.com/docs/ja/hooks-guide#prompt-based-hooks


たくさんの
